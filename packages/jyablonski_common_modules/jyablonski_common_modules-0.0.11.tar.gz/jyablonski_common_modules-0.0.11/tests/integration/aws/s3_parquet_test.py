from datetime import datetime

import boto3
from moto import mock_aws
import pandas as pd
import pytest

try:
    import awswrangler as wr
    from jyablonski_common_modules.aws.s3.parquet import (
        write_parquet_to_s3,
        HAS_PARQUET_SUPPORT,
    )

    SKIP_PARQUET_TESTS = False
except ImportError:
    SKIP_PARQUET_TESTS = True


@pytest.mark.skipif(SKIP_PARQUET_TESTS, reason="awswrangler not installed")
@mock_aws
def test_write_parquet_to_s3_basic():
    """Test basic parquet write with year/month/day partitioning (default)."""
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    df = pd.DataFrame(
        {"id": [1, 2, 3], "name": ["alice", "bob", "charlie"], "value": [100, 200, 300]}
    )

    partition_date = datetime(2024, 3, 15)
    write_parquet_to_s3(
        df=df,
        bucket=bucket_name,
        base_path="test_data",
        partition_date=partition_date,
    )

    # Verify file was written with day partition
    expected_path = "test_data/validated/year=2024/month=03/day=15/"
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=expected_path)

    assert "Contents" in response
    assert len(response["Contents"]) > 0

    file_key = response["Contents"][0]["Key"]
    assert "test_data-2024-03-15.parquet" in file_key

    s3_path = f"s3://{bucket_name}/{expected_path}"
    df_read = wr.s3.read_parquet(path=s3_path)

    assert len(df_read) == 3
    assert list(df_read.columns) == ["id", "name", "value"]
    assert df_read["id"].tolist() == [1, 2, 3]


@pytest.mark.skipif(SKIP_PARQUET_TESTS, reason="awswrangler not installed")
@mock_aws
def test_write_parquet_to_s3_without_day_partition():
    """Test parquet write with only year/month partitioning."""
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    df = pd.DataFrame({"id": [1, 2], "value": [10, 20]})

    partition_date = datetime(2024, 3, 15)
    write_parquet_to_s3(
        df=df,
        bucket=bucket_name,
        base_path="monthly_data",
        partition_date=partition_date,
        include_day_partition=False,
    )

    # Verify the partition structure excludes day
    expected_path = "monthly_data/validated/year=2024/month=03/"
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=expected_path)

    assert "Contents" in response
    assert len(response["Contents"]) > 0

    # Verify file name format
    file_key = response["Contents"][0]["Key"]
    assert "monthly_data-2024-03-15.parquet" in file_key


@pytest.mark.skipif(SKIP_PARQUET_TESTS, reason="awswrangler not installed")
@mock_aws
def test_write_parquet_to_s3_no_subfolder():
    """Test parquet write without subfolder."""
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    df = pd.DataFrame({"col": [1, 2, 3]})

    partition_date = datetime(2024, 5, 1)
    write_parquet_to_s3(
        df=df,
        bucket=bucket_name,
        base_path="data",
        partition_date=partition_date,
        subfolder="",  # No subfolder
    )

    # Verify path doesn't include "validated"
    expected_path = "data/year=2024/month=05/day=01/"
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=expected_path)

    assert "Contents" in response

    # Verify file name format
    file_key = response["Contents"][0]["Key"]
    assert "data-2024-05-01.parquet" in file_key


@pytest.mark.skipif(SKIP_PARQUET_TESTS, reason="awswrangler not installed")
@mock_aws
def test_write_parquet_to_s3_empty_dataframe(caplog):
    """Test that empty DataFrame is not written and logs appropriately."""
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    df = pd.DataFrame()

    # Write empty DataFrame
    with caplog.at_level("INFO"):
        result = write_parquet_to_s3(
            df=df,
            bucket=bucket_name,
            base_path="empty_data",
            partition_date=datetime(2024, 1, 1),
        )

    # Verify nothing was written
    assert result is None
    assert "Not storing empty_data to S3 because DataFrame is empty" in caplog.text

    # Verify no files in S3
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    assert "Contents" not in response


@pytest.mark.skipif(SKIP_PARQUET_TESTS, reason="awswrangler not installed")
@mock_aws
def test_write_parquet_to_s3_zero_padding():
    """Test that single-digit months and days are zero-padded in the path."""
    # Setup
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    df = pd.DataFrame({"col": [1]})

    # Write with single-digit month and day
    partition_date = datetime(2024, 1, 5)
    write_parquet_to_s3(
        df=df,
        bucket=bucket_name,
        base_path="data",
        partition_date=partition_date,
    )

    # Verify zero-padding in path
    expected_path = "data/validated/year=2024/month=01/day=05/"
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=expected_path)

    assert "Contents" in response

    # Verify file name has zero-padded date
    file_key = response["Contents"][0]["Key"]
    assert "data-2024-01-05.parquet" in file_key


@pytest.mark.skipif(SKIP_PARQUET_TESTS, reason="awswrangler not installed")
@mock_aws
def test_write_parquet_to_s3_error_handling():
    """Test error handling when write fails."""
    # Setup - no bucket created, should fail
    df = pd.DataFrame({"col": [1, 2, 3]})

    # This should raise an exception because bucket doesn't exist
    with pytest.raises(Exception):
        write_parquet_to_s3(
            df=df,
            bucket="non-existent-bucket",
            base_path="data",
            partition_date=datetime(2024, 1, 1),
        )


@pytest.mark.skipif(SKIP_PARQUET_TESTS, reason="awswrangler not installed")
@mock_aws
def test_write_parquet_to_s3_file_naming():
    """Test that file names are correctly formatted as base_path-YYYY-mm-dd.parquet."""
    # Setup
    s3_client = boto3.client("s3", region_name="us-east-1")
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    df = pd.DataFrame({"col": [1, 2]})

    # Write file
    partition_date = datetime(2024, 12, 25)
    write_parquet_to_s3(
        df=df,
        bucket=bucket_name,
        base_path="nba_stats",
        partition_date=partition_date,
    )

    # Verify file name follows the expected pattern
    expected_path = "nba_stats/validated/year=2024/month=12/day=25/"
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=expected_path)

    assert "Contents" in response
    file_key = response["Contents"][0]["Key"]
    assert file_key.endswith("nba_stats-2024-12-25.parquet")


@pytest.mark.skipif(SKIP_PARQUET_TESTS, reason="awswrangler not installed")
def test_has_parquet_support():
    """Test that HAS_PARQUET_SUPPORT flag is set correctly."""
    assert HAS_PARQUET_SUPPORT is True
