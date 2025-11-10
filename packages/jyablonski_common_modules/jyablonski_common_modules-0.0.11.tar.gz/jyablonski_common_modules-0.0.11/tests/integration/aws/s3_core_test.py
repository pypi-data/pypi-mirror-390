from datetime import datetime

import boto3
from moto import mock_aws
import pytest

from jyablonski_common_modules.aws.s3.core import (
    check_s3_file_exists,
    _partition_datetime,
)
from jyablonski_common_modules.aws.exceptions import S3PrefixCheckFail


@mock_aws
def test_check_s3_file_exists():
    conn = boto3.client("s3", region_name="us-east-1")
    bucket_name = "jyablonski_fake_bucket"

    conn.create_bucket(Bucket=bucket_name)
    conn.put_object(Bucket=bucket_name, Key=f"{bucket_name}-file.txt", Body="zzz")

    # assert it can successfully check a file
    assert (
        check_s3_file_exists(
            client=conn,
            bucket=bucket_name,
            file_prefix=f"{bucket_name}-file.txt",
        )
        is None
    )

    # assert it raises a failure when it checks a file that doesn't exist
    with pytest.raises(S3PrefixCheckFail):
        check_s3_file_exists(
            client=conn,
            bucket=bucket_name,
            file_prefix="my-fake-ass-file-yo.txt",
        )


def test_partition_datetime_without_day():
    # Test basic year/month partitioning
    dt = datetime(2024, 3, 15, 10, 30, 45)
    result = _partition_datetime(dt, include_day=False)

    assert result == {"year": "2024", "month": "03"}
    assert isinstance(result, dict)
    assert len(result) == 2


def test_partition_datetime_with_day():
    # Test year/month/day partitioning
    dt = datetime(2024, 3, 15, 10, 30, 45)
    result = _partition_datetime(dt, include_day=True)

    assert result == {"year": "2024", "month": "03", "day": "15"}
    assert isinstance(result, dict)
    assert len(result) == 3


def test_partition_datetime_zero_padding():
    # Test that single-digit months and days are zero-padded
    dt = datetime(2024, 1, 5, 10, 30, 45)
    result = _partition_datetime(dt, include_day=True)

    assert result == {"year": "2024", "month": "01", "day": "05"}
    assert result["month"] == "01"  # Not "1"
    assert result["day"] == "05"  # Not "5"


def test_partition_datetime_double_digit():
    # Test that double-digit months and days work correctly
    dt = datetime(2024, 12, 25, 10, 30, 45)
    result = _partition_datetime(dt, include_day=True)

    assert result == {"year": "2024", "month": "12", "day": "25"}


def test_partition_datetime_edge_cases():
    # Test edge cases like January 1st and December 31st
    dt_jan = datetime(2024, 1, 1)
    result_jan = _partition_datetime(dt_jan, include_day=True)
    assert result_jan == {"year": "2024", "month": "01", "day": "01"}

    dt_dec = datetime(2024, 12, 31)
    result_dec = _partition_datetime(dt_dec, include_day=True)
    assert result_dec == {"year": "2024", "month": "12", "day": "31"}
