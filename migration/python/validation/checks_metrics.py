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


def _agg_postgres(conn_str: str) -> Dict[str, Dict[str, float]]:
    metrics: Dict[str, Dict[str, float]] = {}
    with psycopg.connect(conn_str) as conn:
        cur = conn.cursor()

        # customers.customerid
        cur.execute("""
            SELECT COUNT(customerid), SUM(customerid), MAX(customerid)
            FROM adventureworkslite_dbo.customers;
        """)
        cnt, s, mx = cur.fetchone()
        metrics["customers.customer_id"] = {
            "cnt": float(cnt or 0),
            "sum": float(s or 0),
            "max": float(mx or 0),
        }

        # orders.orderid, orders.totalamount
        cur.execute("""
            SELECT COUNT(orderid), SUM(orderid), MAX(orderid),
                   COUNT(totalamount), SUM(totalamount), MAX(totalamount)
            FROM adventureworkslite_dbo.orders;
        """)
        ocnt, osum, omax, tcnt, tsum, tmax = cur.fetchone()
        metrics["orders.order_id"] = {
            "cnt": float(ocnt or 0),
            "sum": float(osum or 0),
            "max": float(omax or 0),
        }
        metrics["orders.total_amount"] = {
            "cnt": float(tcnt or 0),
            "sum": float(tsum or 0),
            "max": float(tmax or 0),
        }

        # order_items.orderitemid, quantity, unitprice
        cur.execute("""
            SELECT COUNT(orderitemid), SUM(orderitemid), MAX(orderitemid),
                   COUNT(quantity), SUM(quantity), MAX(quantity),
                   COUNT(unitprice), SUM(unitprice), MAX(unitprice)
            FROM adventureworkslite_dbo.orderitems;
        """)
        icnt, isum, imax, qcnt, qsum, qmax, pcnt, psum, pmax = cur.fetchone()
        metrics["order_items.order_item_id"] = {
            "cnt": float(icnt or 0),
            "sum": float(isum or 0),
            "max": float(imax or 0),
        }
        metrics["order_items.quantity"] = {
            "cnt": float(qcnt or 0),
            "sum": float(qsum or 0),
            "max": float(qmax or 0),
        }
        metrics["order_items.unit_price"] = {
            "cnt": float(pcnt or 0),
            "sum": float(psum or 0),
            "max": float(pmax or 0),
        }

        # products.productid, price, stockquantity
        cur.execute("""
            SELECT COUNT(productid), SUM(productid), MAX(productid),
                   COUNT(price), SUM(price), MAX(price),
                   COUNT(stockquantity), SUM(stockquantity), MAX(stockquantity)
            FROM adventureworkslite_dbo.products;
        """)
        pcnt2, psum2, pmax2, prcnt, prsum, prmax, scnt, ssum, smax = cur.fetchone()
        metrics["products.product_id"] = {
            "cnt": float(pcnt2 or 0),
            "sum": float(psum2 or 0),
            "max": float(pmax2 or 0),
        }
        metrics["products.price"] = {
            "cnt": float(prcnt or 0),
            "sum": float(prsum or 0),
            "max": float(prmax or 0),
        }
        metrics["products.stock_quantity"] = {
            "cnt": float(scnt or 0),
            "sum": float(ssum or 0),
            "max": float(smax or 0),
        }

    return metrics


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
