import logging

# Use try-except to conditionally import OpenSearchHandler
try:
    from opensearch_logger import OpenSearchHandler

    def create_os_logger(index: str, host_endpoint: str) -> logging.Logger:
        """
        Logger which writes to both STDOUT as well as an Opensearch Endpoint

        Args:
            index (str): The name of the Opensearch Index that logs will go to.
                It will be automatically created if it doesn't already exist.

            host_endpoint (str): The Endpoint of the Opensearch Cluster

        Returns:
            Python Logger object which writes to both STDOUT and Opensearch
        """
        logging.basicConfig(
            level=logging.INFO,
            format="[%(levelname)s] %(asctime)s %(message)s",
            datefmt="%Y-%m-%d %I:%M:%S %p",
        )
        handler = OpenSearchHandler(
            index_name=index,
            hosts=[f"{host_endpoint}:443"],
            # http_auth=("admin", "admin"),
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger
except ImportError:
    # If `opensearch-logger` is not installed, fallback to a basic logging function
    def create_os_logger(index: str, host_endpoint: str):
        raise RuntimeError(
            "OpenSearch logger is not available. Please install 'opensearch-logger' with the 'es-logging' extra."
        )