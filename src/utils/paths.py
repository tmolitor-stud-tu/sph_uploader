import os
import platformdirs

from .constants import PLATFORM_ARGS

import logging
logger = logging.getLogger(__name__)

def get_art_path():
    # path usable from pyinstaller
    art = os.path.join(os.path.dirname(__file__), "..", "art")
    if os.path.isdir(art):
        return art
    # path usable from src dir
    return os.path.join(os.path.dirname(__file__), "..", "..", "art")

def user_data_dir():
    return platformdirs.user_data_dir(*PLATFORM_ARGS, roaming=True)

def user_log_dir():
    return platformdirs.user_log_dir(*PLATFORM_ARGS)
