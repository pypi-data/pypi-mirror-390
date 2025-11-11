from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

from codemie_tools.base.models import CodeMieToolConfig, CredentialTypes, RequiredField


class AzureDevOpsWorkItemConfig(CodeMieToolConfig):
    """Configuration for Azure DevOps Work Item integration."""
    credential_type: CredentialTypes = Field(default=CredentialTypes.AZURE_DEVOPS, exclude=True, frozen=True)

    organization_url: str = RequiredField(
        description="Azure DevOps organization URL",
        json_schema_extra={
            "placeholder": "https://dev.azure.com/your-organization",
            "help": "https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/create-organization"
        }
    )

    project: str = RequiredField(
        description="Azure DevOps project name",
        json_schema_extra={"placeholder": "MyProject"}
    )

    token: str = RequiredField(
        description="Personal Access Token (PAT) for authentication",
        json_schema_extra={
            "placeholder": "your_personal_access_token",
            "sensitive": True,
            "help": "https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate"
        }
    )

    limit: Optional[int] = Field(
        default=5,
        description="Default number of items to return in queries"
    )


# Input models for Azure DevOps work item operations
class SearchWorkItemsInput(BaseModel):
    query: str = Field(description="WIQL query for searching Azure DevOps work items")
    limit: Optional[int] = Field(
        description="Number of items to return. IMPORTANT: Tool returns all items if limit=-1. "
                    "If parameter is not provided then the value will be taken from tool configuration.",
        default=None
    )
    fields: Optional[List[str]] = Field(description="List of requested fields", default=None)


class CreateWorkItemInput(BaseModel):
    work_item_json: str = Field(description="""JSON of the work item fields to create in Azure DevOps, i.e.
                    {
                       "fields":{
                          "System.Title":"Implement Registration Form Validation",
                          "field2":"Value 2",
                       }
                    }
                    """)
    wi_type: Optional[str] = Field(
        description="Work item type, e.g. 'Task', 'Issue' or 'EPIC'",
        default="Task"
    )


class UpdateWorkItemInput(BaseModel):
    id: int = Field(description="ID of work item required to be updated")
    work_item_json: str = Field(description="""JSON of the work item fields to update in Azure DevOps, i.e.
                    {
                       "fields":{
                          "System.Title":"Updated Title",
                          "field2":"Updated Value",
                       }
                    }
                    """)


class GetWorkItemInput(BaseModel):
    id: int = Field(description="The work item id")
    fields: Optional[List[str]] = Field(description="List of requested fields", default=None)
    as_of: Optional[str] = Field(description="AsOf UTC date time string", default=None)
    expand: Optional[str] = Field(
        description="The expand parameters for work item attributes. "
                    "Possible options are { None, Relations, Fields, Links, All }.",
        default=None
    )


class LinkWorkItemsInput(BaseModel):
    source_id: int = Field(description="ID of the work item you plan to add link to")
    target_id: int = Field(description="ID of the work item linked to source one")
    link_type: str = Field(description="Link type: System.LinkTypes.Dependency-forward, etc.")
    attributes: Optional[Dict[str, Any]] = Field(
        description="Dict with attributes used for work items linking. "
                    "Example: `comment`, etc. and syntax 'comment': 'Some linking comment'",
        default=None
    )


class GetRelationTypesInput(BaseModel):
    pass


class GetCommentsInput(BaseModel):
    work_item_id: int = Field(description="The work item id")
    limit_total: Optional[int] = Field(description="Max number of total comments to return", default=None)
    include_deleted: Optional[bool] = Field(description="Specify if the deleted comments should be retrieved",
                                            default=False)
    expand: Optional[str] = Field(
        description="The expand parameters for comments. "
                    "Possible options are { all, none, reactions, renderedText, renderedTextOnly }.",
        default="none"
    )
    order: Optional[str] = Field(
        description="Order in which the comments should be returned. Possible options are { asc, desc }",
        default=None
    )
