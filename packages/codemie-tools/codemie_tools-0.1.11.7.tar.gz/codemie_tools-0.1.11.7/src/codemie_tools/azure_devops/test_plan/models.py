from typing import Optional

from pydantic import BaseModel, Field

from codemie_tools.base.models import CodeMieToolConfig, CredentialTypes, RequiredField

# Constants for repeated field descriptions
PROJECT_DESCRIPTION = "Project ID or project name"


class AzureDevOpsTestPlanConfig(CodeMieToolConfig):
    """Configuration for Azure DevOps Test Plan integration."""
    credential_type: CredentialTypes = Field(default=CredentialTypes.AZURE_DEVOPS, exclude=True, frozen=True)

    organization_url: str = RequiredField(
        description="Azure DevOps organization URL",
        json_schema_extra={
            "placeholder": "https://dev.azure.com/your-organization",
            "help": "https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/create-organization",
        },
    )

    project: str = RequiredField(
        description="Azure DevOps project name", json_schema_extra={"placeholder": "MyProject"}
    )

    token: str = RequiredField(
        description="Personal Access Token (PAT) for authentication",
        json_schema_extra={
            "placeholder": "your_personal_access_token",
            "sensitive": True,
            "help": "https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate",
        },
    )

    limit: Optional[int] = Field(
        default=5, description="Default number of items to return in queries"
    )


# Input models for Azure DevOps test plan operations
class CreateTestPlanInput(BaseModel):
    test_plan_create_params: str = Field(description="JSON of the test plan create parameters")
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)


class DeleteTestPlanInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan to be deleted")
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)


class GetTestPlanInput(BaseModel):
    plan_id: Optional[int] = Field(description="ID of the test plan to get", default=None)
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)


class CreateTestSuiteInput(BaseModel):
    test_suite_create_params: str = Field(description="JSON of the test suite create parameters")
    plan_id: int = Field(description="ID of the test plan that contains the suites")
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)


class DeleteTestSuiteInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan that contains the suite")
    suite_id: int = Field(description="ID of the test suite to delete")
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)


class GetTestSuiteInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan that contains the suites")
    suite_id: Optional[int] = Field(description="ID of the suite to get", default=None)
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)


class AddTestCaseInput(BaseModel):
    suite_test_case_create_update_parameters: str = Field(
        description='JSON array of the suite test case create update parameters. Example: "[{"work_item":{"id":"23"}}]"'
    )
    plan_id: int = Field(description="ID of the test plan to which test cases are to be added")
    suite_id: int = Field(description="ID of the test suite to which test cases are to be added")
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)


class GetTestCaseInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan for which test cases are requested")
    suite_id: int = Field(description="ID of the test suite for which test cases are requested")
    test_case_id: str = Field(description="Test Case Id to be fetched")
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)


class GetTestCasesInput(BaseModel):
    plan_id: int = Field(description="ID of the test plan for which test cases are requested")
    suite_id: int = Field(description="ID of the test suite for which test cases are requested")
    project: Optional[str] = Field(description=PROJECT_DESCRIPTION, default=None)
