import datetime
import os
from argparse import ArgumentParser, Namespace, _SubParsersAction
from logging import getLogger
from pathlib import Path
from typing import Any, cast

logger = getLogger(__name__)


def add_subparser(subparsers: "_SubParsersAction[Any]", **kwargs: Any) -> None:
    description = "クエリを検証します。"
    dummy_desctiption = "queryコマンドと同じ引数を許容するためのダミー引数。"

    parser = cast(
        ArgumentParser,
        subparsers.add_parser(
            "validate",
            description=description,
            help=description,
            **kwargs,
        ),
    )

    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--query-text", type=str, help="クエリ文字列。")
    query_group.add_argument(
        "--query-file",
        type=Path,
        help="クエリファイル。",
    )

    parser.add_argument(
        "--start-date",
        type=datetime.date.fromisoformat,
        required=True,
        help=dummy_desctiption,
    )
    parser.add_argument(
        "--end-date",
        type=datetime.date.fromisoformat,
        required=True,
        help=dummy_desctiption,
    )

    parser.add_argument(
        "--dest-table",
        type=str,
        required=True,
        help=dummy_desctiption,
    )

    parser.add_argument(
        "--customer-id",
        type=str,
        default=os.environ.get("CUSTOMER_ID"),
        required="CUSTOMER_ID" not in os.environ,
        help="クエリを実行するカスタマーID。",
    )

    parser.add_argument(
        "--output-file",
        type=Path,
        required=False,
        help=dummy_desctiption,
    )

    parser.set_defaults(handler=adsdatahub_validate)


def adsdatahub_validate(space: Namespace) -> None:
    import adsdatahub
    import pydantic

    class Args(pydantic.BaseModel):
        query_text: str | None
        query_file: Path | None
        customer_id: str

    args = Args(**vars(space))

    if args.query_text is not None:
        query = args.query_text
    elif args.query_file is not None:
        query = args.query_file.read_text()
    else:
        raise NotImplementedError("到達不可能です。")

    adsdatahub.Client().customer(args.customer_id).validate(query)
    logger.info("クエリの検証に成功しました。")
