import json
import os

from typing import Optional

from bigeye_airflow.airflow_datawatch_client import AirflowDatawatchClient
from bigeye_airflow.operators.client_extensible_operator import ClientExtensibleOperator

from bigeye_sdk.client.datawatch_client import DatawatchClient
from bigeye_sdk.functions.file_functs import read_json_file
from bigeye_sdk.log import get_logger

log = get_logger(__file__)


class BigeyeDbtCoreOperator(ClientExtensibleOperator):
    """
    An operator for syncing dbt core job runs with Bigeye.

    Attributes
    ----------
    connection_id: str
        defined connection in the Airflow deployment, Default bigeye_conn.
    workspace_id: int
        Bigeye workspace ID to sync; e.g. https://app.bigeye.com/w/<workspace_id>
    sync_to_bigeye: bool
        post to Bigeye
    project_name: str
        dbt project name.
        If omitted, attempt to parse from the manifest.json metadata
    job_name: str
        dbt job name.
        If omitted, use AIRFLOW_CTX_DAG_ID
    job_run_id: str
        dbt job name.
        If omitted, use AIRFLOW_CTX_DAG_RUN_ID
    target_path: str
        path where dbt artifacts reside
    project_url: str
        dbt project url
    job_url: str
        dbt job url
    job_run_url: str
        dbt job run url
    """

    def __init__(
        self,
        workspace_id: int,
        sync_to_bigeye: bool = True,
        connection_id: Optional[str] = "bigeye_conn",
        project_name: Optional[str] = None,
        job_name: Optional[str] = None,
        job_run_id: Optional[str] = None,
        target_path: str = "./target",
        project_url: Optional[str] = None,
        job_url: Optional[str] = None,
        job_run_url: Optional[str] = None,
        *args,
        **kwargs,
    ):

        super(BigeyeDbtCoreOperator, self).__init__(*args, **kwargs)
        self.client = None
        self.connection_id = connection_id
        self.workspace_id = workspace_id
        self.sync_to_bigeye = sync_to_bigeye
        self.job_run_url = job_run_url
        self.job_url = job_url
        self.project_url = project_url
        self.target_path = target_path
        self.job_run_id = job_run_id
        self.job_name = job_name
        self.project_name = project_name

    def get_client(self) -> DatawatchClient:
        if not self.client:
            self.client = AirflowDatawatchClient(
                connection_id=self.connection_id, workspace_id=self.workspace_id
            )
            return self.client

    def execute(self, context):

        if self.sync_to_bigeye:

            manifest_json = read_json_file(
                file_path=f"{self.target_path}/manifest.json"
            )
            run_results_json = read_json_file(
                file_path=f"{self.target_path}/run_results.json"
            )

            if not self.job_run_id:
                log.info(f"No job run ID set. Using value of Airflow DAG run ID.")
                self.job_run_id = os.getenv("AIRFLOW_CTX_DAG_RUN_ID")

            if not self.job_name:
                log.info(f"No job name set. Using value of Airflow DAG ID.")
                self.job_name = os.getenv("AIRFLOW_CTX_DAG_ID")

            log.info(
                f"Syncing Bigeye with dbt job\n\tjob name: {self.job_name}\n\tjob run ID: {self.job_run_id}"
            )
            self.get_client().send_dbt_core_job_info(
                project_name=self.project_name,
                job_name=self.job_name,
                job_run_id=self.job_run_id,
                manifest_json=json.dumps(manifest_json),
                run_results_json=json.dumps(run_results_json),
                project_url=self.project_url,
                job_url=self.job_url,
                job_run_url=self.job_run_url,
            )
