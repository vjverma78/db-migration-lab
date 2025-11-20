"""
Row Count Validation: SQL Server -> PostgreSQL
"""

import psycopg
import pyodbc
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

# SQL Server connection (source)
SOURCE_CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=AdventureWorksLite;"
    "UID=sa;"
    "PWD=MigrationLab123!;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

# PostgreSQL connection (target)
TARGET_CONN = {
    "host": "localhost",
    "port": 5432,
    "dbname": "migration_target",
    "user": "postgres",
    "password": "MigrationLab123!",
}

TABLES = ["Customers", "Products", "Orders", "OrderItems"]

TABLE_NAME_MAP = {
    "Customers": "customers",
    "Products": "products",
    "Orders": "orders",
    "OrderItems": "order_items",  # important: underscore here
}

def get_row_counts():
    results = []

    # Connect to SQL Server
    src_conn = pyodbc.connect(SOURCE_CONN_STR)
    src_cur = src_conn.cursor()

    # Connect to PostgreSQL
    tgt_conn = psycopg.connect(**TARGET_CONN)
    tgt_cur = tgt_conn.cursor()

    for table in TABLES:
        # Source count
        src_cur.execute(f"SELECT COUNT(*) FROM {table}")
        src_count = src_cur.fetchone()[0]

        # Target table names are lowercase
        tgt_table = TABLE_NAME_MAP[table]
        tgt_cur.execute(f"SELECT COUNT(*) FROM {tgt_table}")
        tgt_count = tgt_cur.fetchone()[0]

        diff = tgt_count - src_count
        status = "MATCH" if diff == 0 else "MISMATCH"
        color = Fore.GREEN if diff == 0 else Fore.RED

        results.append(
            [
                table,
                src_count,
                tgt_count,
                diff,
                f"{color}{status}{Style.RESET_ALL}",
            ]
        )

    src_cur.close()
    src_conn.close()
    tgt_cur.close()
    tgt_conn.close()

    return results


def main():
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}Row Count Validation Report")
    print(f"{Fore.CYAN}{'='*70}\n")

    results = get_row_counts()

    headers = [
        "Table",
        "Source (SQL Server)",
        "Target (PostgreSQL)",
        "Difference",
        "Status",
    ]
    print(tabulate(results, headers=headers, tablefmt="grid"))

    all_match = all(row[3] == 0 for row in results)

    print(f"\n{Fore.CYAN}{'='*70}")
    if all_match:
        print(f"{Fore.GREEN}✓ All tables match - Migration successful!")
    else:
        print(f"{Fore.RED}✗ Some tables have mismatches - Review required")
    print(f"{Fore.CYAN}{'='*70}\n")


if __name__ == "__main__":
    main()
