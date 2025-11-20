"""
Database Migration Lab - Connectivity Check Script
Tests connections to all source and target databases
"""

import sys
from colorama import init, Fore, Style
import psycopg
import pyodbc
#import cx_Oracle
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

# Initialize colorama for Windows
init(autoreset=True)

# Connection configurations
CONNECTIONS = {
    "postgresql": {
        "host": "localhost",
        "port": 5432,
        "database": "migration_target",
        "user": "postgres",
        "password": "MigrationLab123!"
    },
    "sqlserver": {
        "server": "localhost",
        "port": 1433,
        "database": "master",
        "user": "sa",
        "password": "MigrationLab123!"
    },
    # "oracle": {
    #     "host": "localhost",
    #     "port": 1521,
    #     "service": "XEPDB1",
    #     "user": "system",
    #     "password": "MigrationLab123!"
    # },
    "kafka": {
        "bootstrap_servers": "localhost:29092"
    }
}


def test_postgresql():
    """Test PostgreSQL connection"""
    try:
        config = CONNECTIONS["postgresql"]
        conn = psycopg.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["database"],
            user=config["user"],
            password=config["password"]
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"{Fore.GREEN}✓ PostgreSQL: Connected successfully")
        print(f"  {Style.DIM}Version: {version.split(',')[0]}")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ PostgreSQL: Connection failed")
        print(f"  {Style.DIM}Error: {str(e)}")
        return False


def test_sqlserver():
    """Test SQL Server connection"""
    try:
        config = CONNECTIONS["sqlserver"]
        # Try ODBC Driver 17 for SQL Server
        conn_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['server']},{config['port']};"
            f"DATABASE={config['database']};"
            f"UID={config['user']};"
            f"PWD={config['password']}"
        )
        conn = pyodbc.connect(conn_string, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION;")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"{Fore.GREEN}✓ SQL Server: Connected successfully")
        print(f"  {Style.DIM}Version: {version.split('-')[0].strip()}")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ SQL Server: Connection failed")
        print(f"  {Style.DIM}Error: {str(e)}")
        print(f"  {Style.DIM}Tip: Ensure ODBC Driver 17 is installed or container is running")
        return False


# def test_oracle():
#     """Test Oracle connection"""
#     try:
#         config = CONNECTIONS["oracle"]
#         dsn = cx_Oracle.makedsn(
#             config["host"],
#             config["port"],
#             service_name=config["service"]
#         )
#         conn = cx_Oracle.connect(
#             user=config["user"],
#             password=config["password"],
#             dsn=dsn
#         )
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM v$version WHERE banner LIKE 'Oracle%'")
#         version = cursor.fetchone()[0]
#         cursor.close()
#         conn.close()
#         print(f"{Fore.GREEN}✓ Oracle: Connected successfully")
#         print(f"  {Style.DIM}Version: {version}")
#         return True
#     except Exception as e:
#         print(f"{Fore.RED}✗ Oracle: Connection failed")
#         print(f"  {Style.DIM}Error: {str(e)}")
#         return False


def test_kafka():
    """Test Kafka connection"""
    try:
        config = CONNECTIONS["kafka"]
        # Quick connection test - will fail fast if Kafka is down
        consumer = KafkaConsumer(
            bootstrap_servers=config["bootstrap_servers"],
            consumer_timeout_ms=5000,
            request_timeout_ms=5000
        )
        consumer.close()
        print(f"{Fore.GREEN}✓ Kafka: Connected successfully")
        print(f"  {Style.DIM}Broker: {config['bootstrap_servers']}")
        return True
    except NoBrokersAvailable:
        print(f"{Fore.RED}✗ Kafka: No brokers available")
        print(f"  {Style.DIM}Ensure Kafka container is running")
        return False
    except Exception as e:
        print(f"{Fore.RED}✗ Kafka: Connection failed")
        print(f"  {Style.DIM}Error: {str(e)}")
        return False


def main():
    """Main connectivity check"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Database Migration Lab - Connectivity Check")
    print(f"{Fore.CYAN}{'='*60}\n")

    results = {
        "PostgreSQL": test_postgresql(),
        "SQL Server": test_sqlserver(),
        # "Oracle": test_oracle(),
        "Kafka": test_kafka()
    }

    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Summary")
    print(f"{Fore.CYAN}{'='*60}\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for service, status in results.items():
        symbol = "✓" if status else "✗"
        color = Fore.GREEN if status else Fore.RED
        print(f"{color}{symbol} {service}")

    print(f"\n{Fore.CYAN}Results: {passed}/{total} services connected successfully\n")

    if passed == total:
        print(f"{Fore.GREEN}✓ All systems ready for migration lab!\n")
        return 0
    else:
        print(f"{Fore.YELLOW}⚠ Some services failed connectivity check.")
        print(f"{Fore.YELLOW}  Review the errors above and ensure all Docker containers are running.")
        print(f"{Fore.YELLOW}  Run: docker-compose ps\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
