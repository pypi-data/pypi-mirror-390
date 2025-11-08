import logging
from typing import List, Optional

from bigeye_sdk.generated.com.bigeye.models.generated import (
    Delta,
)
from bigeye_sdk.model.delta_facade import SimpleDeltaConfiguration

from bigeye_sdk.client.datawatch_client import DatawatchClient

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator


class CreateDeltaOperator(ClientExtensibleOperator):
    """
    The CreateDeltaOperator takes a list of SimpleDeltaConfiguration objects and instantiates them according to the
    business logic of Bigeye's API.
    """

    def __init__(self,
                 configuration: List[dict],
                 run_after_upsert: bool = False,
                 connection_id: Optional[str] = "bigeye_conn",
                 workspace_id: Optional[int] = None,
                 *args,
                 **kwargs):
        """
        param connection_id: string referencing a defined connection in the Airflow deployment, Default bigeye_conn.
        param configuration: list of delta configurations to upsert.  The dicts passed as a list must conform to the
        dataclass SimpleDeltaConfiguration.
        param workspace_id: Optional[int] id of the workspace to create the deltas.
        param run_after_upsert: bool whether the delta should be run after upsertion, default False.
        param args: not currently supported
        param kwargs: not currently supported
        """

        super(CreateDeltaOperator, self).__init__(*args, **kwargs)
        self.configuration: List[SimpleDeltaConfiguration] = []

        for c in configuration:
            self.configuration.append(SimpleDeltaConfiguration(**c))

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

        num_failing_delta_runs = 0
        created_delta_ids: List[int] = []

        deltas = self.get_client().create_deltas_from_simple_conf(self.configuration)

        # Iterate each configuration
        for d in deltas:

            created_delta_ids.append(d.id)

            if self.run_after_upsert and d.id is not None:
                logging.info(f"Running Delta ID: {d.id}")
                delta_result: Delta = self.get_client().run_a_delta(delta_id=d.id, await_results=True)

                if (delta_result.alerting_metric_count + delta_result.failed_metric_count) > 0:
                    logging.error("Delta is alerting: %s", d.name)
                    logging.error("Num alerting metrics: %s", delta_result.alerting_metric_count)
                    logging.error("Num failing metrics: %s", delta_result.failed_metric_count)
                    num_failing_delta_runs += 1

        return created_delta_ids

