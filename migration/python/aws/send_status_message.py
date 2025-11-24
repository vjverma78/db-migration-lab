import json
import os
from pathlib import Path

import boto3


QUEUE_NAME = os.getenv("MIGRATION_STATUS_QUEUE", "migration-status-queue")
REPORT_PATH = Path("validation-report.json")


def main() -> None:
    # Determine status from report file presence (simple version)
    status = "SUCCESS" if REPORT_PATH.exists() else "UNKNOWN"

    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

    sqs = boto3.client(
        "sqs",
        endpoint_url=endpoint_url,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    # Resolve queue URL
    resp = sqs.get_queue_url(QueueName=QUEUE_NAME)
    queue_url = resp["QueueUrl"]

    body = {
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "status": status,
        "report_path": str(REPORT_PATH),
    }

    print(f"Sending status message to {queue_url}: {body}")

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(body),
    )

    print("Status message sent")


if __name__ == "__main__":
    main()
