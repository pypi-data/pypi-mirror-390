# Always available
from .core import check_s3_file_exists, _partition_datetime

# Conditionally export parquet functions
try:
    from .parquet import write_parquet_to_s3, HAS_PARQUET_SUPPORT
except ImportError:
    HAS_PARQUET_SUPPORT = False
    write_parquet_to_s3 = None

__all__ = [
    "check_s3_file_exists",
    "_partition_datetime",
    "write_parquet_to_s3",
    "HAS_PARQUET_SUPPORT",
]
