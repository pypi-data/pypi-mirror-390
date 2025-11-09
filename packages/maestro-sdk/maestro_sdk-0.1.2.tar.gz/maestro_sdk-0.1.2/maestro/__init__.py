"""
Python sdk client library.

Example:
    >>> from maestro import Workflow, Job, MaestroClient
    >>> wf = Workflow(id="test-wf")
    >>> wf.owner("tester").tags("test")
    >>> wf.job(Job(id="job1", type='NoOp'))
    >>> wf_yaml = wf.to_yaml()
    >>> client = MaestroClient(base_url="http://127.0.0.1:8080", user="tester")
    >>> response = client.push_yaml(wf_yaml)
    >>> print(response)
"""

from .dsl.workflow import Workflow
from .dsl.jobs import Job, Subworkflow, Foreach, While
from .client.client import MaestroClient

__version__ = "0.1.0"

__all__ = [
    "Job",
    "Subworkflow",
    "Foreach",
    "While",
    "Workflow",
    "MaestroClient",
]
