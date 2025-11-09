"""Python command line interface (cli) for Maestro workflow orchestrator."""

from __future__ import annotations

import argparse
import json

from maestro.client.client import MaestroClient


def push_command(args: argparse.Namespace) -> None:
    """Push a workflow yaml file to maestro server."""
    client = MaestroClient(base_url=args.base_url, user=args.user)
    resp = client.push(args.yaml_file)
    print(json.dumps(resp, indent=2))


def validate_command(args: argparse.Namespace) -> None:
    """Validate a workflow yaml file."""
    client = MaestroClient(base_url=args.base_url, user=args.user)
    resp = client.validate(args.yaml_file)
    print(json.dumps(resp, indent=2))


def start_command(args: argparse.Namespace) -> None:
    if args.params is None:
        run_params = None
    else:
        run_params = json.loads(args.params)

    if args.initiator is None:
        initiator = None
    else:
        initiator = json.loads(args.initiator)

    client = MaestroClient(base_url=args.base_url, user=args.user)
    resp = client.start(workflow_id=args.workflow_id, version=args.version,
                        initiator=initiator, run_params=run_params)
    print(json.dumps(resp, indent=2))


def stop_command(args: argparse.Namespace) -> None:
    if args.instance_id is None:
        instance_id = None
    else:
        instance_id = int(args.instance_id)
    client = MaestroClient(base_url=args.base_url, user=args.user)
    resp = client.stop(workflow_id=args.workflow_id, instance_id=instance_id, step_id=args.step_id)
    print(json.dumps(resp, indent=2))


def get_workflow_command(args: argparse.Namespace) -> None:
    client = MaestroClient(base_url=args.base_url, user=args.user)
    resp = client.get_workflow(workflow_id=args.workflow_id, version=args.version)
    print(json.dumps(resp, indent=2))


def get_instance_command(args: argparse.Namespace) -> None:
    instance_id = int(args.instance_id)
    client = MaestroClient(base_url=args.base_url, user=args.user)
    resp = client.get_instance(workflow_id=args.workflow_id, instance_id=instance_id, step_id=args.step_id)
    print(json.dumps(resp, indent=2))


def cli() -> None:
    """Main CLI entry point. """
    parser = argparse.ArgumentParser(
        prog="maestro",
        description="Maestro command line interface for interacting with Maestro workflow orchestrator",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8080",
        help="Maestro workflow orchestrator server base URL",
    )
    parser.add_argument(
        "--user",
        default="cli-user",
        help="User name for API requests",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    push_parser = subparsers.add_parser(name="push",
                                        help="Push a workflow yaml file to Maestro workflow orchestrator server")
    push_parser.add_argument("yaml_file", help="Path to the workflow yaml file")
    push_parser.set_defaults(func=push_command)

    validate_parser = subparsers.add_parser(name="validate",
                                            help="Validate a workflow yaml file")
    validate_parser.add_argument("yaml_file", help="Path to the workflow yaml file")
    validate_parser.set_defaults(func=validate_command)

    start_parser = subparsers.add_parser(name="start",
                                         help="Start a workflow instance")
    start_parser.add_argument("workflow_id", help="workflow id to start")
    start_parser.add_argument(
        "--version",
        default="default",
        help="Workflow version to execute",
    )
    start_parser.add_argument(
        "--initiator",
        help='Workflow version to execute (e.g. \'{"type": "manual"}\'',
    )
    start_parser.add_argument(
        "--params",
        help='Runtime params in Maestro param JSON format (e.g. \'{"foo": {"value": "bar", "type": "STRING"}}\'',
    )
    start_parser.set_defaults(func=start_command)

    stop_parser = subparsers.add_parser(name="stop",
                                        help="Stop workflow or step execution(s)")
    stop_parser.add_argument("workflow_id", help="workflow id to stop its workflow instances")
    stop_parser.add_argument(
        "instance_id",
        nargs='?',
        help="Workflow instance id to stop it",
    )
    stop_parser.add_argument(
        "step_id",
        nargs='?',
        help="Workflow step id to stop it",
    )
    stop_parser.set_defaults(func=stop_command)

    get_workflow_parser = subparsers.add_parser(name="get-workflow",
                                                help="Get a workflow definition in Maestro JSON format")
    get_workflow_parser.add_argument("workflow_id", help="workflow id to get its definition")
    get_workflow_parser.add_argument(
        "--version",
        default="default",
        help="Workflow version to get its definition",
    )
    get_workflow_parser.set_defaults(func=get_workflow_command)

    get_instance_parser = subparsers.add_parser(name="get-instance",
                                                help="Get a workflow instance or step instance in Maestro JSON format")
    get_instance_parser.add_argument("workflow_id", help="workflow id to get its instance data")
    get_instance_parser.add_argument(
        "instance_id",
        help="Workflow instance id to get its instance data",
    )
    get_instance_parser.add_argument(
        "step_id",
        nargs='?',
        help="Workflow step id to get its step instance data",
    )
    get_instance_parser.set_defaults(func=get_instance_command)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    cli()
