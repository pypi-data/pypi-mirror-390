from jyablonski_common_modules.logging import create_os_logger


def test_create_os_logger():
    index_name = "fake_index"
    endpoint = "my_fake_endpoint"
    logger = create_os_logger(index=index_name, host_endpoint=endpoint,)
    logger.info(f"hi")

    assert 1 == 1
