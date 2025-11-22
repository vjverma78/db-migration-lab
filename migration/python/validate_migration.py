import logging
import sys

from validation.config import load_config
from validation.checks_rowcount import validate_rowcounts
from validation.checks_metrics import validate_metrics
from validation.checks_samples import validate_samples

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger("validate_migration")

def main() -> int:
    cfg = load_config()

    logger.info("Starting migration validation...")

    ok_rowcount, details = validate_rowcounts(
        sqlserver_conn=cfg.sqlserver_conn,
        postgres_conn=cfg.postgres_conn,
    )

    for table, (src, tgt) in sorted(details.items()):
        status = "OK" if src == tgt else "MISMATCH"
        logger.info("Table %-20s src=%-6d tgt=%-6d [%s]", table, src, tgt, status)

    ok_metrics = validate_metrics(
        sqlserver_conn=cfg.sqlserver_conn,
        postgres_conn=cfg.postgres_conn,
    )

    ok_samples = validate_samples(
        sqlserver_conn=cfg.sqlserver_conn,
        postgres_conn=cfg.postgres_conn,
        sample_size=3,
    )

    if not ok_rowcount or not ok_metrics or not ok_samples:
        logger.error(
            "Validation FAILED (rowcount_ok=%s metrics_ok=%s samples_ok=%s)",
            ok_rowcount, ok_metrics, ok_samples,
        )
        return 1

    if not ok_rowcount or not ok_metrics:
        logger.error("Validation FAILED (rowcount_ok=%s metrics_ok=%s)", ok_rowcount, ok_metrics)
        return 1

    logger.info("All validations PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
