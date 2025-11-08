import argparse
import subprocess

from rock.cli.command.command import Command as CliCommand
from rock.logger import init_logger

logger = init_logger("rock.cli.service")


class ServiceCommand(CliCommand):
    name = "service"

    def __init__(self):
        super().__init__()

    async def arun(self, args: argparse.Namespace):
        if not args.service_action:
            raise ValueError("Service action is required (run)")

        if args.service_action == "run":
            await self._service_run(args)
        else:
            raise ValueError(f"Unknown service action '{args.service_action}'")

    async def _service_run(self, args: argparse.Namespace):
        """Start gateway service"""
        env = getattr(args, "env", None)

        subprocess.Popen(["admin", "--env", env])

    @staticmethod
    async def add_parser_to(subparsers: argparse._SubParsersAction):
        service_parser = subparsers.add_parser("service", help="Service operations")
        service_subparsers = service_parser.add_subparsers(dest="service_action", help="Service actions")

        # service run
        service_run_parser = service_subparsers.add_parser("run", help="Run gateway service")
        service_run_parser.add_argument("--env", default="local", help="gateway service env")
