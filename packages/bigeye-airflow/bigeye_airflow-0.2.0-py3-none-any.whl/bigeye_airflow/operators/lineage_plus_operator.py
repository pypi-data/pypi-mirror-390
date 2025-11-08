from typing import Optional, Dict

from bigeye_sdk.client.datawatch_client import DatawatchClient
from bigeye_sdk.controller.lineage_controller import LineageController
from bigeye_sdk.model.lineage_facade import LineageColumnOverride

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator


class BigeyeLineagePlusOperator(ClientExtensibleOperator):
    """
    The BigeyeLineagePlusOperator takes fully qualified table names and creates/updates lineage in Bigeye.
    """

    def __init__(self,
                 fully_qualified_upstream_table: str,
                 fully_qualified_downstream_table: str,
                 column_overrides: Optional[Dict[str, str]] = {},
                 task_name: Optional[str] = None,
                 container_name: Optional[str] = "Airflow",
                 infer_lineage: Optional[bool] = True,
                 purge_lineage: Optional[bool] = False,
                 connection_id: Optional[str] = "bigeye_conn",
                 workspace_id: Optional[int] = None,
                 *args,
                 **kwargs):
        """
        param connection_id: string referencing a defined connection in the Airflow deployment, Default bigeye_conn.
        param fully_qualified_upstream_table: string of the fully qualified upstream table name as can be searched in Bigeye.
        param fully_qualified_downstream_table: string of the fully qualified downstream table name as can be searched in Bigeye.
        param column_overrides: mapping of upstream column names to downstream column names.
        param task_name: Optional name of the task responsible for moving data between upstream and downstream tables.
        Defaults to the associated dag_id.
        param container_name: Optional name of the container responsible for moving data between upstream and downstream tables.
        Defaults to 'Airflow'.
        param infer_lineage: Boolean used to determine how matching should be performed. When true, the operator will
        establish column level lineage based on columns with the same names in the upstream and downstream sources.
        When false, column_overrides must be provided. Defaults to True.
        param purge_lineage: Boolean used to determine if lineage should be created or deleted. When true, the operator
        will delete all associated relationships. Defaults to False.
        param workspace_id: Optional[int] id of the workspace to establish lineage.
        param args: not currently supported
        param kwargs: not currently supported
        """

        super(BigeyeLineagePlusOperator, self).__init__(*args, **kwargs)

        self.connection_id = connection_id
        self.workspace_id = workspace_id
        self.client = None
        self.upstream_table = fully_qualified_upstream_table
        self.downstream_table = fully_qualified_downstream_table
        self.column_overrides = column_overrides
        self.task_name = task_name
        self.container_name = container_name
        self.infer_lineage = infer_lineage
        self.purge_lineage = purge_lineage

    def get_client(self) -> DatawatchClient:
        if not self.client:
            self.client = AirflowDatawatchClient(
                connection_id=self.connection_id,
                workspace_id=self.workspace_id
            )
        return self.client

    def execute(self, context):
        overrides = None
        controller = LineageController(self.get_client())

        if self.column_overrides:
            overrides = [
                LineageColumnOverride(
                    upstream_column_name=upstream,
                    downstream_column_name=downstream
                )
                for upstream, downstream
                in self.column_overrides.items()
            ]

        if not self.task_name:
            self.task_name = context["dag"].dag_id

        controller.create_edges_from_table_names(
            upstream_table_name=self.upstream_table,
            downstream_table_name=self.downstream_table,
            etl_task_name=self.task_name,
            etl_task_container=self.container_name,
            column_overrides=overrides,
            infer_lineage=self.infer_lineage,
            purge_lineage=self.purge_lineage
        )

