import logging
import sys

from argparse import ArgumentParser, BooleanOptionalAction
from typing import NoReturn

from rich.console import Console as RichConsole
from rich.logging import RichHandler
from rich_argparse import RichHelpFormatter

import adsdatahub_cli

from .commands import query, validate


logger = logging.getLogger(__name__)


class AkagiArgumentParser(ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        raise RuntimeError(message)


class App:
    @classmethod
    def run(cls, args: list[str] | None = None) -> None:
        verbose = "--verbose" in (args or sys.argv)
        try:
            logging.basicConfig(
                format="%(message)s",
                level=logging.INFO,
                handlers=[
                    RichHandler(
                        level=logging.DEBUG,
                        console=RichConsole(stderr=True),
                        show_time=False,
                        show_path=False,
                        rich_tracebacks=True,
                        markup=True,
                    )
                ],
            )
            logging.root.setLevel(logging.DEBUG if verbose else logging.INFO)

            parser = AkagiArgumentParser(
                prog="adh",
                description="Google Ads Data Hub を実行するための CLI ツール。",
                formatter_class=RichHelpFormatter,
            )

            parser.add_argument(
                "--version",
                action="version",
                version=f"[argparse.prog]%(prog)s[/] {adsdatahub_cli.__version__}",
            )

            parser.add_argument(
                "--verbose",
                action=BooleanOptionalAction,
                help="output verbose log.",
            )

            subparser = parser.add_subparsers(
                title="commands",
                metavar="COMMAND",
            )

            query.add_subparser(subparser, formatter_class=parser.formatter_class)
            validate.add_subparser(subparser, formatter_class=parser.formatter_class)

            parser.set_defaults(handler=lambda _: parser.print_help())

            space = parser.parse_args(args)

            if hasattr(space, "handler"):
                space.handler(space)

            else:
                parser.print_help()

        except KeyboardInterrupt:
            print()
            logger.info("Cancelled by user 👋")

            sys.exit(1)

        except Exception as e:
            if verbose:
                logger.exception(e)

            else:
                logger.error(e)

            raise e
