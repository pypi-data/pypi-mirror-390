import pytest
from jyablonski_common_modules.aws import (
    S3PrefixCheckFail,
    get_secret_value,
    get_ssm_parameter,
)
from jyablonski_common_modules.aws.s3 import check_s3_file_exists

try:
    from jyablonski_common_modules.aws.s3 import write_parquet_to_s3

    HAS_PARQUET = True
except ImportError:
    write_parquet_to_s3 = None  # Define it as None if import fails
    HAS_PARQUET = False

from jyablonski_common_modules.general import (
    check_feature_flag,
    construct_date_partition,
    get_leading_zeroes,
    get_feature_flags,
)
from jyablonski_common_modules.logging import create_logger
from jyablonski_common_modules.sql import create_sql_engine, write_to_sql_upsert


# List of core functions/classes that should always be available
@pytest.mark.parametrize(
    "obj, name",
    [
        (create_sql_engine, "create_sql_engine"),
        (write_to_sql_upsert, "write_to_sql_upsert"),
        (S3PrefixCheckFail, "S3PrefixCheckFail"),
        (get_secret_value, "get_secret_value"),
        (get_ssm_parameter, "get_ssm_parameter"),
        (check_s3_file_exists, "check_s3_file_exists"),
        (check_feature_flag, "check_feature_flag"),
        (construct_date_partition, "construct_date_partition"),
        (get_leading_zeroes, "get_leading_zeroes"),
        (get_feature_flags, "get_feature_flags"),
        (create_logger, "create_logger"),
    ],
)
def test_imports_are_callable(obj, name):
    assert callable(obj), f"{name} should be callable"


# Test optional parquet function
@pytest.mark.skipif(not HAS_PARQUET, reason="awswrangler not installed")
def test_parquet_import_is_callable():
    assert callable(write_parquet_to_s3), "write_parquet_to_s3 should be callable"


def test_parquet_support_flag():
    """Test that HAS_PARQUET flag matches actual import capability."""
    if HAS_PARQUET:
        assert write_parquet_to_s3 is not None
        assert callable(write_parquet_to_s3)
    else:
        # If parquet support is not available, it should be None
        assert write_parquet_to_s3 is None
