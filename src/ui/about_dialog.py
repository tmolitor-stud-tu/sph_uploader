import sys
import os
import platformdirs
from PyQt5 import QtWidgets, uic, QtGui

from utils import catch_exceptions, paths, VERSION

import logging
logger = logging.getLogger(__name__)

class AboutDialog(QtWidgets.QDialog):
    @catch_exceptions(logger=logger)
    def __init__(self):
        super().__init__()
        
        # load qt ui definition file from same directory and named exactly like this file, but having extension ".ui"
        uifile = paths.get_ui_filepath(os.path.splitext(os.path.basename(__file__))[0]+".ui")
        logger.debug("Loading ui file located at: '%s'..." % uifile)
        uic.loadUi(uifile, self)
        self.setWindowIcon(QtGui.QIcon(paths.get_art_filepath("icon.png")))
        self.setFixedSize(self.size())
        
        self.uiLabel_version.setText(VERSION)
        self.uiLabel_configDir.setText(paths.user_data_dir())
        self.uiLabel_loggerDir.setText(paths.user_log_dir())
