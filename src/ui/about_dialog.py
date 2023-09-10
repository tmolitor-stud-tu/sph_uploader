import sys
import os
import platformdirs
from PyQt5 import QtWidgets, uic, QtGui

from utils import catch_exceptions, PLATFORM_ARGS

import logging
logger = logging.getLogger(__name__)

class AboutDialog(QtWidgets.QDialog):
    @catch_exceptions(logger=logger)
    def __init__(self):
        super().__init__()
        
        # load qt ui definition file from same directory and named exactly like this file, but having extension ".ui"
        uic.loadUi(os.path.join(os.path.dirname(__file__), os.path.splitext(__file__)[0]+".ui"), self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "..", "art", "icon.png")))
        
        self.uiLabel_configDir.setText(platformdirs.user_data_dir(*PLATFORM_ARGS, roaming=True))
        self.uiLabel_loggerDir.setText(platformdirs.user_log_dir(*PLATFORM_ARGS))
