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



import os
import datetime

class ChatLogger:
    def __init__(self, log_directory):
        self.log_directory = log_directory
        self._setup_logger()

    def _setup_logger(self):
        log_filename = self._get_log_filename()
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, force= True, filemode='w',
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def _get_log_filename(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        return os.path.join(self.log_directory, f"{date_str}.log")

    def log_message(self, user_message, bot_response, similarity_search, token):
        logging.info(f"User: {user_message}")
        logging.info(f"Token: {token}")
        for index, value in enumerate(similarity_search):
            logging.info("Pinecone similarity {}: {}".format(index+1,value.replace('\t','').replace('\n','')))
        logging.info(f"Bot: {bot_response}")
        logging.info("=" * 20)