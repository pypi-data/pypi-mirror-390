import logging
from json import JSONDecodeError
from typing import Optional

from airflow.providers.http.hooks.http import HttpHook
from bigeye_sdk.client.datawatch_client import DatawatchClient, Method

headers = {"Content-Type": "application/json", "Accept": "application/json"}


class AirflowDatawatchClient(DatawatchClient):
    def __init__(self, connection_id: str, workspace_id: Optional[int] = None):
        self.conn_id = connection_id
        self.workspace_id = workspace_id
        pass

    def _get_hook(self, method) -> HttpHook:
        return HttpHook(http_conn_id=self.conn_id, method=method)

    def _call_datawatch_impl(self, method: Method, url, body: str = None):
        bigeye_request_hook = self._get_hook(method.name)

        if self.workspace_id:
            headers.update({"x-bigeye-workspace-id": f'{self.workspace_id}'})

        try:
            response = bigeye_request_hook.run(
                endpoint=url,
                headers=headers,
                data=body)

        except Exception as e:
            logging.error(f'Exception calling airflow datawatch: {str(e)}')
            raise e

        if response.status_code != 204:
            try:
                return response.json()
            except JSONDecodeError as e:
                logging.info(f"Cannot decode response.  {response}")
                return ""

    def _call_datawatch(self, method: Method, url, body: str = None):
        url = url.replace('//', '/')
        return self._call_datawatch_impl(method=method, url=url, body=body)
