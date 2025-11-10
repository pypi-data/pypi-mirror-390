from datetime import datetime
import logging
import botocore

from ..exceptions import S3PrefixCheckFail


logger = logging.getLogger(__name__)


def check_s3_file_exists(client: botocore.client, bucket: str, file_prefix: str):
    """
    Function to check if a file exists in an S3 Bucket.

    Args:
        client (S3 Client) - Boto3 S3 Client Object

        bucket (str) - Name of the S3 Bucket (`jyablonski-dev`)

        file_prefix (str) - Name of the S3 File (`tables/my-table/my-table-2023-05-25.parquet`)

    Returns:
        None

    Raises:
        S3PrefixCheckFail Error if the file isn't found
    """
    result = client.list_objects_v2(
        Bucket=bucket,
        Prefix=file_prefix,
        MaxKeys=1,
    )
    if "Contents" in result.keys():
        logging.info(f"S3 File Exists for {bucket}/{file_prefix}")
    else:
        raise S3PrefixCheckFail(f"S3 Prefix for {bucket}/{file_prefix} doesn't exist")


def _partition_datetime(dt: datetime, include_day: bool = False) -> dict[str, str]:
    """Internal function to partition a datetime object into year/month/day components.

    Args:
        dt (datetime): The datetime object to partition

        include_day (bool): Whether to include day in the partition. Defaults to False.

    Returns:
        Dict[str, str]: Dictionary with partition keys and zero-padded values
            e.g., {'year': '2024', 'month': '03', 'day': '15'}
    """
    partitions = {
        "year": str(dt.year),
        "month": str(dt.month).zfill(2),
    }

    if include_day:
        partitions["day"] = str(dt.day).zfill(2)

    return partitions
