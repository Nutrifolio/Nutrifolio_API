from fastapi.requests import Request
from mypy_boto3_s3.client import S3Client


def get_sb_client(request: Request) -> S3Client:
    return request.app.state._sb_client
