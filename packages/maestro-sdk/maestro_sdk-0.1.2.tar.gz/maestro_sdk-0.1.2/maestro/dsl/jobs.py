"""Job builders for Maestro DSL. """

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

try:
    from typing import Self  # Python 3.11+
except ImportError:
    from typing import TypeVar
    Self = TypeVar("Self")  # fallback


_JOB_RESERVED_FIELDS = {
    "id", "name", "description", "owner", "type", "type_version", "failure_mode", "concurrency",
    "timeout", "criticality", "tags", "tag", "jobs", "job", "dag", "step", "steps",
    "transition", "transitions", "condition", "param", "params", "job_params",
    "ranges", "range", "loop_params", "loop_param", "explicit_params", "sync",
    "workflow_id", "subworkflow_id", "version", "subworkflow_version"
}


@dataclass
class JobBase(ABC):
    """Base class for all job types."""
    id: str = field(repr=True, kw_only=True)
    _name: str | None = field(default=None, repr=True)
    _description: str | None = field(default=None, repr=True)
    _failure_mode: str | None = field(default=None, repr=True)
    _tags: list[str] = field(default_factory=list, repr=True)
    _timeout: str | None = field(default=None, repr=True)
    _transition: list[str] = field(default_factory=list, repr=True)
    _job_params: dict[str, Any] = field(default_factory=dict, repr=False)

    def name(self, name: str) -> Self:
        """Set job name"""
        self._name = name
        return self

    def description(self, description: str) -> Self:
        """Set job description."""
        self._description = description
        return self

    def failure_mode(self, mode: str) -> Self:
        """Set failure mode of the job."""
        self._failure_mode = mode
        return self

    def tag(self, tag: str) -> Self:
        """Add a tag to the job."""
        self._tags.append(tag)
        return self

    def tags(self, *tags: str) -> Self:
        """Set tags of the job."""
        self._tags = list(tags)
        return self

    def timeout(self, timeout: str) -> Self:
        """Set job timeout."""
        self._timeout = timeout
        return self

    def transition(self, *successors: str) -> Self:
        """
        Set transition successors of the job.

        Example:
            transition:
            - job2
            - IF x > 0 THEN job3
            - IF x > 1 THEN job4
            - OTHERWISE job5
        """
        self._transition = list(successors)
        return self

    def param(self, name: str, value: Any) -> Self:
        """
        Add a job param.

        Raises:
            NameError: If param name conflicts with reserved job field
        :param name: param name
        :param value: param value
        :return: job
        """
        if name in _JOB_RESERVED_FIELDS:
            raise NameError(
                f"Param name '{name}' conflicts with one of reserved job fields."
                f"Reserved fields are: '{_JOB_RESERVED_FIELDS}'."
            )
        self._job_params[name] = value
        return self

    def param_expr(self, name: str, expr: str) -> Self:
        """
        Add a SEL expression param.
        """
        return self.param(f"!{name}", expr)

    def to_dict_base(self) -> dict[str, Any]:
        """
        Serialize DSL workflow object to a dict.

        :return: dict with all workflow fields.
        """
        result: dict[str, Any] = {"id": self.id}

        self._set_optional_fields(result, {
            "name": "_name", "description": "_description", "failure_mode": "_failure_mode",
            "tags": "_tags", "timeout": "_timeout", "transition": "_transition",
        })

        result.update(self._job_params)

        return result

    def _set_optional_fields(self, result: dict[str, Any], field_map: dict[str, str]) -> None:
        for key, attr in field_map.items():
            value = getattr(self, attr, None)
            if value is not None:
                result[key] = value

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize a job to dict. Must be implemented by subclasses. """


@dataclass
class Job(JobBase):
    """
    Typed job for predefined job templates, e.g. spark, shell, etc.

    Example:
        >>> Job(id="job1", type="shell")
        >>> Job(id="job1", type="shell").type_version("v1")
    """
    type: str = field(kw_only=True, repr=True)  # job template type id
    _type_version: str | None = field(default=None, repr=True)

    def type_version(self, version: str) -> Self:
        """Set job template type version."""
        self._type_version = version
        return self

    def to_dict(self) -> dict[str, Any]:
        """Serialize a DSL typed job to a dict."""
        result: dict[str, Any] = self.to_dict_base()
        result["type"] = self.type

        self._set_optional_fields(result, {
            "type_version": "_type_version",
        })

        return {"job": result}


@dataclass
class Subworkflow(JobBase):
    """
    Subworkflow job to invoke another workflow.

    Example:
        >>> Subworkflow(id="job1")
        >>> Subworkflow(id="job1").workflow_id("child").version("v1")
    """
    _workflow_id: str | None = field(default=None, repr=True)
    _workflow_version: str | None = field(default=None, repr=True)
    _sync: bool | None = field(default=None, repr=True)
    _explicit_params: bool | None = field(default=None, repr=True)

    def workflow_id(self, workflow_id: str) -> Self:
        """Set subworkflow workflow id."""
        self._workflow_id = workflow_id
        return self

    def version(self, version: str) -> Self:
        """Set subworkflow workflow version."""
        self._workflow_version = version
        return self

    def sync(self, sync: bool) -> Self:
        """Set whether to run subworkflow synchronously (blocking until completion) or not."""
        self._sync = sync
        return self

    def explicit_params(self, explicit_params: bool) -> Self:
        """Set whether to pass params explicitly to subworkflow."""
        self._explicit_params = explicit_params
        return self

    def to_dict(self) -> dict[str, Any]:
        """Serialize a DSL subworkflow job to a dict."""
        result: dict[str, Any] = self.to_dict_base()

        self._set_optional_fields(result, {
            "workflow_id": "_workflow_id", "workflow_version": "_workflow_version", "sync": "_sync",
            "explicit_params": "_explicit_params",
        })

        return {"subworkflow": result}


@dataclass
class LoopBase(JobBase, ABC):
    """Base ABC loop job for foreach and while."""
    _loop_params: dict[str, Any] = field(default_factory=dict, repr=True)
    _jobs: list[JobBase] = field(default_factory=list, repr=True)
    _dag: str | dict[str, Any] | None = field(default=None, repr=True)

    def loop_param(self, name: str, value: Any) -> Self:
        """
        Add a loop param, which is updated during while loop iterations.

        Raises:
            NameError: If param name conflicts with reserved job field
        :param name: param name
        :param value: param value
        :return: while job
        """
        if name in _JOB_RESERVED_FIELDS:
            raise NameError(
                f"Loop param name '{name}' conflicts with one of reserved job fields."
                f"Reserved fields are: ${_JOB_RESERVED_FIELDS}."
            )
        self._loop_params[name] = value
        return self

    def loop_param_expr(self, name: str, expr: str) -> Self:
        """
        Add a SEL expression defined loop param .
        """
        return self.loop_param(f"!{name}", expr)

    def job(self, job: JobBase) -> Self:
        """Add a nested job to the foreach iteration."""
        self._jobs.append(job)
        return self

    def jobs(self, *jobs: JobBase) -> Self:
        """set jobs of the workflow."""
        self._jobs = list(jobs)
        return self

    def dag(self, dag: str | dict[str, Any]) -> Self:
        """
        Set DAG of foreach iteration.

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

    def to_dict_loop(self) -> dict[str, Any]:
        """Serialize a DSL loop job to a dict."""
        result: dict[str, Any] = self.to_dict_base()

        self._set_optional_fields(result, {
            "loop_params": "_loop_params", "dag": "_dag"
        })

        if self._jobs:
            result["jobs"] = [job.to_dict() for job in self._jobs]

        return result


