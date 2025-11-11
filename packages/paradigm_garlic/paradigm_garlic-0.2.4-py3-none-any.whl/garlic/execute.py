from __future__ import annotations

import typing
from . import env

if typing.TYPE_CHECKING:
    import polars as pl
    from snowflake.connector import SnowflakeConnection
    from snowflake.connector.cursor import SnowflakeCursor


def query(
    sql: str,
    *,
    cursor: SnowflakeCursor | None = None,
    conn: SnowflakeConnection | None = None,
    credentials: dict[str, str | None] | None = None,
    use_batched: bool = True,
) -> pl.DataFrame:
    """
    Execute a SQL query and return results as a Polars DataFrame.

    Args:
        sql: SQL query to execute
        cursor: Optional existing cursor
        conn: Optional existing connection
        credentials: Optional credentials dict
        use_batched: If True, use fetch_arrow_batches() for better performance (default).
                     Benchmarks show 42% faster than fetch_arrow_all() for 6M row datasets.
                     Set to False to use fetch_arrow_all() if needed for compatibility.

    Returns:
        Polars DataFrame with query results

    Performance notes:
        - Connection uses client_fetch_use_mp=True for multi-processed fetching (2025 feature)
        - Connection uses client_prefetch_threads=8 for parallel downloads
        - CLIENT_RESULT_CHUNK_SIZE defaults to 160 (max value, already optimized)
        - Batched fetching provides ~42% speedup (22.2s vs 38.4s for 6M rows)
    """
    import polars as pl
    import snowflake.connector

    if cursor is None:
        cursor = env.get_cursor(conn=conn, credentials=credentials)
    cursor.execute(sql)

    try:
        if use_batched:
            # Batched approach: faster than fetch_arrow_all (42% improvement observed)
            # Converts each batch immediately, allowing better pipelining and cache locality
            batches = []
            for arrow_batch in cursor.fetch_arrow_batches():  # type: ignore
                batches.append(pl.from_arrow(arrow_batch))  # type: ignore
            return pl.concat(batches)
        else:
            # Standard approach: fetch all at once (optimized with multiprocessing)
            arrow_table = cursor.fetch_arrow_all()  # type: ignore
            return pl.from_arrow(arrow_table)  # type: ignore

    except snowflake.connector.errors.NotSupportedError as e:
        if cursor._query_result_format == 'json':
            all_results = cursor.fetchall()
            return pl.DataFrame(all_results)
        raise e


def create_table(table_name: str, select_sql: str) -> str:
    sql = """
        CREATE OR REPLACE TABLE {table_name} AS

        {select_sql}
    """.format(table_name=table_name, select_sql=select_sql)

    return query(sql).item()  # type: ignore
