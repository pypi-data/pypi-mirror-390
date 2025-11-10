from typing import Dict, Any, List

from codemie_tools.azure_devops.wiki.models import AzureDevOpsWikiConfig
from codemie_tools.azure_devops.wiki.tools import (
    GetWikiTool,
    GetWikiPageByPathTool,
    GetWikiPageByIdTool,
    DeletePageByPathTool,
    DeletePageByIdTool,
    ModifyWikiPageTool,
    RenameWikiPageTool
)
from codemie_tools.azure_devops.wiki.tools_vars import (
    GET_WIKI_TOOL,
    GET_WIKI_PAGE_BY_PATH_TOOL,
    GET_WIKI_PAGE_BY_ID_TOOL,
    DELETE_PAGE_BY_PATH_TOOL,
    DELETE_PAGE_BY_ID_TOOL,
    MODIFY_WIKI_PAGE_TOOL,
    RENAME_WIKI_PAGE_TOOL
)
from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool


class AzureDevOpsWikiToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.AZURE_DEVOPS_WIKI
    tools: List[Tool] = [
        Tool.from_metadata(GET_WIKI_TOOL),
        Tool.from_metadata(GET_WIKI_PAGE_BY_PATH_TOOL),
        Tool.from_metadata(GET_WIKI_PAGE_BY_ID_TOOL),
        Tool.from_metadata(DELETE_PAGE_BY_PATH_TOOL),
        Tool.from_metadata(DELETE_PAGE_BY_ID_TOOL),
        Tool.from_metadata(MODIFY_WIKI_PAGE_TOOL),
        Tool.from_metadata(RENAME_WIKI_PAGE_TOOL),
    ]


class AzureDevOpsWikiToolkit(BaseToolkit):
    ado_config: AzureDevOpsWikiConfig

    @classmethod
    def get_tools_ui_info(cls):
        return ToolKit(
            toolkit=ToolSet.AZURE_DEVOPS_WIKI,
            tools=[
                Tool.from_metadata(GET_WIKI_TOOL),
                Tool.from_metadata(GET_WIKI_PAGE_BY_PATH_TOOL),
                Tool.from_metadata(GET_WIKI_PAGE_BY_ID_TOOL),
                Tool.from_metadata(DELETE_PAGE_BY_PATH_TOOL),
                Tool.from_metadata(DELETE_PAGE_BY_ID_TOOL),
                Tool.from_metadata(MODIFY_WIKI_PAGE_TOOL),
                Tool.from_metadata(RENAME_WIKI_PAGE_TOOL),
            ],
            settings_config=True
        ).model_dump()

    def get_tools(self) -> list:
        tools = [
            GetWikiTool(config=self.ado_config),
            GetWikiPageByPathTool(config=self.ado_config),
            GetWikiPageByIdTool(config=self.ado_config),
            DeletePageByPathTool(config=self.ado_config),
            DeletePageByIdTool(config=self.ado_config),
            ModifyWikiPageTool(config=self.ado_config),
            RenameWikiPageTool(config=self.ado_config)
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        ado_config = AzureDevOpsWikiConfig(**configs)
        return AzureDevOpsWikiToolkit(ado_config=ado_config)
