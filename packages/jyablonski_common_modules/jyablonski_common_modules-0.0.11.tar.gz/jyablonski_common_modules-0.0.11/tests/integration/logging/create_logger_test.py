import logging
import os

from jyablonski_common_modules.logging import create_logger


def test_create_logger_with_log_file(caplog):
    log_file_location = "test.log_fake"
    log_msg = "This is a test log."

    # create logger with a log file
    logger = create_logger(log_file=log_file_location)

    # verify that the log file exists
    assert os.path.exists(log_file_location)

    # Ensure the logger writes to the console
    with caplog.at_level(logging.INFO):
        logger.info(log_msg)
        assert log_msg in caplog.text

    # clean up
    os.remove(log_file_location)


def test_create_logger_without_log_file(caplog):
    # Test logger without log file
    logger = create_logger()
    log_msg = "Console log test."

    # Ensure the logger writes to the console
    with caplog.at_level(logging.INFO):
        logger.info(log_msg)
        assert log_msg in caplog.text

    # Verify that no log file is created
    log_files = [file for file in os.listdir() if file.endswith(".log")]
    assert not log_files
