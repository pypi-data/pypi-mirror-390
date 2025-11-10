from codemie_tools.base.models import ToolMetadata
from .models import AzureDevOpsGitConfig

AZURE_DEVOPS_GIT_TOOL = ToolMetadata(
    name="azure_devops_git",
    description="""
        Advanced Azure DevOps Git REST API client tool that provides comprehensive access to Azure DevOps Git repositories.
        
        IMPORTANT: Azure DevOps Structure
        - Organization: Top-level container (e.g., "EPMC-EASE")
        - Project: Container for repositories, pipelines, etc. (e.g., "DefaultProject", "MyTeam")
        - Repository: Git repository within a project (e.g., "git-version-experiments")
        
        HOW TO FIND PROJECT NAME:
        1. First, list all projects in the organization:
           {"query": {"method": "GET", "url": "/_apis/projects", "method_arguments": {}}}
           Note: This uses /_apis/projects (not /_apis/git/)
        
        2. Then list repositories in a specific project:
           {"query": {"method": "GET", "url": "/_apis/git/repositories", "method_arguments": {"project": "ProjectName"}}}
        
        3. Or list ALL repositories across all projects (no project parameter):
           {"query": {"method": "GET", "url": "/_apis/git/repositories", "method_arguments": {}}}
           This will show repository.project.name for each repository
        
        INPUT FORMAT:
        The tool accepts a `query` parameter containing a JSON with the following structure:
        {"query":
            {
                "method": "GET|POST|PUT|DELETE|PATCH",
                "url": "/_apis/git/...",
                "method_arguments": {object with request data},
                "custom_headers": {optional dictionary of additional HTTP headers}
            }
        }
        
        REQUIREMENTS:
        - `method`: HTTP method (GET, POST, PUT, DELETE, PATCH)
        - `url`: Must start with "/_apis/git/" for Git operations (Azure DevOps Git API endpoint - relative path)
        - `method_arguments`: Object containing request parameters or body data
        - `custom_headers`: Optional dictionary for additional headers (authorization headers are protected)
        - The entire query must be valid JSON that passes json.loads() validation
        
        PROJECT PARAMETER:
        - For most Git operations, you need to specify the PROJECT name (not repository name!)
        - Project can be specified in method_arguments: {"project": "ProjectName", ...}
        - If unsure about project name, first list all repositories without project parameter
        
        API VERSION:
        - Azure DevOps REST API uses api-version parameter, defaults to configured version (7.1-preview.1)
        - For specific API version requirements, include it in the method_arguments: {"api-version": "7.0"}
        
        FEATURES:
        - Automatic request parameter handling (GET uses query params, others use request body)
        - Built-in authentication using configured Azure DevOps Personal Access Token
        - Custom header support for specialized API calls
        - Structured response with full context for AI agent processing
        - Comprehensive error handling and validation
        - URL placeholder replacement (e.g., {repositoryId} from method_arguments)
        - Project can be specified in method_arguments to override default
        
        RESPONSE FORMAT:
        Returns an AzureDevOpsGitOutput object containing:
        {
            "success": true/false,           # Whether request was successful
            "status_code": 200,               # HTTP status code
            "method": "GET",                  # HTTP method used
            "url": "https://...",             # Full URL that was called
            "data": {...} or [...] or "...",  # Response body (JSON object/array or text)
            "error": null or "error message"  # Error message if failed
        }
        
        This structured format provides complete visibility into the HTTP transaction for AI agent analysis.
        
        SECURITY:
        - Authorization headers are automatically managed and cannot be overridden via custom_headers
        - Personal Access Token (PAT) is securely transmitted via Basic Authentication header
             
        EXAMPLES:
        
        Find the right project for your repository:
        {"query": {"method": "GET", "url": "/_apis/git/repositories", "method_arguments": {}}}
        Then look for your repository name and note its "project": {"name": "..."} field
        
        List repositories in a specific project:
        {"query": {"method": "GET", "url": "/_apis/git/repositories", "method_arguments": {"project": "ProjectName"}}}
        Response: {"success": true, "status_code": 200, "method": "GET", "url": "https://dev.azure.com/org/_apis/git/repositories", "data": {"value": [...]}, "error": null}
        
        2. Get a specific repository (with placeholder):
        {"query": {"method": "GET", "url": "/_apis/git/repositories/{repositoryId}", "method_arguments": {"repositoryId": "repo-guid"}}}
        Response: {"success": true, "status_code": 200, "method": "GET", "url": "https://dev.azure.com/org/_apis/git/repositories/123", "data": {...}, "error": null}
        
        3. Create a repository:
        {"query": 
            {
                "method": "POST", 
                "url": "/_apis/git/repositories", 
                "method_arguments": {
                    "name": "NewRepo",
                    "project": {"id": "ProjectId"}
                }
            }
        }
        Response: {"success": true, "status_code": 201, "method": "POST", "url": "https://dev.azure.com/org/_apis/git/repositories", "data": {...}, "error": null}
        
        4. Get repository branches:
        {"query": {"method": "GET", "url": "/_apis/git/repositories/{repositoryId}/refs", "method_arguments": {"filter": "heads/"}}}
        
        5. Get commit details:
        {"query": {"method": "GET", "url": "/_apis/git/repositories/{repositoryId}/commits/{commitId}", "method_arguments": {}}}
        
        6. Get file content (with custom headers):
        {"query":
            {
                "method": "GET", 
                "url": "/_apis/git/repositories/{repositoryId}/items", 
                "method_arguments": {
                    "repositoryId": "repo-id",
                    "path": "/path/to/file.txt",
                    "scopePath": "/",
                    "recursionLevel": "none",
                    "includeContentMetadata": "true",
                    "latestProcessedChange": "true"
                },
                "custom_headers": {"Accept": "application/octet-stream"}
            }
        }
        
        7. Create a pull request:
        {"query":
            {
                "method": "POST",
                "url": "/_apis/git/repositories/{repositoryId}/pullrequests",
                "method_arguments": {
                    "repositoryId": "repo-id",
                    "sourceRefName": "refs/heads/feature-branch",
                    "targetRefName": "refs/heads/main",
                    "title": "Feature implementation",
                    "description": "Adding new feature X",
                    "reviewers": [
                        {
                            "id": "user-guid"
                        }
                    ]
                }
            }
        }
        
        8. Example of error response:
        {"query": {"method": "GET", "url": "/_apis/git/repositories/invalid-id", "method_arguments": {}}}
        Response: {"success": false, "status_code": 404, "method": "GET", "url": "https://dev.azure.com/org/_apis/git/repositories/invalid-id", "data": {"message": "Repository not found"}, "error": "HTTP 404: Not Found - Repository not found"}
        """,
    label="Azure DevOps Git",
    user_description="""
        Provides comprehensive access to the Azure DevOps Git REST API with structured response formatting for optimal AI agent processing. This tool enables the AI assistant to perform any Azure DevOps Git operation available through the REST API.
        
        Key Capabilities:
        - Repository management (create, read, update, delete)
        - Branch and ref operations
        - Commit history and details
        - Pull request creation and management
        - File content retrieval and manipulation
        - Tag management
        - Policy configuration
        - Import repository operations
        - Structured response with full HTTP context
        
        Setup Requirements:
        1. Azure DevOps Organization URL (e.g., https://dev.azure.com/organization)
        2. Azure DevOps Personal Access Token with Git permissions
        
        Response Features:
        - Structured response object with success/failure indication
        - Complete HTTP transaction details including status codes
        - Full response body content (JSON or text)
        - Error messages for failed requests
        - Automatic handling of different request types (GET vs POST/PUT/DELETE)
        
        The tool returns a structured response object that includes:
        - success: boolean indicating if the request succeeded
        - status_code: HTTP status code for understanding the result
        - method: HTTP method used for the request
        - url: Full URL that was called
        - data: The actual response data from Azure DevOps
        - error: Error message if the request failed
        
        This structured format ensures the AI agent has full context about each API operation, making it easier to understand results and handle errors appropriately.
        
        Use this tool when you need direct access to Azure DevOps Git repositories that may not be covered by other specialized Azure DevOps tools.
        """.strip(),
    settings_config=True,
    config_class=AzureDevOpsGitConfig
)