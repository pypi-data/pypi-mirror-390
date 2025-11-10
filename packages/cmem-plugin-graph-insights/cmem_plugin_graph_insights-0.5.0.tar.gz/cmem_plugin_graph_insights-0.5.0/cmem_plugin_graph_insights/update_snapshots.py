"""Update snapshots workflow task"""

from collections.abc import Sequence

import requests
from cmem.cmempy.config import get_cmem_base_uri
from cmem_plugin_base.dataintegration.context import (
    ExecutionContext,
    ExecutionReport,
    PluginContext,
)
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginAction, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.parameter.graph import GraphParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs
from requests import HTTPError, Response


@Plugin(
    label="Update Graph Insights Snapshots",
    plugin_id="cmem_plugin_graph_insights-Update",
    icon=Icon(package=__package__, file_name="update_snapshots.svg"),
    description="Update one or more snapshots, optionally selected by affected graph.",
    documentation="""This workflow task updates [Graph Insights](https://go.eccenca.com/feature/explore-graph-exploration-graph-insights?lang=en&origin=cmem-plugin-graph-insights)
    snapshots for a specified graph in your system.

## Behavior

- **No graph selected**: All snapshots in the system are updated
- **Graph selected**: Only snapshots associated with the selected graph are updated

## Usage

1. Add this task to your workflow.
2. Optionally select a specific graph to limit which snapshots are updated.
3. Use the "Preview Snapshots" action to see which snapshots will be affected before execution.
4. Run the workflow to update the snapshots.

## Prerequisites

- Graph Insights must be active in your system
- User must have permissions to access Graph Insights
- The plugin will skip execution with a warning if these conditions are not met
    """,
    actions=[
        PluginAction(
            name="preview_snapshots",
            label="Preview Snapshots",
            description="Previews snapshots for graph insights in a workflow.",
        ),
    ],
    parameters=[
        PluginParameter(
            name="selected_graph",
            label="Selected Graph",
            description="Selected graph to update snapshots for. "
            "Leave empty for updating all snapshots.",
            param_type=GraphParameterType(
                show_di_graphs=True,
                show_graphs_without_class=True,
                show_system_graphs=True,
                allow_only_autocompleted_values=False,
            ),
            default_value="",
        ),
        PluginParameter(
            name="timeout",
            label="Timeout",
            description="Timeout in seconds for Graph Insights API.",
            advanced=True,
            default_value=100,
        ),
    ],
)
class UpdateSnapshots(WorkflowPlugin):
    """Workflow plugin for graph insights snapshot updates"""

    def __init__(self, selected_graph: str, timeout: float) -> None:
        """Initialize the plugin with graph selection and timeout settings"""
        self.selected_graph = selected_graph
        self.base_url = get_cmem_base_uri()
        self.input_ports = FixedNumberOfInputs([])
        self.output_ports = None
        self.timeout = timeout

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> None:
        """Execute the snapshot update workflow for selected or all graphs"""
        _ = inputs

        if not self.check_status(context):
            return
        if self.selected_graph == "":
            self.update_all_snapshots(context)
        else:
            self.update_associated_snapshots(context)

    def update_all_snapshots(self, context: ExecutionContext) -> None:
        """Update all available snapshots in the system"""
        snapshot_ids = self.get_all_snapshots_ids(context=context)
        headers = {"Authorization": f"Bearer {context.user.token()!s}"}
        for snapshot_id in snapshot_ids:
            requests.put(
                url=self.base_url + f"/dataplatform/api/ext/semspect/snapshot/{snapshot_id}",
                headers=headers,
                timeout=self.timeout,
            )
            context.report.update(
                ExecutionReport(entity_count=len(snapshot_ids), operation_desc="snapshots updated")
            )

    def get_all_snapshots_ids(self, context: ExecutionContext) -> list[int]:
        """Retrieve database IDs for all available snapshots"""
        response = self.get_all_snapshots(context)
        return [snapshot_id["databaseId"] for snapshot_id in response.json()]

    def update_associated_snapshots(self, context: ExecutionContext) -> None:
        """Update only snapshots associated with the selected graph"""
        headers = {"Authorization": f"Bearer {context.user.token()!s}"}
        response = self.get_all_snapshots(context)
        snapshot_counter = 0
        for result in response.json():
            if self.selected_graph in result["allGraphsSynced"]:
                snapshot_counter += 1
                snapshot_id = result["databaseId"]
                requests.put(
                    url=self.base_url + f"/dataplatform/api/ext/semspect/snapshot/{snapshot_id}",
                    headers=headers,
                    timeout=self.timeout,
                )
                context.report.update(
                    ExecutionReport(
                        entity_count=snapshot_counter,
                        operation_desc="snapshot updated",
                    )
                )

    def get_all_snapshots(self, context: ExecutionContext | PluginContext) -> Response:
        """Fetch all snapshots from the Graph Insights API"""
        headers = {"Authorization": f"Bearer {context.user.token()!s}"}
        return requests.get(
            url=self.base_url + "/dataplatform/api/ext/semspect/snapshot/status",
            headers=headers,
            timeout=self.timeout,
        )

    def preview_snapshots(self, context: PluginContext) -> str:
        """Generate a table preview of snapshots that will be affected"""
        answer = ""

        response = self.get_all_snapshots(context=context)

        filtered_response = []

        if self.selected_graph != "":
            for result in response.json():
                if self.selected_graph in result["allGraphsSynced"]:
                    filtered_response.append(result)  # noqa: PERF401
        else:
            filtered_response = response.json()

        answer += "| ID | Main Graph | Updated | Status | Valid |\n"
        answer += "| --- | --- | --- | --- | --- |\n"

        for result in filtered_response:
            link_url = f"{self.base_url}/default/explore?graph={result['mainGraphSynced']}"
            answer += (
                f"| {result['databaseId']} | "
                f"[{result['mainGraphSynced']}]({link_url}) | "
                f"{result['updateInfoTimestamp']} | "
                f"{result['status']} | "
                f"{result['isValid']} |\n"
            )

        return answer

    def check_status(self, context: ExecutionContext) -> bool:
        """Verify that Graph Insights is active and user is authorized"""
        try:
            headers = {"Authorization": f"Bearer {context.user.token()!s}"}
            response = requests.get(
                self.base_url + "/dataplatform/api/ext/semspect", timeout=10, headers=headers
            )
            response.raise_for_status()
            data: dict[str, bool] = response.json()
            if not data["isActive"]:
                context.report.update(
                    ExecutionReport(
                        warnings=["Graph insights is not active."],
                        summary=[("isActive", str(data["isActive"]))],
                    )
                )
                return False
            if not data["isUserAllowed"]:
                context.report.update(
                    ExecutionReport(
                        warnings=["User is not allowed to use graph insights."],
                        summary=[("isUserAllowed", str(data["isUserAllowed"]))],
                    )
                )
                return False

            return True  # noqa: TRY300

        except HTTPError as e:
            raise HTTPError(f"HTTP error: {e}") from e
