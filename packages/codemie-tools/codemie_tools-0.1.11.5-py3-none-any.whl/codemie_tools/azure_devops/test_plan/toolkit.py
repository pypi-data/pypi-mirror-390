from typing import Dict, Any, List

from codemie_tools.azure_devops.test_plan.models import AzureDevOpsTestPlanConfig
from codemie_tools.azure_devops.test_plan.tools import (
    CreateTestPlanTool,
    DeleteTestPlanTool,
    GetTestPlanTool,
    CreateTestSuiteTool,
    DeleteTestSuiteTool,
    GetTestSuiteTool,
    AddTestCaseTool,
    GetTestCaseTool,
    GetTestCasesTool
)
from codemie_tools.azure_devops.test_plan.tools_vars import (
    CREATE_TEST_PLAN_TOOL,
    DELETE_TEST_PLAN_TOOL,
    GET_TEST_PLAN_TOOL,
    CREATE_TEST_SUITE_TOOL,
    DELETE_TEST_SUITE_TOOL,
    GET_TEST_SUITE_TOOL,
    ADD_TEST_CASE_TOOL,
    GET_TEST_CASE_TOOL,
    GET_TEST_CASES_TOOL
)
from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool


class AzureDevOpsTestPlanToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.AZURE_DEVOPS_TEST_PLAN
    tools: List[Tool] = [
        Tool.from_metadata(CREATE_TEST_PLAN_TOOL),
        Tool.from_metadata(DELETE_TEST_PLAN_TOOL),
        Tool.from_metadata(GET_TEST_PLAN_TOOL),
        Tool.from_metadata(CREATE_TEST_SUITE_TOOL),
        Tool.from_metadata(DELETE_TEST_SUITE_TOOL),
        Tool.from_metadata(GET_TEST_SUITE_TOOL),
        Tool.from_metadata(ADD_TEST_CASE_TOOL),
        Tool.from_metadata(GET_TEST_CASE_TOOL),
        Tool.from_metadata(GET_TEST_CASES_TOOL),
    ]


class AzureDevOpsTestPlanToolkit(BaseToolkit):
    ado_config: AzureDevOpsTestPlanConfig

    @classmethod
    def get_tools_ui_info(cls):
        return ToolKit(
            toolkit=ToolSet.AZURE_DEVOPS_TEST_PLAN,
            tools=[
                Tool.from_metadata(CREATE_TEST_PLAN_TOOL),
                Tool.from_metadata(DELETE_TEST_PLAN_TOOL),
                Tool.from_metadata(GET_TEST_PLAN_TOOL),
                Tool.from_metadata(CREATE_TEST_SUITE_TOOL),
                Tool.from_metadata(DELETE_TEST_SUITE_TOOL),
                Tool.from_metadata(GET_TEST_SUITE_TOOL),
                Tool.from_metadata(ADD_TEST_CASE_TOOL),
                Tool.from_metadata(GET_TEST_CASE_TOOL),
                Tool.from_metadata(GET_TEST_CASES_TOOL),
            ],
            settings_config=True
        ).model_dump()

    def get_tools(self) -> list:
        tools = [
            CreateTestPlanTool(config=self.ado_config),
            DeleteTestPlanTool(config=self.ado_config),
            GetTestPlanTool(config=self.ado_config),
            CreateTestSuiteTool(config=self.ado_config),
            DeleteTestSuiteTool(config=self.ado_config),
            GetTestSuiteTool(config=self.ado_config),
            AddTestCaseTool(config=self.ado_config),
            GetTestCaseTool(config=self.ado_config),
            GetTestCasesTool(config=self.ado_config)
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        ado_config = AzureDevOpsTestPlanConfig(**configs)
        return AzureDevOpsTestPlanToolkit(ado_config=ado_config)
