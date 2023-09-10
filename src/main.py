#!/usr/bin/env python3

import sys
import os
import signal
import shutil
import argparse
from PyQt5 import QtWidgets

from utils import paths

# prepare platform dirs and copy over logger.json
logger_config_file = os.path.join(paths.user_data_dir(), "logger.json")
os.makedirs(paths.user_data_dir(), exist_ok=True)
os.makedirs(paths.user_log_dir(), exist_ok=True)
try:
    shutil.copy2(os.path.join(os.path.dirname(__file__), "conf", "logger.json"), logger_config_file)
except FileExistsError:
    pass

# parse commandline
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="SPH Uploader")
parser.add_argument("--log", metavar='LOGLEVEL', help="Loglevel to log", default="INFO")
args = parser.parse_args()

import json, logging, logging.config
with open(logger_config_file, 'r') as logging_configuration_file:
    logger_config = json.load(logging_configuration_file)
logger_config["handlers"]["debugFile"]["filename"] = os.path.join(paths.user_log_dir(), "debug.log")
logger_config["handlers"]["file"]["filename"] = os.path.join(paths.user_log_dir(), "info.log")
logger_config["handlers"]["stderr"]["level"] = args.log
logging.config.dictConfig(logger_config)
logger = logging.getLogger(__name__)
logger.info("Logger configured via '%s', logging to '%s'..." % (logger_config_file, paths.user_log_dir()))


def sigint_handler(sig, frame):
    logger.warning('Main thread got interrupted, shutting down...')
    os._exit(1)
signal.signal(signal.SIGINT, sigint_handler)

try:
    # initialize qt application
    app = QtWidgets.QApplication(sys.argv)
    from ui import MainWindow
    window = MainWindow()
    window.show()
    
    # ignore pyinstaller splashscreen errors
    try:
        import pyi_splash
        pyi_splash.close()
    except:
        pass
    
    # run qt mainloop
    app.exec_()
except:
    logger.exception("Catched top level exception!")
sys.exit(0)
