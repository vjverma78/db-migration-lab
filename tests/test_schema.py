import os
import psycopg


def _get_conn():
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    dbname = os.environ.get("POSTGRES_DB", "migration_target")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "")

    dsn = f"host={host} port={port} dbname={dbname} user={user}"
    if password:
        dsn += f" password={password}"
    return psycopg.connect(dsn)


def test_core_tables_exist():
    expected = ["customers", "orders", "order_items", "products"]
    with _get_conn() as conn, conn.cursor() as cur:
        for table in expected:
            cur.execute(
                """
                SELECT EXISTS (
                  SELECT 1
                  FROM information_schema.tables
                  WHERE table_schema = 'public'
                    AND table_name = %s
                );
                """,
                (table,),
            )
            exists, = cur.fetchone()
            assert exists, f"Expected table {table} to exist"


def test_orders_columns():
    cols = {
        "order_id",
        "customer_id",
        "order_date",
        "status",
        "total_amount",
    }
    with _get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'orders';
            """
        )
        got = {row[0] for row in cur.fetchall()}
    missing = cols - got
    assert not missing, f"orders missing columns: {missing}"
