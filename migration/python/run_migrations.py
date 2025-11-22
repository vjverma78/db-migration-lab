import argparse
import logging
import os
import pathlib
import sys

import psycopg


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("run_migrations")


def get_postgres_dsn(env_name: str) -> str:
    """
    Build a DSN for the target Postgres in CI.
    For the dev workflow, we connect to the GitHub Actions postgres service.
    """
    # In CI, the service is exposed on localhost:5432 with user/password from env.
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("DB_DEV_PASSWORD") or os.environ.get("POSTGRES_PASSWORD", "")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    dbname = os.environ.get("POSTGRES_DB", "migration_target")

    if not password:
        logger.warning("No password found in DB_DEV_PASSWORD/POSTGRES_PASSWORD; connecting without password")

    dsn = f"host={host} port={port} dbname={dbname} user={user}"
    if password:
        dsn += f" password={password}"
    return dsn


def apply_sql_file(conn: psycopg.Connection, sql_path: pathlib.Path) -> None:
    logger.info("Applying %s", sql_path)
    sql = sql_path.read_text(encoding="utf-8")
    # Very simple splitter; assumes each file is a single statement or uses plain ';' terminators.
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def apply_directory(conn: psycopg.Connection, source_dir: pathlib.Path) -> None:
    sql_files = sorted(source_dir.rglob("*.sql"))
    if not sql_files:
        logger.info("No .sql files found under %s, nothing to do", source_dir)
        return

    logger.info("Found %d .sql files under %s", len(sql_files), source_dir)

    for sql_file in sql_files:
        apply_sql_file(conn, sql_file)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    parser.add_argument("--phase", required=True, choices=["schema", "data"])
    parser.add_argument("--source", required=True)
    args = parser.parse_args()

    source_dir = pathlib.Path(args.source)
    if not source_dir.exists():
        logger.warning("Source directory %s does not exist, skipping", source_dir)
        return 0

    dsn = get_postgres_dsn(args.env)
    logger.info("Connecting to Postgres with DSN: %s", dsn.replace(password if (password := os.environ.get('DB_DEV_PASSWORD')) else "", "****"))

    try:
        with psycopg.connect(dsn) as conn:
            logger.info("Connected. Applying %s migrations from %s", args.phase, source_dir)
            apply_directory(conn, source_dir)
    except Exception as exc:
        logger.error("Migration failed: %s", exc, exc_info=True)
        return 1

    logger.info("Migrations completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
