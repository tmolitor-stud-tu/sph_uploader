import os
import functools
from PyQt5 import uic

from utils import paths

import logging
logger = logging.getLogger(__name__)

def init_ui(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        obj = args[0]
        if not hasattr(obj, "__class__"):
            raise RuntimeError("Can only load ui onto classes!")
        if not func.__name__ == "__init__":
            raise RuntimeError("Can only decorate __init__ methods!")
        uifile = paths.get_ui_filepath(os.path.splitext(os.path.basename(func.__code__.co_filename))[0]+".ui")
        logger.debug("Loading ui file located at: '%s' onto %s..." % (uifile, obj))
        super(type(obj), obj).__init__()
        uic.loadUi(uifile, obj)
        return func(*args, **kwargs)
    return wrapper
