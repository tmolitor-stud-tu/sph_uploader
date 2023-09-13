import os
from PyQt5 import QtWidgets, QtGui

from .about_dialog import AboutDialog
from utils import catch_exceptions, paths

import logging
logger = logging.getLogger(__name__)

class TrayIcon(QtWidgets.QSystemTrayIcon):
    @catch_exceptions(logger=logger)
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # create tray icon and menu
        self.setIcon(QtGui.QIcon(os.path.join(paths.get_art_path(), "icon.png")))
        self.tray_menu = QtWidgets.QMenu()
        self.uiAction_hideShow = QtWidgets.QAction("dummy_text", self)
        self.tray_menu.addAction(self.uiAction_hideShow)
        self.uiAction_about = QtWidgets.QAction(self.main_window.style().standardIcon(QtWidgets.QStyle.SP_TitleBarContextHelpButton), "Über", self)
        self.tray_menu.addAction(self.uiAction_about)
        self.tray_menu.addSeparator()
        self.uiAction_quit = QtWidgets.QAction(self.main_window.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton), "Beenden", self)
        self.tray_menu.addAction(self.uiAction_quit)
        self.setToolTip("SPH Uploader")
        self.setContextMenu(self.tray_menu)
        self.show()
        
        # connect menu items
        self.uiAction_hideShow.triggered.connect(self.action_hide_show)
        self.uiAction_about.triggered.connect(self.action_about)
        self.uiAction_quit.triggered.connect(self.action_quit)
        self.activated.connect(self.action_show)
        self.messageClicked.connect(lambda *args: self.action_show(QtWidgets.QSystemTrayIcon.ActivationReason.Trigger))
        
        # intialize menu state
        self.update_menu()
        
        # show init message
        self.showMessage(
            "SPH Uploader",
            "SPH Uploader erfolgreich initialisiert",
            QtWidgets.QSystemTrayIcon.Information,
            4000
        )
    
    @catch_exceptions(logger=logger)
    def action_show(self, trigger):
        if trigger != QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            logger.debug("Tray trigger wrong: %d" % trigger)
            return
        self.action_hide_show()
    
    @catch_exceptions(logger=logger)
    def action_hide_show(self, *args):
        if self.main_window.isVisible():
            logger.info("Closing main window...")
            self.main_window.close()
        else:
            logger.info("Showing main window...")
            self.main_window.showNormal()       # used instead of show() to make sure this will be opened in the foreground
        self.update_menu()
    
    @catch_exceptions(logger=logger)
    def action_about(self, *args):
        logger.info("Showing About Dialog...")
        about = AboutDialog()
        about.show()
        about.exec_()
    
    @catch_exceptions(logger=logger)
    def action_quit(self, *args):
        logger.info("Closing application...")
        QtWidgets.QApplication.quit()
    
    def update_menu(self):
        if self.main_window.isVisible():
            self.uiAction_hideShow.setText("Uploader verstecken")
            self.uiAction_hideShow.setIcon(self.main_window.style().standardIcon(QtWidgets.QStyle.SP_TitleBarMinButton))
        else:
            self.uiAction_hideShow.setText("Uploader anzeigen")
            self.uiAction_hideShow.setIcon(self.main_window.style().standardIcon(QtWidgets.QStyle.SP_TitleBarMaxButton))
