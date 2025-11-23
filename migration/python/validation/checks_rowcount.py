import logging
from typing import Dict, Tuple

import pyodbc
import psycopg

logger = logging.getLogger(__name__)

TABLE_MAP = {
    "Customers": "adventureworkslite_dbo.customers",
    "Orders": "adventureworkslite_dbo.orders",
    "OrderItems": "adventureworkslite_dbo.orderitems",
    "Products": "adventureworkslite_dbo.products",
}



def _get_sqlserver_counts(conn_str: str) -> Dict[str, int]:
    counts = {}
    with pyodbc.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.name AS table_name, SUM(p.rows) AS row_count
            FROM sys.tables t
            JOIN sys.partitions p ON t.object_id = p.object_id
            WHERE p.index_id IN (0, 1)
              AND t.schema_id = SCHEMA_ID('dbo')
              AND t.name IN ('Customers','Orders','OrderItems','Products')
            GROUP BY t.name;
        """)
        for name, row_count in cur.fetchall():
            counts[name] = int(row_count)
    return counts


def _get_postgres_counts(conn_str: str) -> Dict[str, int]:
    counts = {}
    with psycopg.connect(conn_str) as conn:
        cur = conn.cursor()
        # We now know exact table names; just count them directly
        for tbl in [
            "adventureworkslite_dbo.customers",
            "adventureworkslite_dbo.orders",
            "adventureworkslite_dbo.orderitems",
            "adventureworkslite_dbo.products",
        ]:
            cur.execute(f"SELECT COUNT(*) FROM {tbl};")
            (row_count,) = cur.fetchone()
            counts[tbl] = int(row_count)
    return counts


def validate_rowcounts(sqlserver_conn: str, postgres_conn: str) -> Tuple[bool, Dict[str, Tuple[int, int]]]:
    """
    Return (ok, details) where details[table] = (src_count, tgt_count),
    using TABLE_MAP to relate SQL Server table names to PostgreSQL names.
    """
    src = _get_sqlserver_counts(sqlserver_conn)
    tgt = _get_postgres_counts(postgres_conn)

    all_ok = True
    details: Dict[str, Tuple[int, int]] = {}

    # Compare mapped tables
    for src_table, src_count in src.items():
        tgt_table = TABLE_MAP.get(src_table)
        tgt_count = tgt.get(tgt_table, 0) if tgt_table else 0
        key = tgt_table or src_table
        details[key] = (src_count, tgt_count)
        if src_count != tgt_count:
            all_ok = False
            logger.warning(
                "Rowcount mismatch src=%s tgt=%s (src_table=%s tgt_table=%s)",
                src_count, tgt_count, src_table, tgt_table,
            )

    # Tables only in Postgres (among mapped targets)
    for tgt_table, tgt_count in tgt.items():
        if tgt_table not in TABLE_MAP.values():
            continue
        if tgt_table not in details:
            details[tgt_table] = (0, tgt_count)
            all_ok = False
            logger.warning("Table only in Postgres: %s tgt=%s src=0", tgt_table, tgt_count)

    return all_ok, details
