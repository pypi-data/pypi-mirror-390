import logging
from typing import List, Optional

from bigeye_sdk.generated.com.bigeye.models.generated import (
    BatchRunMetricsResponse,
    MetricRunStatus,
    MetricInfo,
)
from bigeye_sdk.model.metric_facade import SimpleUpsertMetricRequest

from bigeye_sdk.client.datawatch_client import DatawatchClient

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator


HEALTHY_METRIC_STATUSES = [
    MetricRunStatus.METRIC_RUN_STATUS_OK,
    MetricRunStatus.METRIC_RUN_STATUS_MUTABLE_OK
]


class CreateMetricOperator(ClientExtensibleOperator):
    """
    The CreateMetricOperator takes a list of SimpleUpsertMetricRequest objects and instantiates them according to the
    business logic of Bigeye's API.
    """

    def __init__(self,
                 warehouse_id: int,
                 configuration: List[dict],
                 run_after_upsert: bool = False,
                 connection_id: Optional[str] = "bigeye_conn",
                 workspace_id: Optional[int] = None,
                 *args,
                 **kwargs):
        """
        param connection_id: string referencing a defined connection in the Airflow deployment, Default bigeye_conn.
        param warehouse_id: int id of the warehouse where the operator will upsert the metrics.
        param configuration: list of metric configurations to upsert.  The dicts passed as a list must conform to the
        dataclass SimplePredefinedMetricTemplate.
        param workspace_id: Optional[int] id of the workspace to create the metrics
        param run_after_upsert: bool whether the metric should be run after upsertion, default False.
        param args: not currently supported
        param kwargs: not currently supported
        """

        super(CreateMetricOperator, self).__init__(*args, **kwargs)
        self.configuration: List[SimpleUpsertMetricRequest] = []

        for c in configuration:
            c['warehouse_id'] = warehouse_id
            self.configuration.append(SimpleUpsertMetricRequest(**c))

        self.connection_id = connection_id
        self.workspace_id = workspace_id
        self.client = None

        self.run_after_upsert = run_after_upsert

    def get_client(self) -> DatawatchClient:
        if not self.client:
            self.client = AirflowDatawatchClient(
                connection_id=self.connection_id,
                workspace_id=self.workspace_id
            )
        return self.client

    def execute(self, context):

        num_failing_metric_runs = 0
        created_metrics_ids: List[int] = []

        # Iterate each configuration
        for c in self.configuration:

            metric_id = self.get_client().upsert_metric_from_simple_template(sumr=c)
            created_metrics_ids.append(metric_id)

            if self.run_after_upsert and metric_id is not None:
                logging.info(f"Running metric ID: {metric_id}")
                metric_infos: List[MetricInfo] = self.get_client().batch_run_metrics(
                    metric_ids=[metric_id],
                    queue=True
                )

                for mr in metric_infos:
                    if mr.status not in HEALTHY_METRIC_STATUSES:
                        logging.error("Metric is not OK: %s", metric_id)
                        logging.error("Metric result: %s", mr.status.value)
                        num_failing_metric_runs += 1

        return created_metrics_ids

