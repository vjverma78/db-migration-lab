import os
from dataclasses import dataclass

@dataclass
class DbConfig:
    sqlserver_conn: str
    postgres_conn: str
    sample_size: int

def load_config() -> DbConfig:
    sqlserver_conn = os.environ.get(
        "SRC_SQLSERVER_CONN_STR",
        "Driver={ODBC Driver 18 for SQL Server};Server=localhost,1433;Database=AdventureWorksLite;Uid=sa;Pwd=MigrationLab123!;Encrypt=yes;TrustServerCertificate=yes;",
    )
    postgres_conn = os.environ.get(
        "TGT_POSTGRES_CONN_STR",
        "host=localhost port=5432 dbname=migration_target user=postgres password=MigrationLab123!",
    )
    sample_size = int(os.environ.get("VALIDATION_SAMPLE_SIZE", "50"))

    return DbConfig(
        sqlserver_conn=sqlserver_conn,
        postgres_conn=postgres_conn,
        sample_size=sample_size,
    )
