from typing import Optional

from pydantic import BaseModel, Field

from codemie_tools.base.models import CodeMieToolConfig, CredentialTypes, RequiredField

# Constants for repeated field descriptions
WIKI_IDENTIFIER_DESCRIPTION = "Wiki ID or wiki name"


class AzureDevOpsWikiConfig(CodeMieToolConfig):
    """Configuration for Azure DevOps Wiki integration."""
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


# Input models for Azure DevOps wiki operations
class GetWikiInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)


class GetPageByPathInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    page_name: str = Field(description="Wiki page path")


class GetPageByIdInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    page_id: int = Field(description="Wiki page ID")


class ModifyPageInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    page_name: str = Field(description="Wiki page name")
    page_content: str = Field(description="Wiki page content")
    version_identifier: str = Field(
        description="Version string identifier (name of tag/branch, SHA1 of commit)"
    )
    version_type: Optional[str] = Field(
        description="Version type (branch, tag, or commit). Determines how Id is interpreted",
        default="branch",
    )


class RenamePageInput(BaseModel):
    wiki_identified: str = Field(description=WIKI_IDENTIFIER_DESCRIPTION)
    old_page_name: str = Field(
        description="Old Wiki page name to be renamed", examples=["/TestPageName"]
    )
    new_page_name: str = Field(description="New Wiki page name", examples=["/RenamedName"])
    version_identifier: str = Field(
        description="Version string identifier (name of tag/branch, SHA1 of commit)"
    )
    version_type: Optional[str] = Field(
        description="Version type (branch, tag, or commit). Determines how Id is interpreted",
        default="branch",
    )
