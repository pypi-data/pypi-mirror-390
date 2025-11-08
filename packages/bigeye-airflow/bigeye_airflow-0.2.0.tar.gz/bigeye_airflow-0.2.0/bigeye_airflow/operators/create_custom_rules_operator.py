import logging
from typing import List, Optional

from bigeye_sdk.generated.com.bigeye.models.generated import (
    MetricRunStatus,
    CustomRule,
)

from bigeye_sdk.client.datawatch_client import DatawatchClient

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator

HEALTHY_METRIC_STATUSES = [
    MetricRunStatus.METRIC_RUN_STATUS_OK,
    MetricRunStatus.METRIC_RUN_STATUS_MUTABLE_OK
]

# TODO Create abstract SimpleCustomRule class and use here


class CreateCustomRulesOperator(ClientExtensibleOperator):
    """
    The CreateCustomRulesOperator takes a list of CustomRule objects and instantiates them according to the
    business logic of Bigeye's API.
    """

    def __init__(self,
                 source_id: int,
                 configuration: List[CustomRule],
                 connection_id: Optional[str] = "bigeye_conn",
                 workspace_id: Optional[int] = None,
                 *args,
                 **kwargs):
        """
        param connection_id: string referencing a defined connection in the Airflow deployment, Default bigeye_conn.
        param source_id: int id of the source where the operator will upsert the custom rules.
        param configuration: list of CustomRule configurations to upsert.
        param workspace_id: Optional[int] id of the workspace to create the custom rules
        param args: not currently supported
        param kwargs: not currently supported
        """

        super(CreateCustomRulesOperator, self).__init__(*args, **kwargs)
        self.configuration: List[CustomRule] = []
        self.source_id = source_id
        for c in configuration:
            c.warehouse_id = source_id
            self.configuration.append(c)

        self.connection_id = connection_id
        self.workspace_id = workspace_id
        self.client = None

    def get_client(self) -> DatawatchClient:
        if not self.client:
            self.client = AirflowDatawatchClient(
                connection_id=self.connection_id,
                workspace_id=self.workspace_id
            )
        return self.client

    def execute(self, context):

        created_rule_ids: List[int] = []

        # Iterate each configuration
        for c in self.configuration:

            all_custom_rules = self.get_client().get_rules_for_source(warehouse_id=self.source_id).custom_rules
            existing_cr = next((cr for cr in all_custom_rules if cr.custom_rule.name.lower() == c.name.lower()), None)

            if existing_cr:
                logging.info(f'Custom rule with name {existing_cr.custom_rule.name} already exists. Updating rule.')
                rule = self.get_client().edit_custom_rule(
                    custom_rule=existing_cr.custom_rule,
                    rule_id=existing_cr.id
                )
                logging.info(f'Custom rule {existing_cr.custom_rule.name} successfully updated.')
            else:
                rule = self.get_client().create_custom_rule(
                    warehouse_id=c.warehouse_id,
                    name=c.name,
                    sql=c.sql,
                    threshold_type=c.threshold_type,
                    upper_threshold=c.upper_threshold,
                    lower_threshold=c.lower_threshold,
                    collection_ids=c.collection_ids,
                    schedule=c.metric_schedule
                )
                logging.info(f'Custom rule {rule.custom_rule.name} successfully created.')
            created_rule_ids.append(rule.id)

        return created_rule_ids
