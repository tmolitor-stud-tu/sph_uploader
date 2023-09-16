import os
from PyQt5 import QtWidgets, QtGui

from utils import catch_exceptions, paths, VERSION, init_ui

import logging
logger = logging.getLogger(__name__)

class AboutDialog(QtWidgets.QDialog):
    @catch_exceptions(logger=logger)
    @init_ui        # load qt ui definition file from same directory and named exactly like this file, but having extension ".ui"
    def __init__(self):
        self.setWindowIcon(QtGui.QIcon(paths.get_art_filepath("icon.png")))
        #self.setFixedSize(self.size())
        
        self.uiLabel_version.setText(VERSION)
        self.uiLabel_configDir.setText(paths.user_data_dir())
        self.uiLabel_loggerDir.setText(paths.user_log_dir())
