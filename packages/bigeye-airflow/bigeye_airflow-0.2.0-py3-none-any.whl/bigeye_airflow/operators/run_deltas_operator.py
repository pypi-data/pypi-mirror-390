from typing import List, Optional

from bigeye_sdk.client.datawatch_client import DatawatchClient
from bigeye_sdk.exceptions.exceptions import DeltaUnhealthyException
from bigeye_sdk.generated.com.bigeye.models.generated import (
    Table,
    Delta,
    DeltaInfo,
)

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator
from bigeye_sdk.log import get_logger

log = get_logger(__file__)


class RunDeltasOperator(ClientExtensibleOperator):
    """
    The RunDeltasOperator will run deltas in Bigeye based on the following:
    1. All deltas for a given table, by providing warehouse ID, schema name and table name.
    2. Any or all deltas, given a list of delta IDs.
    Currently, if a list of delta IDs is provided these will be run instead of deltas provided for
    warehouse_id, schema_name, table_name.
    """

    template_fields = ["delta_ids"]

    def __init__(
        self,
        warehouse_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        table_name: Optional[str] = None,
        connection_id: Optional[str] = "bigeye_conn",
        workspace_id: Optional[int] = None,
        delta_ids: Optional[List[int]] = None,
        circuit_breaker_mode: bool = False,
        *args,
        **kwargs,
    ):
        """
        param connection_id: string referencing a defined connection in the Airflow deployment, Default bigeye_conn.
        param warehouse_id: Optional[int] id of the warehouse where the operator will run the metrics.
        param schema_name: Optional[str] name of the schema where the table resides.
        param table_name: Optional[str] name of the table to run all metrics.
        param delta_ids: Optional[List[int]] list of delta IDs to run.
        param workspace_id: Optional[int] id of the workspace to run the deltas.
        param circuit_breaker_mode: bool Whether dag should raise an exception if delta results in alerting state, default False.
        param args: not currently supported
        param kwargs: not currently supported
        """
        super(RunDeltasOperator, self).__init__(*args, **kwargs)
        self.connection_id = connection_id
        self.workspace_id = workspace_id
        self.warehouse_id = warehouse_id
        self.schema_name = schema_name
        self.table_name = table_name
        self.delta_ids = delta_ids
        self.circuit_breaker_mode = circuit_breaker_mode
        self.client = None

    def get_client(self) -> DatawatchClient:
        if not self.client:
            self.client = AirflowDatawatchClient(
                connection_id=self.connection_id, workspace_id=self.workspace_id
            )
        return self.client

    def execute(self, context):
        delta_ids_to_run = self._set_delta_ids_to_run()
        return self._run_deltas(delta_ids_to_run)

    def _get_table_for_name(self, schema_name, table_name) -> Table:
        tables = (self.get_client().get_tables(warehouse_id=[self.warehouse_id],
                                               schema=[schema_name],
                                               table_name=[table_name]
                                               ).tables)
        if not tables:
            raise Exception(
                f"Could not find table: {self.table_name} in {self.schema_name}"
            )
        else:
            return tables.pop()

    def _set_delta_ids_to_run(self) -> List[int]:
        if self.delta_ids is None:
            table = self._get_table_for_name(self.schema_name, self.table_name)
            delta_infos: List[DeltaInfo] = self.get_client().get_deltas()
            deltas: List[DeltaInfo] = []
            for d in delta_infos:
                if (
                    table.id == d.delta.source_table.id
                    or table.id in [t.target_table_id for t in d.delta.comparison_table_configurations]
                ):
                    deltas.append(d)

            return [d.delta.id for d in deltas]
        else:
            return self.delta_ids

    def _run_deltas(self, delta_ids_to_run: List[int]) -> dict:
        success: List[dict] = []
        failure: List[dict] = []
        log.debug("Running delta IDs: %s", delta_ids_to_run)
        delta_infos: List[Delta] = []

        for did in delta_ids_to_run:
            delta_info = self.get_client().run_a_delta(delta_id=did, await_results=True)
            delta_infos.append(delta_info)

        num_failing_deltas = 0
        for di in delta_infos:
            if (di.alerting_metric_count + di.failed_metric_count) > 0:
                log.error(f"Delta is not OK: {di.name}")
                log.error(
                    f"# of alerting metrics: {di.alerting_metric_count}"
                )
                log.error(f"# of failing metrics: {di.failed_metric_count}")
                failure.append({"delta_id": di.id, "delta_name":di.name})
                num_failing_deltas += 1
            else:
                log.info(f"Delta is healthy: {di.name}")
                success.append({"delta_id": di.id, "delta_name": di.name})

        if self.circuit_breaker_mode and num_failing_deltas > 0:
            raise DeltaUnhealthyException(
                f"{num_failing_deltas} deltas have alerting or failed metrics."
            )

        return {"success": success, "failure": failure}
