import logging
import random
from typing import Dict, Any, List

import pyodbc
import psycopg

logger = logging.getLogger(__name__)

TABLE_KEY_MAP = {
    # source_table -> (target_table, pk_source, pk_target)
    "Customers": ("customers", "CustomerID", "customer_id"),
    "Orders": ("orders", "OrderID", "order_id"),
    "OrderItems": ("order_items", "OrderItemID", "order_item_id"),
    "Products": ("products", "ProductID", "product_id"),
}


def _pick_random_ids(cur: pyodbc.Cursor, table: str, pk_col: str, sample_size: int) -> List[Any]:
    cur.execute(f"SELECT [{pk_col}] FROM dbo.[{table}];")
    ids = [row[0] for row in cur.fetchall()]
    if not ids:
        return []
    if len(ids) <= sample_size:
        return ids
    return random.sample(ids, sample_size)


def validate_samples(
    sqlserver_conn: str,
    postgres_conn: str,
    sample_size: int = 3,
) -> bool:
    """
    Randomly sample PKs on SQL Server and compare full rows with Postgres.
    """
    ok = True

    with pyodbc.connect(sqlserver_conn) as src_conn, psycopg.connect(postgres_conn) as tgt_conn:
        src_cur = src_conn.cursor()
        tgt_cur = tgt_conn.cursor()

        for src_table, (tgt_table, pk_src, pk_tgt) in TABLE_KEY_MAP.items():
            ids = _pick_random_ids(src_cur, src_table, pk_src, sample_size)
            if not ids:
                logger.info("Sampling: table %s has no rows, skipping", src_table)
                continue

            for pk_val in ids:
                # fetch source row
                src_cur.execute(f"SELECT * FROM dbo.[{src_table}] WHERE [{pk_src}] = ?", pk_val)
                src_row = src_cur.fetchone()

                # fetch target row
                tgt_cur.execute(
                    f'SELECT * FROM {tgt_table} WHERE {pk_tgt} = %s',
                    (pk_val,),
                )
                tgt_row = tgt_cur.fetchone()

                if src_row is None or tgt_row is None:
                    ok = False
                    logger.warning(
                        "Sampling mismatch for %s id=%s: src_row=%s tgt_row=%s",
                        src_table, pk_val, bool(src_row), bool(tgt_row),
                    )
                    continue

                # compare by position (schemas already aligned in bulk_migrate)
                if tuple(src_row) != tuple(tgt_row):
                    ok = False
                    logger.warning(
                        "Sampling mismatch for %s id=%s: src=%s tgt=%s",
                        src_table, pk_val, tuple(src_row), tuple(tgt_row),
                    )

    return ok
