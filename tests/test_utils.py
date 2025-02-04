import glob
import json
import os

import duckdb
import sqlite_utils
from pytest_mock import MockerFixture
from querydataio.aws.shared import safe_filename


def duckdb_connect():
    ddb_con = duckdb.connect(":memory:")
    ddb_con.sql("SET disabled_filesystems='HTTPFileSystem';")
    return ddb_con


def download_side_effect(
    mocker: MockerFixture,
    mock_json_filepaths: dict[str, str],
    validate_expected_urls: bool = False,
    expected_urls: list[str] | None = None,
):
    download = mocker.patch("querydataio.aws.shared.download")

    def download_side_effect(
        ddb_con: duckdb.DuckDBPyConnection,
        urls: list[str],
        table_prefix: str,
        print_indent: int = 0,
    ) -> str:
        if validate_expected_urls and urls != expected_urls:
            raise Exception("Update side effect")

        ddb_con.sql(
            f"""
                CREATE OR REPLACE TEMP TABLE __{table_prefix}_downloads AS
                SELECT * FROM read_json_auto('{mock_json_filepaths[table_prefix]}', format='auto');
                """
        )
        return f"__{table_prefix}_downloads"

    download.side_effect = download_side_effect


def assert_query_result(database: str, query: str):
    result = safe_filename(database, query)

    have = json.dumps(sqlite_utils.Database(database).execute_returning_dicts(query))

    with open(result) as file:
        want = json.dumps(json.load(file))

        assert want == have


def clean_test_dbs():
    for file in glob.glob("tests/dbs/*.*"):
        print(f"removing {file}")
        os.remove(file)
