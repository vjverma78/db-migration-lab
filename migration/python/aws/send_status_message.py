import json
import os
from pathlib import Path

import boto3


QUEUE_NAME = os.getenv("MIGRATION_STATUS_QUEUE", "migration-status-queue")
REPORT_PATH = Path("validation-report.json")


def main() -> None:
    if REPORT_PATH.exists():
        with REPORT_PATH.open("r", encoding="utf-8") as f:
            report = json.load(f)
        status = "SUCCESS" if report.get("overall_ok") else "FAILED"
        payload = {
            "environment": os.getenv("ENVIRONMENT", "dev"),
            "status": status,
            "rowcount_ok": report.get("rowcount_ok"),
            "metrics_ok": report.get("metrics_ok"),
            "samples_ok": report.get("samples_ok"),
        }
    else:
        payload = {
            "environment": os.getenv("ENVIRONMENT", "dev"),
            "status": "UNKNOWN",
            "rowcount_ok": None,
            "metrics_ok": None,
            "samples_ok": None,
        }

    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

    sqs = boto3.client(
        "sqs",
        endpoint_url=endpoint_url,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    resp = sqs.get_queue_url(QueueName=QUEUE_NAME)
    queue_url = resp["QueueUrl"]

    print(f"Sending status message to {queue_url}: {payload}")

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(payload),
    )

    print("Status message sent")


if __name__ == "__main__":
    main()
