import sys
import os
import platformdirs

from .constants import PLATFORM_ARGS

import logging
logger = logging.getLogger(__name__)

def get_basedir_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def get_ui_filepath(filename):
    return os.path.abspath(os.path.join(get_basedir_path(), "ui", filename))

def get_art_filepath(filename):
    return os.path.abspath(os.path.join(get_basedir_path(), "data", "art", filename))

def user_data_dir():
    return platformdirs.user_data_dir(*PLATFORM_ARGS, roaming=True)

def user_log_dir():
    return platformdirs.user_log_dir(*PLATFORM_ARGS)

def user_cache_dir():
    return platformdirs.user_cache_dir(*PLATFORM_ARGS)
