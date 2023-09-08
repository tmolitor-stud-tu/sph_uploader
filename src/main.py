#!/usr/bin/env python3

import sys
import os
import signal
import shutil
import argparse
from PyQt5 import QtWidgets

# prepare top level dirs and copy over logger.json
try:
    os.mkdir(os.path.join(os.path.dirname(sys.argv[0]), "conf"))
    shutil.copy2(os.path.join(os.path.dirname(__file__), "conf", "logger.json"), os.path.join(os.path.dirname(sys.argv[0]), "conf", "logger.json"))
except FileExistsError:
    pass
try:
    os.mkdir(os.path.join(os.path.dirname(sys.argv[0]), "log"))
except FileExistsError:
    pass

# parse commandline
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="SPH Uploader")
parser.add_argument("--log", metavar='LOGLEVEL', help="Loglevel to log", default="INFO")
args = parser.parse_args()

import json, logging, logging.config
with open(os.path.join(os.path.dirname(sys.argv[0]), "conf", "logger.json"), 'r') as logging_configuration_file:
    logger_config = json.load(logging_configuration_file)
logger_config["handlers"]["stderr"]["level"] = args.log
logging.config.dictConfig(logger_config)
logger = logging.getLogger(__name__)
logger.info('Logger configured...')


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
