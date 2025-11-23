import logging
from typing import Dict, Tuple

import pyodbc
import psycopg

logger = logging.getLogger(__name__)

# target table -> target numeric cols
NUMERIC_COLUMNS = {
    "customers": ["customer_id"],
    "orders": ["order_id", "total_amount"],
    "order_items": ["order_item_id", "quantity", "unit_price"],
    "products": ["product_id", "price", "stock_quantity"],
}

# explicit source mapping (SQL Server)
SRC_TABLE_MAP = {
    "customers": "Customers",
    "orders": "Orders",
    "order_items": "OrderItems",
    "products": "Products",
}

SRC_COL_MAP = {
    # target_col -> source_col
    "customer_id": "CustomerID",
    "order_id": "OrderID",
    "total_amount": "TotalAmount",
    "order_item_id": "OrderItemID",
    "quantity": "Quantity",
    "unit_price": "UnitPrice",
    "price": "Price",
    "stock_quantity": "StockQuantity",
    "product_id": "ProductID",
}


def _agg_sqlserver(conn_str: str) -> Dict[Tuple[str, str], Tuple[float, float, float]]:
    """
    Return {(target_table, target_col): (count, sum, max)} using source SQL Server data.
    """
    result = {}
    with pyodbc.connect(conn_str) as conn:
        cur = conn.cursor()
        for tgt_tbl, cols in NUMERIC_COLUMNS.items():
            src_tbl = SRC_TABLE_MAP[tgt_tbl]
            for tgt_col in cols:
                src_col = SRC_COL_MAP[tgt_col]
                cur.execute(f"""
                    SELECT COUNT([{src_col}]), SUM(CAST([{src_col}] AS FLOAT)), MAX(CAST([{src_col}] AS FLOAT))
                    FROM dbo.[{src_tbl}];
                """)
                cnt, s, mx = cur.fetchone()
                result[(tgt_tbl, tgt_col)] = (float(cnt or 0), float(s or 0), float(mx or 0))
    return result


def _agg_postgres(conn_str: str) -> Dict[str, float]:
    with psycopg.connect(conn_str) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(c.customerid)              AS customers_count,
                COALESCE(SUM(o.totalamount), 0)  AS total_revenue,
                COALESCE(AVG(o.totalamount), 0)  AS avg_order_value
            FROM adventureworkslite_dbo.customers c
            LEFT JOIN adventureworkslite_dbo.orders o
                ON o.customerid = c.customerid;
        """)
        customers_count, total_revenue, avg_order_value = cur.fetchone()
        return {
            "customers_count": customers_count,
            "total_revenue": float(total_revenue),
            "avg_order_value": float(avg_order_value),
        }



def validate_metrics(sqlserver_conn: str, postgres_conn: str, tol: float = 1e-6) -> bool:
    src = _agg_sqlserver(sqlserver_conn)
    tgt = _agg_postgres(postgres_conn)

    ok = True
    for key, (src_cnt, src_sum, src_max) in src.items():
        tgt_cnt, tgt_sum, tgt_max = tgt.get(key, (0.0, 0.0, 0.0))
        tbl, col = key

        if (
            abs(src_cnt - tgt_cnt) > tol
            or abs(src_sum - tgt_sum) > tol
            or abs(src_max - tgt_max) > tol
        ):
            ok = False
            logger.warning(
                "Metric mismatch %s.%s: "
                "src(cnt=%s,sum=%s,max=%s) tgt(cnt=%s,sum=%s,max=%s)",
                tbl, col,
                src_cnt, src_sum, src_max,
                tgt_cnt, tgt_sum, tgt_max,
            )
    return ok
