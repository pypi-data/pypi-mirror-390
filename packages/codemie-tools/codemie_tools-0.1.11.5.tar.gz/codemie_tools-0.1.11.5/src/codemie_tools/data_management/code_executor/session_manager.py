"""
Sandbox session manager for maintaining persistent code execution sessions.

This module provides the SandboxSessionManager singleton that manages
a pool of reusable sandbox sessions with automatic health checking and
intelligent pod discovery.
"""

import logging
import random
import threading
from typing import Dict, List, Optional

from langchain_core.tools import ToolException
from llm_sandbox import SandboxSession, SandboxBackend, ArtifactSandboxSession
from llm_sandbox.exceptions import SandboxTimeoutError
from llm_sandbox.security import SecurityPolicy
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log, retry_if_exception_type

from codemie_tools.data_management.code_executor.models import CodeExecutorConfig

logger = logging.getLogger(__name__)


class SandboxSessionManager:
    """
    Singleton manager for maintaining persistent sandbox sessions.

    Manages a pool of reusable sessions mapped to pod names, providing
    thread-safe access and automatic session lifecycle management.

    Attributes:
        _sessions: Dictionary mapping pod names to active sandbox sessions
        _session_locks: Per-pod locks for thread-safe session access
        _config: Configuration for sandbox execution
        _initialized: Flag indicating whether the singleton has been initialized
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config: CodeExecutorConfig):
        """Implement thread-safe singleton pattern with double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: CodeExecutorConfig):
        """
        Initialize session storage and per-pod locks.

        Args:
            config: Configuration for sandbox execution. If not provided, loads from environment.
        """
        if self._initialized:
            return

        self._config = config
        self._sessions: Dict[str, SandboxSession] = {}
        self._session_locks: Dict[str, threading.Lock] = {}
        self._available_pods: List[str] = []
        self._k8s_client_instance = None
        self._initialized = True

    def _get_or_create_lock(self, pod_name: str) -> threading.Lock:
        """
        Get or create a lock for the specified pod.

        Args:
            pod_name: Name of the pod

        Returns:
            threading.Lock: Lock for the pod
        """
        if pod_name not in self._session_locks:
            self._session_locks[pod_name] = threading.Lock()
        return self._session_locks[pod_name]

    @property
    def _k8s_client(self):
        """
        Lazily initialize and return the Kubernetes client.

        Loads Kubernetes configuration with the following priority:
        1. config.kubeconfig_path: Path to a specific kubeconfig file (from config)
        2. Otherwise: Uses load_incluster_config() for in-cluster deployment

        Returns:
            kubernetes.client.CoreV1Api: Kubernetes API client
        """
        if self._k8s_client_instance is None:
            from kubernetes import client, config

            if self._config.kubeconfig_path:
                logger.debug(f"Loading Kubernetes config from: {self._config.kubeconfig_path}")
                config.load_kube_config(config_file=self._config.kubeconfig_path)
            else:
                logger.debug("Loading Kubernetes config for in-cluster environment.")
                config.load_incluster_config()

            self._k8s_client_instance = client.CoreV1Api()

        return self._k8s_client_instance

    def _check_pod_exists(self, pod_name: str) -> bool:
        """
        Check if a pod exists and is in Running state in Kubernetes.

        Args:
            pod_name: Name of the pod to check

        Returns:
            bool: True if pod exists and is running, False otherwise
        """
        try:
            pod = self._k8s_client.read_namespaced_pod(
                name=pod_name,
                namespace=self._config.namespace
            )
            is_running = pod.status.phase == "Running"
            if is_running:
                logger.debug(f"Pod {pod_name} exists and is running")
            else:
                logger.debug(f"Pod {pod_name} exists but not running (phase: {pod.status.phase})")
            return is_running
        except Exception as e:
            logger.debug(f"Pod {pod_name} does not exist or cannot be accessed: {e}")
            return False

    def _list_available_pods(self) -> List[str]:
        """
        List all running pods in the namespace that match the pod name prefix.

        Returns:
            List[str]: Names of available running pods
        """
        try:
            pods = self._k8s_client.list_namespaced_pod(
                namespace=self._config.namespace,
                label_selector="app=codemie-executor"
            )

            available = []
            for pod in pods.items:
                if pod.status.phase == "Running":
                    available.append(pod.metadata.name)

            logger.debug(f"Found {len(available)} running pods in namespace {self._config.namespace}")
            return available

        except Exception as e:
            logger.warning(f"Failed to list pods: {e}")
            return []

    def _get_available_pod_name(self) -> Optional[str]:
        """
        Get an available pod name, randomly selecting from existing running pods.

        Strategy:
        1. List all running pods with app=codemie-executor label
        2. If running pods exist, randomly select one for reuse (load distribution)
        3. If no pods exist and under max limit, generate new pod name
        4. Return None if at max capacity

        Returns:
            str: Available pod name, or None if at capacity
        """
        # Refresh list of available pods from Kubernetes
        running_pods = self._list_available_pods()

        # Randomly select from existing running pods for better load distribution
        if running_pods:
            pod_name = random.choice(running_pods)  # NOSONAR
            logger.debug(f"Randomly selected pod: {pod_name} from {len(running_pods)} available pod(s)")
            return pod_name

        # No running pods, check if we can create a new one
        if len(running_pods) < self._config.max_pod_pool_size:
            # Generate unique pod name based on current count
            new_pod_name = f"{self._config.pod_name_prefix}{len(running_pods) + 1}"
            logger.debug(
                f"Will create new pod: {new_pod_name} "
                f"(current: {len(running_pods)}, max: {self._config.max_pod_pool_size})"
            )
            return new_pod_name

        # At capacity, return None
        logger.warning(f"Pod pool at maximum capacity ({self._config.max_pod_pool_size})")
        return None

    def get_session(
            self,
            pod_name: str,
            workdir: str,
            pod_manifest: dict,
            security_policy: SecurityPolicy
    ):
        """
        Get or create a persistent session for the specified pod.

        This method provides thread-safe session acquisition with per-pod locking
        and automatic health checking to ensure session validity.

        Args:
            pod_name: Name of the pod to connect to
            workdir: Working directory for the session
            pod_manifest: Pod manifest for creating new pods
            security_policy: Security policy for code validation

        Returns:
            SandboxSession: Active session for the pod

        Raises:
            ToolException: If session creation fails
        """
        lock = self._get_or_create_lock(pod_name)
        with lock:
            if pod_name in self._sessions and self._is_session_healthy(pod_name):
                logger.debug(f"Reusing existing session for pod: {pod_name}")
                return self._sessions[pod_name]

            # Create new session
            logger.debug(f"Creating new session for pod: {pod_name}")
            session = self._create_session(pod_name, workdir, pod_manifest, security_policy)
            self._sessions[pod_name] = session
            return session

    def _is_session_healthy(self, pod_name: str) -> bool:
        """
        Check if an existing session is still healthy and responsive.

        Args:
            pod_name: Name of the pod to check

        Returns:
            bool: True if session is healthy, False otherwise
        """
        session = self._sessions[pod_name]
        try:
            # Test if session is still alive with a simple command
            session.run("print('health_check')")
            return True
        except SandboxTimeoutError:
            logger.warning(f"Session for {pod_name} expired, will recreate")
            self._close_session(pod_name)
            return False
        except Exception as e:
            logger.warning(f"Existing session for {pod_name} is dead, will recreate: {e}")
            self._close_session(pod_name)
            return False

    def _create_session(
            self,
            pod_name: str,
            workdir: str,
            pod_manifest: dict,
            security_policy: SecurityPolicy
    ):
        """
        Create a new sandbox session by connecting to existing pod or creating new one.

        Optimization: Checks if pod exists using Kubernetes API before attempting connection.
        This avoids expensive pod creation operations when pods already exist.

        Args:
            pod_name: Name of the pod
            workdir: Working directory
            pod_manifest: Pod manifest for new pod creation
            security_policy: Security policy for code validation

        Returns:
            SandboxSession: Newly created session

        Raises:
            ToolException: If session creation fails
        """
        # Check if pod already exists and is running
        pod_exists = self._check_pod_exists(pod_name)

        if pod_exists:
            # Connect to existing pod with retry logic
            try:
                session = self._connect_to_existing_pod_with_retry(pod_name, workdir, security_policy)
                logger.debug(f"✓ Connected to existing pod: {pod_name}")
                return session
            except Exception as connect_error:
                # Enhanced error logging with exception type
                error_type = type(connect_error).__name__
                logger.warning(
                    f"Failed to connect to existing pod {pod_name} after retries: {error_type}: {connect_error}",
                    exc_info=True
                )
                # Fall through to create new pod

        # Pod doesn't exist or connection failed, create it
        logger.debug(f"Creating new pod: {pod_name}")
        return self._create_new_pod(pod_name, workdir, pod_manifest, security_policy)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _connect_to_existing_pod_with_retry(
            self,
            pod_name: str,
            workdir: str,
            security_policy: SecurityPolicy
    ):
        """
        Connect to an existing Kubernetes pod with retry logic.

        This method uses exponential backoff retry strategy:
        - Max attempts: 3
        - Wait strategy: 1s, 2s, 4s between attempts
        - Retries on any Exception

        Args:
            pod_name: Name of the existing pod
            workdir: Working directory
            security_policy: Security policy for code validation

        Returns:
            SandboxSession: Connected session

        Raises:
            Exception: If all connection attempts fail (re-raised from last attempt)
        """
        try:
            logger.debug(f"Attempting connection to pod {pod_name}")
            session = self._connect_to_existing_pod(pod_name, workdir, security_policy)
            logger.debug(f"✓ Successfully connected to pod {pod_name}")
            return session
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.warning(
                f"Connection attempt failed for pod {pod_name}: {error_type}: {error_msg}"
            )
            raise

    def _connect_to_existing_pod(
            self,
            pod_name: str,
            workdir: str,
            security_policy: SecurityPolicy
    ):
        """
        Connect to an existing pod without creating a new one.

        Args:
            pod_name: Name of the existing pod
            workdir: Working directory
            security_policy: Security policy for code validation

        Returns:
            SandboxSession: Connected session

        Raises:
            Exception: If connection fails
        """
        try:
            session_config = self._build_session_config(
                client=self._k8s_client,
                workdir=workdir,
                security_policy=security_policy,
                container_id=pod_name
            )
            logger.debug(f"Creating session for existing pod {pod_name} with config: {session_config.keys()}")
            session = ArtifactSandboxSession(**session_config)

            logger.debug(f"Opening session to existing pod {pod_name}")
            session.open()

            logger.debug(f"Session opened successfully for pod {pod_name}")

            # Validate container name was set during session.open()
            container_name = getattr(session._session, 'container_name', None)
            if not container_name:
                raise ToolException(
                    f"Container name not set after opening session for pod {pod_name}. "
                    "This may indicate the pod has no containers or the connection failed."
                )
            logger.debug(f"Validated container name: '{container_name}' for pod {pod_name}")

            # Health check: verify pod is responsive
            logger.debug(f"Running health check for pod {pod_name}")
            self._health_check_session(session, pod_name)

            return session
        except ToolException:
            # Re-raise ToolException as-is
            raise
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(
                f"Failed to connect to existing pod {pod_name}: {error_type}: {error_msg}",
                exc_info=True
            )
            raise ToolException(f"Connection to pod {pod_name} failed: {error_type}: {error_msg}") from e

    def _create_new_pod(
            self,
            pod_name: str,
            workdir: str,
            pod_manifest: dict,
            security_policy: SecurityPolicy
    ):
        """
        Create a new pod with the specified configuration.

        Args:
            pod_name: Name for the new pod
            workdir: Working directory
            pod_manifest: Pod manifest configuration
            security_policy: Security policy for code validation

        Returns:
            SandboxSession: Session for the newly created pod

        Raises:
            Exception: If pod creation fails
        """
        session_config = self._build_session_config(
            client=self._k8s_client,
            workdir=workdir,
            security_policy=security_policy,
            pod_manifest=pod_manifest,
            keep_template=self._config.keep_template,
            default_timeout=self._config.default_timeout
        )

        threshold_name = security_policy.severity_threshold.name if security_policy else "UNRESTRICTED"
        logger.debug(f"Security policy applied: {threshold_name} threshold")

        session = ArtifactSandboxSession(**session_config)
        session.open()
        logger.debug(f"✓ New pod created: {pod_name}")
        return session

    def _health_check_session(self, session, pod_name: str) -> None:
        """
        Perform health check on newly created session to ensure it's responsive.

        Args:
            session: The sandbox session to check
            pod_name: Name of the pod being checked

        Raises:
            ToolException: If health check fails
        """
        try:
            # Try to run a simple echo command
            result = session.run("print('health_check_ok')")

            # Verify we got expected output
            if result.exit_code != 0:
                raise ToolException(
                    f"Health check failed with exit code {result.exit_code}. "
                    f"Stderr: {result.stderr}"
                )

            if 'health_check_ok' not in result.stdout:
                raise ToolException(
                    f"Health check returned unexpected output. "
                    f"Expected 'health_check_ok' in stdout, got: {result.stdout}"
                )

            logger.debug(f"✓ Health check passed for pod {pod_name}")

        except ToolException:
            # Re-raise ToolException as-is
            raise
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(
                f"Health check failed for pod {pod_name}: {error_type}: {error_msg}",
                exc_info=True
            )
            raise ToolException(
                f"Pod {pod_name} is not responsive: {error_type}: {error_msg}"
            ) from e

    def _build_session_config(
            self,
            workdir: str,
            security_policy: SecurityPolicy,
            **kwargs
    ) -> dict:
        """
        Build session configuration with common parameters.

        Args:
            workdir: Working directory
            security_policy: Security policy for code validation
            **kwargs: Additional configuration parameters

        Returns:
            dict: Session configuration
        """
        config = {
            "backend": SandboxBackend.KUBERNETES,
            "lang": "python",
            "kube_namespace": self._config.namespace,
            "verbose": self._config.verbose,
            "workdir": workdir,
            "execution_timeout": self._config.execution_timeout,
            "session_timeout": self._config.session_timeout,
            "security_policy": security_policy,
            "skip_environment_setup": self._config.skip_environment_setup
        }
        config.update(kwargs)
        return config

    def _close_session(self, pod_name: str):
        """Close and remove a session from the pool."""
        if pod_name in self._sessions:
            try:
                self._sessions[pod_name].close()
            except Exception as e:
                logger.warning(f"Error closing session for {pod_name}: {e}")
            finally:
                del self._sessions[pod_name]

    def close_all(self):
        """Close all managed sessions. Useful for cleanup."""
        for pod_name in list(self._sessions.keys()):
            self._close_session(pod_name)
        logger.info("All sessions closed")
