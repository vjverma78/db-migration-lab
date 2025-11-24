import json
import os
from pathlib import Path

import boto3


BUCKET_NAME = os.getenv("MIGRATION_REPORT_BUCKET", "migration-validation-reports")
REPORT_PATH = Path("validation-report.json")


def main() -> None:
    if not REPORT_PATH.exists():
        print(f"Validation report not found at {REPORT_PATH}, skipping upload")
        return

    # LocalStack endpoint (works locally and in GitHub Actions)
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    key = "dev/" + REPORT_PATH.name
    print(f"Uploading {REPORT_PATH} to s3://{BUCKET_NAME}/{key}")

    with REPORT_PATH.open("rb") as f:
        s3.upload_fileobj(f, BUCKET_NAME, key)

    print("Upload complete")


if __name__ == "__main__":
    main()
