import platformdirs

from .constants import PLATFORM_ARGS

import logging
logger = logging.getLogger(__name__)

def user_data_dir():
    return platformdirs.user_data_dir(*PLATFORM_ARGS, roaming=True)

def user_log_dir():
    return platformdirs.user_log_dir(*PLATFORM_ARGS)
