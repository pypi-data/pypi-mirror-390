import logging


def create_logger(
    log_file: str | None = None, date_format: str = "%Y-%m-%d %I:%M:%S %p"
):
    """
    Function to create a logger that writes to both STDOUT and a log file if specified.

    Args:
        log_file (str | None): Optional parameter to specify a Log File for logs to be
            written out to

        date_format (str): The format of the date in the log message.

    Returns:
        Python Logger object which writes Logs out as specified

    """
    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(message)s",
        datefmt=date_format,
        handlers=handlers,
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    return logger
