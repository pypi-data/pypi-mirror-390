import datetime
import os
from argparse import ArgumentParser, Namespace, _SubParsersAction
from logging import getLogger
from pathlib import Path
from typing import Any, cast

logger = getLogger(__name__)


def add_subparser(subparsers: "_SubParsersAction[Any]", **kwargs: Any) -> None:
    description = "クエリを実行します。"

    parser = cast(
        ArgumentParser,
        subparsers.add_parser(
            "query",
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
        help="クエリが利用するデータ期間の開始日",
    )
    parser.add_argument(
        "--end-date",
        type=datetime.date.fromisoformat,
        required=True,
        help="クエリが利用するデータ期間の終了日",
    )

    parser.add_argument(
        "--dest-table",
        type=str,
        required=True,
        help="結果の出力対象の bigquery テーブル。 Format: [[{project_id}.]{dataset_id}.]{table_id}",
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
        help="出力ファイル。",
        required=False,
    )

    parser.set_defaults(handler=adsdatahub_query)


def adsdatahub_query(space: Namespace) -> None:
    import adsdatahub
    import pandas as pd
    import pydantic

    class Args(pydantic.BaseModel):
        query_text: str | None
        query_file: Path | None
        start_date: datetime.date
        end_date: datetime.date
        dest_table: str
        customer_id: str
        output: Path | None

    args = Args(**vars(space))

    if args.query_text is not None:
        query = args.query_text
    elif args.query_file is not None:
        query = args.query_file.read_text()
    else:
        raise NotImplementedError("到達不可能です。")

    result = (
        adsdatahub.Client()
        .customer(args.customer_id)
        .query(
            query,
            start_date=args.start_date,
            end_date=args.end_date,
            dest_table=args.dest_table,
        )
    )

    df = cast(pd.DataFrame, result.job.to_dataframe())
    if args.output:
        match args.output.suffix:
            case ".csv":
                df.to_csv(args.output)
            case ".json":
                df.to_json(args.output)
            case _:
                raise ValueError(f"Unsupported file format: {args.output.suffix}")
    else:
        print(df)
