import logging
from operator import attrgetter
from typing import List, Optional

from bigeye_sdk.client.datawatch_client import DatawatchClient
from bigeye_sdk.exceptions.exceptions import MetricUnhealthyException
from bigeye_sdk.generated.com.bigeye.models.generated import MetricRunStatus, CustomRuleInfo

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator


HEALTHY_METRIC_STATUSES = [
    MetricRunStatus.METRIC_RUN_STATUS_OK,
    MetricRunStatus.METRIC_RUN_STATUS_MUTABLE_OK
]


class RunCustomRulesOperator(ClientExtensibleOperator):
    """
        The RunCustomRulesOperator will run custom rules in Bigeye based on the following:
        1. All custom rules for a given source, by providing source ID.
        2. All custom rules for a given collection, by providing the collection ID.
        3. Any or all custom rules, given a list of custom rule names.
        4. Any or all custom rules, given a list of custom rule IDs.
        Currently, if a list of metric IDs is provided these will be run instead of metrics provided for
        warehouse_id, schema_name, table_name, and collection_id.
    """

    def __init__(self,
                 source_id: Optional[int] = None,
                 collection_id: Optional[int] = None,
                 rule_names: Optional[List[str]] = None,
                 rule_ids: Optional[List[int]] = None,
                 connection_id: Optional[str] = "bigeye_conn",
                 workspace_id: Optional[int] = None,
                 circuit_breaker_mode: bool = False,
                 tolerance: Optional[int] = 0,
                 *args,
                 **kwargs):
        """
                param connection_id: string referencing a defined connection in the Airflow deployment, Default bigeye_conn.
                param source_id: Optional[int] The id of the source where the operator will run the custom rules.
                param collection_id: Optional[int] id of the collection where the operator will run the metrics.
                param rule_names: Optional[List[str]] list of rule names to run.
                param rule_ids: Optional[List[int]] list of rule IDs to run.
                param workspace_id: Optional[int] id of the workspace to run the metrics.
                param circuit_breaker_mode: bool Whether dag should raise an exception if custom rules result in alerting
                state, default False.
                param tolerance: Optional[int] The number of metrics where alerting is tolerable. Only applicable when
                circuit_breaker_mode is True. Default 0.
                param args: not currently supported
                param kwargs: not currently supported
        """
        super(RunCustomRulesOperator, self).__init__(*args, **kwargs)
        self.connection_id = connection_id
        self.workspace_id = workspace_id
        self.source_id = source_id
        self.collection_id = collection_id
        self.rule_names = rule_names
        self.rule_ids = rule_ids
        self.circuit_breaker_mode = circuit_breaker_mode
        self.tolerance = tolerance
        self.client = None

    def get_client(self) -> DatawatchClient:
        if not self.client:
            self.client = AirflowDatawatchClient(
                connection_id=self.connection_id,
                workspace_id=self.workspace_id
            )
        return self.client

    def execute(self, context):
        custom_rules_to_run = self._get_custom_rules_to_run()
        return self._run_custom_rules(custom_rules_to_run)

    def _get_custom_rules_to_run(self) -> List[CustomRuleInfo]:
        custom_rules = self.get_client().get_rules(warehouse_id=self.source_id, collection_id=self.collection_id)

        if self.rule_names:
            requested_names = [rn.lower() for rn in self.rule_names]
            custom_rules = [c for c in custom_rules.custom_rules if c.custom_rule.name.lower() in requested_names]
        elif self.rule_ids:
            custom_rules = [c for c in custom_rules.custom_rules if c.id in self.rule_ids]
        else:
            custom_rules = [c for c in custom_rules.custom_rules]

        return custom_rules

    @staticmethod
    def _get_latest_run_for_custom_rule(custom_rule: CustomRuleInfo):
        return max(custom_rule.latest_runs, key=attrgetter('run_at_epoch_seconds'))

    def _run_custom_rules(self, custom_rules_to_run: List[CustomRuleInfo]) -> dict:
        success: List[str] = []
        failure: List[str] = []
        custom_rule_ids = [c.id for c in custom_rules_to_run]
        logging.info("Running custom rule IDs: %s", custom_rule_ids)

        # sync api call to run all rules
        custom_rule_runs = self.get_client().bulk_run_rules(rule_ids=custom_rule_ids)

        # This is different from alerting, this is the sql failed for some reason
        # if run failed and this is a circuit breaker then raise exception
        for failed_run in custom_rule_runs.failed_updates:
            if self.circuit_breaker_mode:
                raise Exception(
                    f"Custom rule ID: {failed_run.id} failed to run due to : {failed_run.reason}"
                )

        # go and get the updated statuses again now that custom rules have been run
        custom_rule_statuses = self._get_custom_rules_to_run()

        num_failing_rules = 0
        for cr in custom_rule_statuses:
            latest_run = self._get_latest_run_for_custom_rule(cr)
            if latest_run.status not in HEALTHY_METRIC_STATUSES:
                logging.error(f"Custom rule {cr.custom_rule.name} returned an unhealthy result: {latest_run.status}")
                failure.append(cr.to_json())
                num_failing_rules += 1
            else:
                success.append(cr.to_json())

        if self.circuit_breaker_mode and num_failing_rules > self.tolerance:
            raise MetricUnhealthyException(
                f"{num_failing_rules} alerting custom rules detected by Bigeye."
            )

        return {"success": success, "failure": failure}
