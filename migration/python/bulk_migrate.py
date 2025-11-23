"""
Bulk migrate data: SQL Server -> PostgreSQL
"""

import pyodbc
import psycopg
from colorama import Fore, Style, init

init(autoreset=True)

# SQL Server (source)
SOURCE_CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=AdventureWorksLite;"
    "UID=sa;"
    "PWD=MigrationLab123!;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

# PostgreSQL (target)
TARGET_CONN = {
    "host": "localhost",
    "port": 5432,
    "dbname": "migration_target",
    "user": "postgres",
    "password": "MigrationLab123!",
}

TABLE_PAIRS = [
    (
        "Customers",
        "adventureworkslite_dbo.customers",
        # Drop CustomerID; let Postgres assign customerid
        ["FirstName", "LastName", "Email", "Phone", "CreatedDate", "ModifiedDate"],
        ["firstname", "lastname", "email", "phone", "createddate", "modifieddate"],
    ),
    (
        "Products",
        "adventureworkslite_dbo.products",
        # Drop ProductID
        ["ProductName", "Category", "Price", "StockQuantity", "CreatedDate"],
        ["productname", "category", "price", "stockquantity", "createddate"],
    ),
    (
        "Orders",
        "adventureworkslite_dbo.orders",
        # Drop OrderID
        ["CustomerID", "OrderDate", "TotalAmount", "Status"],
        ["customerid", "orderdate", "totalamount", "status"],
    ),
    (
        "OrderItems",
        "adventureworkslite_dbo.orderitems",
        # Drop OrderItemID
        ["OrderID", "ProductID", "Quantity", "UnitPrice"],
        ["orderid", "productid", "quantity", "unitprice"],
    ),
]


def migrate_table(src_cur, tgt_cur, src_table, tgt_table, src_cols, tgt_cols):
    print(f"{Fore.CYAN}Migrating {src_table} -> {tgt_table}{Style.RESET_ALL}")

    # Fetch all rows from source
    src_col_list = ", ".join(src_cols)
    src_cur.execute(f"SELECT {src_col_list} FROM {src_table}")
    rows = src_cur.fetchall()

    if not rows:
        print(f"  {Fore.YELLOW}No rows to migrate{Style.RESET_ALL}")
        return 0

    # Prepare INSERT for target
    tgt_col_list = ", ".join(tgt_cols)
    placeholders = ", ".join(["%s"] * len(tgt_cols))
    insert_sql = f"INSERT INTO {tgt_table} ({tgt_col_list}) VALUES ({placeholders})"

    # Convert pyodbc Row objects to plain tuples
    data = [tuple(r) for r in rows]

    tgt_cur.executemany(insert_sql, data)
    print(f"  {Fore.GREEN}Inserted {len(data)} rows{Style.RESET_ALL}")
    return len(data)


def main():
    # Connect to source and target
    src_conn = pyodbc.connect(SOURCE_CONN_STR)
    src_cur = src_conn.cursor()

    tgt_conn = psycopg.connect(**TARGET_CONN)
    tgt_conn.autocommit = False
    tgt_cur = tgt_conn.cursor()

    try:
        total = 0
        for src_table, tgt_table, src_cols, tgt_cols in TABLE_PAIRS:
            # Optional: clear target before loading (idempotent runs)
            tgt_cur.execute(f"TRUNCATE TABLE {tgt_table} RESTART IDENTITY CASCADE;")
            inserted = migrate_table(src_cur, tgt_cur, src_table, tgt_table, src_cols, tgt_cols)
            total += inserted

        tgt_conn.commit()
        print(f"\n{Fore.GREEN}Bulk migration completed. Total rows inserted: {total}{Style.RESET_ALL}")
    except Exception as exc:
        tgt_conn.rollback()
        print(f"{Fore.RED}Migration failed: {exc}{Style.RESET_ALL}")
        raise
    finally:
        src_cur.close()
        src_conn.close()
        tgt_cur.close()
        tgt_conn.close()


if __name__ == "__main__":
    main()
