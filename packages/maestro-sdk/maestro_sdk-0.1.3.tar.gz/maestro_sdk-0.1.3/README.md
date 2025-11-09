# maestro-python
Python sdk client library for [Maestro workflow orchestrator](https://github.com/Netflix/maestro).
It has a minimal dependency, only requiring pyyaml.

## Features
 
- Maestro yaml DSL
- Maestro python DSL
- Maestro client
- Maestro command line interface

## Installation

```bash
pip install maestro-sdk
```

Or install maestro sdk from source code:

```bash
git clone https://github.com/jun-he/maestro-python.git
cd maestro-python
pip install -e .
```

## Quick Start

### Creating a workflow

```python
from maestro import Workflow, Job

wf = Workflow(id="test-wf")
wf.owner("tester").tags("test")
wf.job(Job(id="job1", type='NoOp'))
wf_yaml = wf.to_yaml()
```

### Pushing a workflow to Maestro server

```python
from maestro import Workflow, Job, MaestroClient

wf = Workflow(id="test-wf")
wf.owner("tester").tags("test")
wf.job(Job(id="job1", type='NoOp'))
wf_yaml = wf.to_yaml()

client = MaestroClient(base_url="http://127.0.0.1:8080", user="tester")
response = client.push_yaml(wf_yaml)
print(response)
```

### Starting a workflow

```python
from maestro import MaestroClient

client = MaestroClient(base_url="http://127.0.0.1:8080", user="tester")
response = client.start(workflow_id="test-wf", run_params={"foo": {"value": "bar", "type": "STRING"}})
print(response)
```

## Command line interface (CLI)

### Push a workflow

```bash
maestro --base-url http://127.0.0.1:8080 --user tester push sample-wf.yaml
# push the yaml using default base-url and user name
maestro push sample-wf.yaml
```

### Validate a workflow

```bash
maestro --base-url http://127.0.0.1:8080 --user tester validate sample-wf.yaml
# validate the yaml using default base-url and user name
maestro validate sample-wf.yaml
```

### Start a workflow definition

```bash
# start sample-wf with default version and none runtime params
maestro --base-url http://127.0.0.1:8080 --user tester start sample-wf.yaml
# start sample-wf with default base-url & user name and runtime params using a specific version 
maestro start sample-wf --version 1 --params '{"foo": {"value": "bar", "type": "STRING"}}'
# start sample-wf with default base-url & user name and runtime params using the latest version
maestro start sample-wf --version latest --params '{"foo": {"value": "bar", "type": "STRING"}}'
```

### Stop workflow or step execution(s)
```bash
maestro --base-url http://127.0.0.1:8080 --user tester start sample-wf.yaml
maestro start sample-wf --version 1 --params '{"foo": {"value": "bar", "type": "STRING"}}'
# stop all workflow instances for workflow_id = sample-wf
maestro stop sample-wf
# stop a workflow instance for workflow_id = sample-wf and instance_id = 1
maestro stop sample-wf 1
# stop a step instance for workflow_id = sample-wf and instance_id = 1 and step_id = job1
maestro stop sample-wf 1 job1
```

### Get a workflow definition
```bash
maestro --base-url http://127.0.0.1:8080 --user tester start sample-wf.yaml
# get workflow definition for version 1
maestro get-workflow sample-wf --version 1
```

### Get a workflow instance or step instance
```bash
maestro --base-url http://127.0.0.1:8080 --user tester start sample-wf.yaml
maestro start sample-wf --version 1 --params '{"foo": {"value": "bar", "type": "STRING"}}'
# get workflow instance for instance id 1
maestro get-instance sample-wf 1
# get workflow step instance for instance id = 1 and step id = job1
maestro get-instance sample-wf 1 job1
```
