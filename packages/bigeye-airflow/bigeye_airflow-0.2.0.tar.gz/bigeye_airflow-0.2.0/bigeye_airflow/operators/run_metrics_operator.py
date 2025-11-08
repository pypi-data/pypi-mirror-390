import logging
from typing import List, Optional

from bigeye_sdk.client.datawatch_client import DatawatchClient
from bigeye_sdk.exceptions.exceptions import MetricUnhealthyException
from bigeye_sdk.generated.com.bigeye.models.generated import Table, MetricConfiguration, \
    MetricInfo, MetricRunStatus

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator


HEALTHY_METRIC_STATUSES = [
    MetricRunStatus.METRIC_RUN_STATUS_OK,
    MetricRunStatus.METRIC_RUN_STATUS_MUTABLE_OK
]


class RunMetricsOperator(ClientExtensibleOperator):
    """
        The RunMetricsOperator will run metrics in Bigeye based on the following:
        1. All metrics for a given table, by providing warehouse ID, schema name and table name.
        2. All metrics for a given collection, by providing the collection ID.
        3. Any or all metrics, given a list of metric IDs.
        Currently, if a list of metric IDs is provided these will be run instead of metrics provided for
        warehouse_id, schema_name, table_name, and collection_id.
    """

    template_fields = ["metric_ids"]

    def __init__(self,
                 warehouse_id: Optional[int] = None,
                 schema_name: Optional[str] = None,
                 table_name: Optional[str] = None,
                 collection_id: Optional[int] = None,
                 metric_ids: Optional[List[int]] = None,
                 connection_id: Optional[str] = "bigeye_conn",
                 workspace_id: Optional[int] = None,
                 circuit_breaker_mode: bool = False,
                 tolerance: Optional[int] = 0,
                 *args,
                 **kwargs):
        """
                param connection_id: string referencing a defined connection in the Airflow deployment, Default bigeye_conn.
                param warehouse_id: Optional[int] id of the warehouse where the operator will run the metrics.
                param schema_name: Optional[str] name of the schema where the table resides.
                param table_name: Optional[str] name of the table to run all metrics.
                param collection_id: Optional[int] id of the collection where the operator will run the metrics.
                param metric_ids: Optional[List[int]] list of metric IDs to run.
                param workspace_id: Optional[int] id of the workspace to run the metrics.
                param circuit_breaker_mode: bool Whether dag should raise an exception if metrics result in alerting
                state, default False.
                param tolerance: Optional[int] The number of metrics where alerting is tolerable. Only applicable when
                circuit_breaker_mode is True. Default 0.
                param args: not currently supported
                param kwargs: not currently supported
        """
        super(RunMetricsOperator, self).__init__(*args, **kwargs)
        self.connection_id = connection_id
        self.workspace_id = workspace_id
        self.warehouse_id = warehouse_id
        self.schema_name = schema_name
        self.table_name = table_name
        self.collection_id = collection_id
        self.metric_ids = metric_ids
        self.circuit_breaker_mode = circuit_breaker_mode
        self.tolerance = tolerance
        self.connection_id = connection_id
        self.client = None

    def get_client(self) -> DatawatchClient:
        if not self.client:
            self.client = AirflowDatawatchClient(
                connection_id=self.connection_id,
                workspace_id=self.workspace_id
            )
        return self.client

    def execute(self, context):

        metric_ids_to_run = self._set_metric_ids_to_run()
        return self._run_metrics(metric_ids_to_run)

    def _get_table_for_name(self, schema_name, table_name) -> Table:
        tables = self.get_client().get_tables(warehouse_id=[self.warehouse_id],
                                              schema=[schema_name],
                                              table_name=[table_name]).tables

        if not tables:
            raise Exception(f"Could not find table: {self.table_name} in {self.schema_name}")
        else:
            return tables.pop()

    def _set_metric_ids_to_run(self) -> List[int]:
        if self.metric_ids is None and self.table_name:
            table = self._get_table_for_name(self.schema_name, self.table_name)
            metrics: List[MetricConfiguration] = self.get_client().search_metric_configuration(
                warehouse_ids=[table.warehouse_id],
                table_ids=[table.id])

            return [m.id for m in metrics]
        elif self.metric_ids is None and self.collection_id:
            return self.get_client().get_collection(collection_id=self.collection_id).collection.metric_ids
        else:
            return self.metric_ids

    def _run_metrics(self, metric_ids_to_run: List[int]) -> dict:
        success: List[str] = []
        failure: List[str] = []
        logging.debug("Running metric IDs: %s", metric_ids_to_run)

        # TODO update this call when backend returns BatchMetricRunResponse in workflow status
        # https://linear.app/torodata/issue/HELP-721/return-batchrunmetricsresponse-with-workflow-response
        metric_infos: List[MetricInfo] = self.get_client().run_metric_batch(metric_ids=metric_ids_to_run).metric_infos
        num_failing_metrics = 0
        for mi in metric_infos:
            if mi.status not in HEALTHY_METRIC_STATUSES:
                logging.error(f"Metric is not OK: {mi.metric_configuration.name}")
                logging.error(f"Metric result: {mi.metric_configuration}")
                failure.append(mi.to_json())
                num_failing_metrics += 1
            else:
                success.append(mi.to_json())

        if self.circuit_breaker_mode and num_failing_metrics > self.tolerance:
            raise MetricUnhealthyException(
                f"{num_failing_metrics} alerting metrics detected by Bigeye."
            )

        return {"success": success, "failure": failure}
