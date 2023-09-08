import functools
import sys
import threading
import _thread
import logging
from PyQt5 import QtWidgets

# see https://stackoverflow.com/a/16068850
def catch_exceptions(exception=Exception, logger=logging.getLogger(__name__)):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as err:
                logger.exception("Exception in thread/pyqt callback!")
                QtWidgets.QMessageBox.critical(None, "Fatal Error!", "%s: %s" % (str(type(err).__name__), str(err)))
                
                logger.error("Shutting down immediately due to exception!")
                _thread.interrupt_main()
                # if threading.current_thread() is not threading.main_thread():
                #     _thread.interrupt_main()
                # else:
                #     sys.exit(1)
                return None
        return wrapper
    return deco

def display_exceptions(exception=Exception, logger=logging.getLogger(__name__)):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as err:
                logger.exception("Exception in thread/pyqt callback!")
                QtWidgets.QMessageBox.warning(None, str(type(err).__name__), str(err))
                
                #logger.error("Shutting down immediately due to exception!")
                #_thread.interrupt_main()
                # if threading.current_thread() is not threading.main_thread():
                #     _thread.interrupt_main()
                # else:
                #     sys.exit(1)
                return None
        return wrapper
    return deco 
