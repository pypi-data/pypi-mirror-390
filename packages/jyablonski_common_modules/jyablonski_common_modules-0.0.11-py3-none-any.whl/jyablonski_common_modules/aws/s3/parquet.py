from datetime import datetime
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

from .core import _partition_datetime

try:
    import awswrangler as wr
    import pandas as pd

    HAS_PARQUET_SUPPORT = True
except ImportError:
    HAS_PARQUET_SUPPORT = False


logger = logging.getLogger(__name__)


def write_parquet_to_s3(
    df: "pd.DataFrame",
    bucket: str,
    base_path: str,
    partition_date: datetime,
    include_day_partition: bool = True,
    subfolder: str = "validated",
) -> None:
    """Write a pandas DataFrame to S3 as a parquet file with date-based partitioning.

    The output file name is automatically generated as: {base_path}-{YYYY-mm-dd}.parquet

    Args:
        df (pd.DataFrame): The DataFrame to write to S3

        bucket (str): The S3 bucket name

        base_path (str): The base path within the bucket (e.g., 'boxscores', 'nba_stats').
            Also used as the file name prefix.

        partition_date (datetime): Date to use for partitioning and file naming

        include_day_partition (bool): Whether to include day-level partitioning. Defaults to False.

        subfolder (str): Optional subfolder between base_path and partitions. Defaults to 'validated'.

    Returns:
        None

    Raises:
        ImportError: If awswrangler or pandas are not installed

        Exception: Logs any errors that occur during the write operation

    Example:
        Basic usage with year/month partitioning:

        >>> import pandas as pd
        >>> from datetime import datetime
        >>> from jyablonski_common_modules.aws.s3 import write_parquet_to_s3
        >>>
        >>> df = pd.DataFrame({
        ...     'player': ['LeBron', 'Curry', 'Durant'],
        ...     'points': [27, 30, 28]
        ... })
        >>>
        >>> write_parquet_to_s3(
        ...     df=df,
        ...     bucket='my-sports-data',
        ...     base_path='nba_stats',
        ...     partition_date=datetime(2024, 3, 15)
        ... )
        # Output: s3://my-sports-data/nba_stats/validated/year=2024/month=03/day=15/nba_stats-2024-03-15.parquet

        With day-level partitioning:

        >>> write_parquet_to_s3(
        ...     df=df,
        ...     bucket='my-sports-data',
        ...     base_path='nba_stats',
        ...     partition_date=datetime(2024, 3, 15),
        ...     include_day_partition=False
        ... )
        # Output: s3://my-sports-data/nba_stats/validated/year=2024/month=03/nba_stats-2024-03-15.parquet

        Without subfolder:

        >>> write_parquet_to_s3(
        ...     df=df,
        ...     bucket='my-sports-data',
        ...     base_path='boxscores',
        ...     partition_date=datetime(2024, 3, 15),
        ...     subfolder=''
        ... )
        # Output: s3://my-sports-data/boxscores/year=2024/month=03/day=15/boxscores-2024-03-15.parquet
    """
    if not HAS_PARQUET_SUPPORT:
        raise ImportError(
            "awswrangler and pandas are required for parquet operations. "
            "Install with: pip install jyablonski_common_modules[parquet]"
        )

    if len(df) == 0:
        logging.info(f"Not storing {base_path} to S3 because DataFrame is empty.")
        return

    try:
        partitions = _partition_datetime(
            partition_date, include_day=include_day_partition
        )

        partition_parts = [f"{k}={v}" for k, v in partitions.items()]
        partition_path = "/".join(partition_parts)

        # generate final file name from base_path and partition_date
        date_str = partition_date.strftime("%Y-%m-%d")
        file_name = f"{base_path}-{date_str}.parquet"

        path_components = [f"s3://{bucket}", base_path]

        if subfolder:
            path_components.append(subfolder)

        path_components.append(partition_path)
        path_components.append(file_name)

        s3_path = "/".join(path_components)

        wr.s3.to_parquet(
            df=df,
            path=s3_path,
        )

        logging.info(f"Successfully stored {len(df)} rows to S3: {s3_path}")
        return None

    except Exception as error:
        logging.error(f"Failed to write {base_path} to S3: {error}")
        raise
