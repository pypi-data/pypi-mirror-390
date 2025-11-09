"""Maestro client to interact with Maestro server."""

from __future__ import annotations

import http.client
import json
import urllib.parse
from pathlib import Path
from typing import Any
import yaml


def _load_file(file_path: str | Path) -> str:
    """
    Load a file.

    :param file_path: file path
    :return: file content as string
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return path.read_text(encoding="utf-8")


def _validate_yaml(yaml_str: str) -> None:
    """
    Validate YAML and check invalid none value.

    :param yaml_str: yaml context to validate
    :raise yaml.YAMLError: if invalid
    """
    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid yaml with the error: {e}")

    def check_for_none_values(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                cur_path = f"{path}.{key}" if path else key
                if value is None:
                    raise yaml.YAMLError(f"Invalid yaml: '{cur_path}' has null/empty value. "
                                         f"Please check indentation and colons")
                check_for_none_values(value, cur_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_for_none_values(item, f"{path}[{i}]")

    check_for_none_values(data)


class MaestroClient:
    """
    Client to interact with Maestro.

    Example:
        >>> client = MaestroClient(base_url="http://127.0.0.1:8080", user="tester")
        >>> response = client.push("sample-workflow.yaml")
        >>> print(response)
    """

    def __init__(self, base_url: str, user: str):
        """
        Initialize Maestro python client.

        :param base_url: base url of maestro server (e.g., "http://127.0.0.1:8080")
        :param user:  username to use in API requests
        """
        self.parsed_url = urllib.parse.urlparse(base_url)
        self.user = user

    def _make_request(self, method: str, path: str, headers: dict[str, str],
                      body: bytes | None = None) -> dict[str, Any]:
        """
        Make a http request using http.client.

        :param method: http method (GET, POST, PUT, DELETE, etc.)
        :param path: request path
        :param headers: request headers
        :param body: request body
        :return: response from the server as dict
        """
        host = self.parsed_url.hostname or "localhost"
        port = self.parsed_url.port or (443 if self.parsed_url.scheme == "https" else 80)
        if self.parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(host, port)
        else:
            conn = http.client.HTTPConnection(host, port)

        try:
            conn.request(method, path, body=body, headers=headers)
            response = conn.getresponse()
            response_body = response.read().decode("utf-8")
            try:
                return json.loads(response_body)
            except json.JSONDecodeError:
                return {
                    "status_code": response.status,
                    "response": response_body,
                }
        finally:
            conn.close()

    def _send_yaml(self, method: str, path: str, yaml_str: str) -> dict[str, Any]:
        """
        Make a http request using http.client.

        :param method: http method (GET, POST, PUT, DELETE, etc.)
        :param path: API endpoint path
        :return: response from the server as dict
        :param yaml_str: yaml content
        :return: response from maestro server
        :raise: yaml.YAMLError: if invalid
        """
        _validate_yaml(yaml_str)
        headers = {"user": self.user, "Content-Type": "application/yaml"}
        return self._make_request(method, path, headers, yaml_str.encode("utf-8"))

    def push(self, yaml_file: str | Path) -> dict[str, Any]:
        """
        Push a yaml file including a workflow definition to maestro serve
        :param yaml_file: path the yaml file
        :return: response from the maestro server
        """
        return self.push_yaml(_load_file(yaml_file))

    def push_yaml(self, yaml_str: str) -> dict[str, Any]:
        """
        Push a workflow definition in the yaml format to maestro serve

        :param yaml_str: workflow as a yaml string
        :return: response from the maestro server
        """
        return self._send_yaml("POST", f"/api/v3/workflows/yaml", yaml_str)

    def validate(self, yaml_file: str | Path) -> dict[str, Any]:
        """
        Validate a yaml file including a workflow definition to maestro serve
        :param yaml_file: path the yaml file
        :return: response from the maestro server
        """
        return self.validate_yaml(_load_file(yaml_file))

    def validate_yaml(self, yaml_str: str) -> dict[str, Any]:
        """
        Validate a workflow definition in the yaml format to maestro serve

        :param yaml_str: workflow as a yaml string
        :return: response from the maestro server
        """
        return self._send_yaml("PUT", f"/api/v3/workflows/actions/validate/yaml", yaml_str)

    def start(self, workflow_id: str, version: str = "default", initiator: dict[str, Any] | None = None,
              run_params: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
        """
        Start a workflow execution.

        :param workflow_id: workflow id to start
        :param version: workflow version to start
        :param initiator: type of the initiator
        :param run_params: runtime params as a dict where each key is a dict with value and type,
                           e.g., {"foo": {"value": "bar", "type": "STRING"}}
        :return: the started workflow info.

        Example:
            >>> from maestro import Workflow, Job, MaestroClient
            >>> client = MaestroClient(base_url="http://127.0.0.1:8080", user="tester")
            >>> response = client.start(workflow_id="sample-wf",
            ...                         run_params={"foo": {"value": "bar", "type": "STRING"}})
        """
        headers = {"user": self.user, "Content-Type": "application/json"}
        path = f"/api/v3/workflows/{workflow_id}/versions/{version}/actions/start"
        payload = {"initiator": {"type": "manual"} if initiator is None else initiator}
        if run_params is not None:
            payload["run_params"] = run_params

        payload_bytes = json.dumps(payload).encode("utf-8")
        return self._make_request("POST", path, headers, payload_bytes)

    def stop(self, workflow_id: str, instance_id: int | None = None, step_id: str | None = None) -> dict[str, Any]:
        """
        Stop workflow execution(s).
        If only workflow_id is provided, stop all workflow instances of the given workflow id.
        If only workflow_id and instance_id are provided, stop a given workflow instance.
        If workflow_id, instance_id, and step_id are provided, stop a given step instance.

        :param workflow_id: workflow id to stop
        :param instance_id: if present, workflow instance id to stop
        :param step_id: if present, stop a given step instance
        :return: stop action response from maestro server.

        Example:
            >>> from maestro import Workflow, Job, MaestroClient
            >>> client = MaestroClient(base_url="http://127.0.0.1:8080", user="tester")
            >>> response = client.get_instance(workflow_id="sample-wf", instance_id=1)
        """
        headers = {"user": self.user, "Content-Type": "application/json"}
        if instance_id is None:
            path = f"/api/v3/workflows/{workflow_id}/actions/stop"
        elif step_id is None:
            path = f"/api/v3/workflows/{workflow_id}/instances/{instance_id}/actions/stop"
        else:
            path = f"/api/v3/workflows/{workflow_id}/instances/{instance_id}/steps/{step_id}/actions/stop"

        return self._make_request("PUT", path, headers)

    def get_workflow(self, workflow_id: str, version: str = "default", enriched: bool = False) -> dict[str, Any]:
        """
        Get a workflow definition.

        :param workflow_id: workflow id to get
        :param version: workflow version, e.g. default, latest, 1, etc.
        :param enriched: flag to indicate whether enriching the definition to return extra info
        :return: the workflow definition.

        Example:
            >>> from maestro import Workflow, Job, MaestroClient
            >>> client = MaestroClient(base_url="http://127.0.0.1:8080", user="tester")
            >>> response = client.get_workflow(workflow_id="sample-wf", version='latest')
        """
        headers = {"user": self.user, "Content-Type": "application/json"}
        path = f"/api/v3/workflows/{workflow_id}/versions/{version}?enriched={enriched}"

        return self._make_request("GET", path, headers)

    def get_instance(self, workflow_id: str, instance_id: int, step_id: str | None = None) -> dict[str, Any]:
        """
        Get a workflow instance or a step instance (if step id is provided).

        :param workflow_id: workflow id to get
        :param instance_id: workflow instance id to get
        :param step_id: if absent, return workflow instance, otherwise, return step instance
        :return: the workflow instance or step instance info.

        Example:
            >>> from maestro import Workflow, Job, MaestroClient
            >>> client = MaestroClient(base_url="http://127.0.0.1:8080", user="tester")
            >>> response = client.get_instance(workflow_id="sample-wf", instance_id=1)
        """
        headers = {"user": self.user, "Content-Type": "application/json"}
        path = f"/api/v3/workflows/{workflow_id}/instances/{instance_id}" if step_id is None \
            else f"/api/v3/workflows/{workflow_id}/instances/{instance_id}/steps/{step_id}"

        return self._make_request("GET", path, headers)
