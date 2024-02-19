import os
import platform
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QTimer

from storage import SettingsSingleton
from .about_dialog import AboutDialog
from utils import catch_exceptions, paths
from net import Github

import logging
logger = logging.getLogger(__name__)


class DownloadWorker(QObject):
    update_message = pyqtSignal(dict)
    update_error = pyqtSignal(Exception)
    
    @catch_exceptions(logger=logger)
    def run(self):
        logger.info("Starting downloader thread...")
        QThread.setTerminationEnabled(True)
        try:
            github = Github()
            update_metadata = github.has_update()
            if update_metadata != None:
                self.update_message.emit(update_metadata)
                if SettingsSingleton()["auto_install_updates"]:
                    github.download_latest_release(lambda: QThread.currentThread().isInterruptionRequested())
        except Exception as err:
            logger.exception("Exception while downloading update!")
            self.update_error.emit(err)
        logger.info("Stopping downloader thread...")
        self.deleteLater()
        QThread.currentThread().quit()


class TrayIcon(QtWidgets.QSystemTrayIcon):
    @catch_exceptions(logger=logger)
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # create tray icon and menu
        logger.info("Loading tray icon at '%s'..." % paths.get_art_filepath("icon.png"))
        icon = QtGui.QIcon(paths.get_art_filepath("icon.png"))
        self.setIcon(icon)
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
        self.setVisible(True)
        
        # connect menu items
        self.uiAction_hideShow.triggered.connect(self.action_hide_show)
        self.uiAction_about.triggered.connect(self.action_about)
        self.uiAction_quit.triggered.connect(self.action_quit)
        # macos always shows the context menu, even on left click --> just don't show window on left click
        if platform.system() != "Darwin":
            self.activated.connect(self.action_show)
        self.messageClicked.connect(lambda *args: self.action_show(QtWidgets.QSystemTrayIcon.ActivationReason.Trigger))
        
        # intialize menu state
        self.update_menu()
        
        # check for updates in an extra background thread to not block ui while checking/downloading
        # see https://realpython.com/python-pyqt-qthread/#multithreading-in-pyqt-with-qthread
        self.thread = QThread(self)
        self.download_worker = DownloadWorker()
        self.download_worker.moveToThread(self.thread)
        self.thread.started.connect(self.download_worker.run)
        #self.download_worker.finished.connect(self.download_worker.deleteLater)
        self.thread.finished.connect(self.cleanupThread)
        self.download_worker.update_message.connect(self.show_update_message)
        self.download_worker.update_error.connect(self.show_update_error)
        self.thread.start()
        
        # show init message
        self.showMessage(
            "SPH Uploader",
            "SPH Uploader überwacht nun die konfigurierten Dateien auf Veränderungen",
            QtWidgets.QSystemTrayIcon.Information,
            4000
        )
        
        self.installEventFilter(self)
    
    @pyqtSlot()
    @catch_exceptions(logger=logger)
    def cleanupThread(self):
        self.thread.deleteLater()
        self.thread = None
    
    @pyqtSlot(dict)
    @catch_exceptions(logger=logger)
    def show_update_message(self, update_metadata):
        self.showMessage(
            "SPH Uploader Update verfügbar",
            "Neues Release von %s verfügbar: %s" % (update_metadata["date"].strftime('%x %X'), update_metadata["version"]),
            QtWidgets.QSystemTrayIcon.Warning,
            10000
        )
    
    @pyqtSlot(Exception)
    @catch_exceptions(logger=logger)
    def show_update_error(self, err):
        self.showMessage(
            "SPH Uploader Update Error",
            "Konnte Update nicht herunterladen: %s" % str(err),
            QtWidgets.QSystemTrayIcon.Warning,
            4000
        )
        QtWidgets.QMessageBox.critical(None, "SPH Uploader Update Error", "Konnte Update nicht herunterladen: %s" % str(err))
    
    @catch_exceptions(logger=logger)
    def action_show(self, trigger):
        logger.debug("Tray trigger: %d" % trigger)
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
