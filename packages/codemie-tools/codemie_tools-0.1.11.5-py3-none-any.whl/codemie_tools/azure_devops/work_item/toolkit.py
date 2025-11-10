from typing import Dict, Any, List

from codemie_tools.azure_devops.work_item.models import AzureDevOpsWorkItemConfig
from codemie_tools.azure_devops.work_item.tools import (
    SearchWorkItemsTool,
    CreateWorkItemTool,
    UpdateWorkItemTool,
    GetWorkItemTool,
    LinkWorkItemsTool,
    GetRelationTypesTool,
    GetCommentsTool
)
from codemie_tools.azure_devops.work_item.tools_vars import (
    SEARCH_WORK_ITEMS_TOOL,
    CREATE_WORK_ITEM_TOOL,
    UPDATE_WORK_ITEM_TOOL,
    GET_WORK_ITEM_TOOL,
    LINK_WORK_ITEMS_TOOL,
    GET_RELATION_TYPES_TOOL,
    GET_COMMENTS_TOOL
)
from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool


class AzureDevOpsWorkItemToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.AZURE_DEVOPS_WORK_ITEM
    tools: List[Tool] = [
        Tool.from_metadata(SEARCH_WORK_ITEMS_TOOL),
        Tool.from_metadata(CREATE_WORK_ITEM_TOOL),
        Tool.from_metadata(UPDATE_WORK_ITEM_TOOL),
        Tool.from_metadata(GET_WORK_ITEM_TOOL),
        Tool.from_metadata(LINK_WORK_ITEMS_TOOL),
        Tool.from_metadata(GET_RELATION_TYPES_TOOL),
        Tool.from_metadata(GET_COMMENTS_TOOL),
    ]


class AzureDevOpsWorkItemToolkit(BaseToolkit):
    ado_config: AzureDevOpsWorkItemConfig

    @classmethod
    def get_tools_ui_info(cls):
        return ToolKit(
            toolkit=ToolSet.AZURE_DEVOPS_WORK_ITEM,
            tools=[
                Tool.from_metadata(SEARCH_WORK_ITEMS_TOOL),
                Tool.from_metadata(CREATE_WORK_ITEM_TOOL),
                Tool.from_metadata(UPDATE_WORK_ITEM_TOOL),
                Tool.from_metadata(GET_WORK_ITEM_TOOL),
                Tool.from_metadata(LINK_WORK_ITEMS_TOOL),
                Tool.from_metadata(GET_RELATION_TYPES_TOOL),
                Tool.from_metadata(GET_COMMENTS_TOOL),
            ],
            settings_config=True
        ).model_dump()

    def get_tools(self) -> list:
        tools = [
            SearchWorkItemsTool(config=self.ado_config),
            CreateWorkItemTool(config=self.ado_config),
            UpdateWorkItemTool(config=self.ado_config),
            GetWorkItemTool(config=self.ado_config),
            LinkWorkItemsTool(config=self.ado_config),
            GetRelationTypesTool(config=self.ado_config),
            GetCommentsTool(config=self.ado_config)
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        ado_config = AzureDevOpsWorkItemConfig(**configs)
        return AzureDevOpsWorkItemToolkit(ado_config=ado_config)
