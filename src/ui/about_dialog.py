import sys
import os
from PyQt5 import QtWidgets, uic, QtGui

from utils import catch_exceptions

import logging
logger = logging.getLogger(__name__)

class AboutDialog(QtWidgets.QDialog):
    @catch_exceptions(logger=logger)
    def __init__(self):
        super().__init__()
        
        # load qt ui definition file from same directory and named exactly like this file, but having extension ".ui"
        uic.loadUi(os.path.join(os.path.dirname(__file__), os.path.splitext(__file__)[0]+".ui"), self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "..", "art", "icon.png")))
