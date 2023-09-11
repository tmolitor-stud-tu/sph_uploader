import sys
import os
import platformdirs
from PyQt5 import QtWidgets, uic, QtGui

from utils import catch_exceptions, paths

import logging
logger = logging.getLogger(__name__)

class AboutDialog(QtWidgets.QDialog):
    @catch_exceptions(logger=logger)
    def __init__(self):
        super().__init__()
        
        # load qt ui definition file from same directory and named exactly like this file, but having extension ".ui"
        uic.loadUi(os.path.join(os.path.dirname(__file__), os.path.splitext(__file__)[0]+".ui"), self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(paths.get_art_path(), "icon.png")))
        
        self.uiLabel_configDir.setText(paths.user_data_dir())
        self.uiLabel_loggerDir.setText(paths.user_log_dir())
