"""Workflow builder for Maestro DSL. """

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from .jobs import JobBase

try:
    from typing import Self  # Python 3.11+
except ImportError:
    from typing import TypeVar
    Self = TypeVar("Self")  # fallback

import yaml


# Reserved workflow field names that cannot be used as param names
_WORKFLOW_RESERVED_FIELDS = {
    "id", "name", "description", "owner", "run_strategy", "workflow_concurrency", "concurrency",
    "timeout", "criticality", "tags", "tag", "jobs", "job", "dag", "param", "params",
    "step", "steps", "transition", "transitions", "workflow_params", "workflow_param",
}


FIELD_MAP = {
    "name": "_name",
    "description": "_description",
    "owner": "_owner",
    "run_strategy": "_run_strategy",
    "workflow_concurrency": "_workflow_concurrency",
    "timeout": "_timeout",
    "criticality": "_criticality",
    "tags": "_tags",
    "jobs": "_jobs",
    "dag": "_dag"
}


@dataclass
class Workflow:
    """
    Workflow builder.

    It includes fields defined in Maestro DSL specs:
    - https://github.com/Netflix/maestro/tree/main/maestro-dsl

    Example:
        >>> wf = Workflow(id="test-wf")
        >>> wf.owner("tester").tags("test")
        >>> wf.job(Job(id="job1", type='NoOp'))
        >>> wf_yaml = wf.to_yaml()
    """

    id: str
    _name: str | None = field(default=None, repr=True)
    _description: str | None = field(default=None, repr=True)
    _owner: str | None = field(default=None, repr=True)
    _run_strategy: str | None = field(default=None, repr=True)
    _workflow_concurrency: int | None = field(default=None, repr=True)
    _timeout: str | None = field(default=None, repr=True)
    _criticality: str | None = field(default=None, repr=True)
    _tags: list[str] = field(default_factory=list, repr=True)
    _jobs: list[JobBase] = field(default_factory=list, repr=True)
    _dag: str | dict[str, Any] | None = field(default=None, repr=True)
    _workflow_params: dict[str, Any] = field(default_factory=dict, repr=False)

    def name(self, name: str) -> Self:
        """Set workflow name"""
        self._name = name
        return self

    def description(self, description: str) -> Self:
        """Set workflow description."""
        self._description = description
        return self

    def owner(self, owner: str) -> Self:
        """Set workflow owner."""
        self._owner = owner
        return self

    def run_strategy(self, strategy: str) -> Self:
        """Set workflow run strategy."""
        self._run_strategy = strategy
        return self

    def concurrency(self, concurrency: int) -> Self:
        """Set workflow concurrency."""
        self._workflow_concurrency = concurrency
        return self

    def timeout(self, timeout: str) -> Self:
        """Set workflow timeout."""
        self._timeout = timeout
        return self

    def criticality(self, criticality: str) -> Self:
        """Set workflow criticality."""
        self._criticality = criticality
        return self

    def tag(self, tag: str) -> Self:
        """Add a tag to the workflow."""
        self._tags.append(tag)
        return self

    def tags(self, *tags: str) -> Self:
        """Set tags of the workflow."""
        self._tags = list(tags)
        return self

    def job(self, job: JobBase) -> Self:
        """Add a job to the workflow."""
        self._jobs.append(job)
        return self

    def jobs(self, *jobs: JobBase) -> Self:
        """set jobs of the workflow."""
        self._jobs = list(jobs)
        return self

    def dag(self, dag: str | dict[str, Any]) -> Self:
        """
        Set DAG of the workflow.

        Example 1:
            dag: sequential

        Example 2:
            dag:
              job1: job2
              job2:
                - IF x > 0 THEN job3
                - IF x > 1 THEN job4
                - OTHERWISE job5
              job5:
                - job6
        """
        self._dag = dag
        return self

    def param(self, name: str, value: Any) -> Self:
        """
        Add a workflow param.

        Raises:
            NameError: If param name conflicts with reserved workflow field
        :param name: param name
        :param value: param value
        :return: workflow
        """
        if name in _WORKFLOW_RESERVED_FIELDS:
            raise NameError(
                f"Param name '{name}' conflicts with one of reserved workflow fields."
                f"Reserved fields are: ${_WORKFLOW_RESERVED_FIELDS}."
            )
        self._workflow_params[name] = value
        return self

    def param_expr(self, name: str, expr: str) -> Self:
        """
        Add a SEL expression param.
        """
        return self.param(f"!{name}", expr)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize DSL workflow object to a dict keyed by 'Workflow'.

        :return: dict with 'Workflow' key including all workflow fields.
        """
        result: dict[str, Any] = {"id": self.id}

        for key, attr in FIELD_MAP.items():
            value = getattr(self, attr, None)
            if value is not None:
                result[key] = value

        result.update(self._workflow_params)

        if self._jobs:
            result["jobs"] = [job.to_dict() for job in self._jobs]

        return {"Workflow": result}

    def to_yaml(self, file_path: str | Path | None = None) -> str:
        """
        Serialize workflow to yaml
        :param file_path: optional path to write yaml file
        :return: yaml string
        """
        yaml_str = yaml.dump(
            self.to_dict(),
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

        if file_path:
            Path(file_path).write_text(yaml_str, encoding="utf-8")

        return yaml_str