@dataclass
class Foreach(LoopBase):
    """
    Foreach loop job that iterates over arrays or ranges.

    Example:
        >>> Foreach(id="job1").loop_param("foo", [1, 2, 3])
        >>> Foreach(id="job1").range("i", 0, 10)
    """
    _concurrency: int | None = field(default=None, repr=True)
    _ranges: dict[str, tuple[int | None, int, int | None]] = field(default_factory=dict, repr=True)

    def concurrency(self, concurrency: int) -> Self:
        """Set foreach loop iteration concurrency."""
        self._concurrency = concurrency
        return self

    def range(self, name: str, start: int | None = None, stop: int = None, step: int | None = None) -> Self:
        """
        Set a numeric range to iterate over.

        Args:
        :param name: param name
        :param start: start value (inclusive, optional)
        :param stop: end value (exclusive)
        :param step: step size (optional)
        :return: foreach job

        Example:
            >>> Foreach(id="job1").range("i", 0, 10)
        """
        self._ranges[name] = (start, stop, step)
        return self

    def to_dict(self) -> dict[str, Any]:
        """Serialize a DSL foreach job to a dict."""
        result: dict[str, Any] = self.to_dict_loop()

        self._set_optional_fields(result, {
            "concurrency": "_concurrency", "ranges": "_ranges",
        })

        return {"foreach": result}


@dataclass
class While(LoopBase):
    """
    While loop job that iterates until the condition is not true.

    Example:
        >>> While(id="job1").condition("x < 0")
        >>> While(id="job1").condition("x > 0").loop_param("x", 1)
    """
    _condition: str | None = field(default=None, repr=True)

    def condition(self, condition: str) -> Self:
        """Set while loop iteration condition, which is defined using a SEL expression."""
        self._condition = condition
        return self

    def to_dict(self) -> dict[str, Any]:
        """Serialize a DSL foreach job to a dict."""
        result: dict[str, Any] = self.to_dict_loop()

        self._set_optional_fields(result, {
            "condition": "_condition"
        })

        return {"while": result}
