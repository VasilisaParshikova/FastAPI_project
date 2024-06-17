from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from aiologger.formatters.base import Formatter
from dotenv import load_dotenv
import os

load_dotenv()

if os.environ.get("ENV") == "test":
    LOG_FILE = os.getenv('LOG_FILE_TESTS')
else:
    LOG_FILE = os.getenv('LOG_FILE')


async def get_logger():
    logger = Logger(name='app_logger')

    file_handler = AsyncFileHandler(filename=LOG_FILE)
    formatter = Formatter(fmt="%(name)s - %(module)s - %(funcName)s - %(asctime)s - %(levelname)s: %(message)s")
    file_handler.formatter = formatter
    logger.add_handler(file_handler)

    return logger
