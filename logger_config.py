import logging


def setup_logger(name) -> logging.Logger:
    FORMAT = '%(asctime)s - %(message)s'
    TIME_FORMAT = '%d-%b-%y %H:%M:%S'

    logging.basicConfig(
        format=FORMAT, datefmt=TIME_FORMAT, level=logging.INFO, filename="api.log"
    )

    logger = logging.getLogger(name)
    return logger


def setup_chat_logger(name) -> logging.Logger:
    # FORMAT = '%(message)s'

    logging.basicConfig(
        level=logging.INFO, filename="api.log"
    )

    logger = logging.getLogger(name)
    return logger

# in any file that import fn setup_logger from the above 'logger_config.py', you can set up local logger like:
# local_logger = setup_logger(__name__)

# local_logger.info(
#     f"I am writing to file {FILENAME}. If that file did not exist, it would be automatically created. Here, you can change me to write about the call to a specific route function etc."
# )