import os
from PyQt5 import QtWidgets, QtGui, QtCore

from .about_dialog import AboutDialog
from utils import catch_exceptions, display_exceptions, widget_name, paths, init_ui
from storage import SettingsSingleton, GPU014, PDF
from net import SPH, Web

import logging
logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    @catch_exceptions(logger=logger)
    @init_ui        # load qt ui definition file from same directory and named exactly like this file, but having extension ".ui"
    def __init__(self, app):
        # load ui state
        self.setWindowIcon(QtGui.QIcon(paths.get_art_filepath("icon.png")))
        self.setFixedSize(self.size())
        SettingsSingleton().restore_geometry(self)
        SettingsSingleton().restore_state(self)
        tabIndex = SettingsSingleton()[widget_name(self.uiTabWidget_mainTabs)]
        self.uiTabWidget_mainTabs.setCurrentIndex(tabIndex if tabIndex != None else -1)
        
        # load ui element contents
        self.uiCheckBox_sphEnabled.setChecked(SettingsSingleton().get_sph("enabled"))
        self.uiSpinBox_sphSchulid.setValue(SettingsSingleton().get_sph("schulid"))
        self.uiLineEdit_sphUploadKey.setText(SettingsSingleton().get_sph("uploadKey"))
        self.uiLineEdit_sphFile.setText(SettingsSingleton().get_sph("file"))
        for filter in SettingsSingleton()["supportedFilters"].keys():
            self.uiListWidget_sphFilter.addItem(filter)
        for i in range(self.uiListWidget_sphFilter.count()):
            item = self.uiListWidget_sphFilter.item(i);
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable);
            item.setCheckState(QtCore.Qt.Checked if item.text().strip() in SettingsSingleton().get_sph("filter") else QtCore.Qt.Unchecked)
        self.uiSpinBox_sphInterval.setValue(SettingsSingleton().get_sph("interval"))
        self._update_sph_stats()
        
        self.uiCheckBox_webEnabled.setChecked(SettingsSingleton().get_web("enabled"))
        self.uiLineEdit_webUrl.setText(SettingsSingleton().get_web("url"))
        self.uiLineEdit_webSecret.setText(SettingsSingleton().get_web("secret"))
        self.uiLineEdit_webDir.setText(SettingsSingleton().get_web("dir"))
        self.uiSpinBox_webInterval.setValue(SettingsSingleton().get_web("interval"))
        self._update_web_stats()
        
        # connect ui element signals
        self.uiAction_close.triggered.connect(self.action_close)
        self.uiAction_quit.triggered.connect(self.action_quit)
        self.uiAction_about.triggered.connect(self.action_about)
        self.uiTabWidget_mainTabs.currentChanged.connect(self.tab_changed)
        
        self.uiCheckBox_sphEnabled.stateChanged.connect(self.sph_enable_changed)
        self.uiSpinBox_sphSchulid.valueChanged.connect(self.sph_schulid_changed)
        self.uiLineEdit_sphUploadKey.editingFinished.connect(self.sph_upload_key_changed)
        self.uiLineEdit_sphFile.editingFinished.connect(self.sph_file_changed)
        self.uiButton_sphSelectFile.clicked.connect(self.sph_open_file)
        self.uiListWidget_sphFilter.itemChanged.connect(self.sph_filter_changed)
        self.uiSpinBox_sphInterval.valueChanged.connect(self.sph_interval_changed)
        self.uiButton_sphForceUpload.clicked.connect(self.sph_force_upload)
        
        self.uiCheckBox_webEnabled.stateChanged.connect(self.web_enable_changed)
        self.uiLineEdit_webUrl.editingFinished.connect(self.web_url_changed)
        self.uiLineEdit_webSecret.editingFinished.connect(self.web_secret_changed)
        self.uiLineEdit_webDir.editingFinished.connect(self.web_dir_changed)
        self.uiButton_webSelectDir.clicked.connect(self.web_open_dir)
        self.uiSpinBox_webInterval.valueChanged.connect(self.web_interval_changed)
        self.uiButton_webForceUpload.clicked.connect(self.web_force_upload)
        
        self.resizeEvent = self.window_resized
        
        # create timer
        self._configure_sph_timer()
        self._configure_web_timer()
        self.closeTimer = QtCore.QTimer()
        self.closeTimer.timeout.connect(QtWidgets.QApplication.quit)
        
        # handle app messages (single app mode)
        app.messageAvailable.connect(self.handle_message)
    
    @catch_exceptions(logger=logger)
    def handle_message(self, message):
        if message == "show":
            logger.info("Received show message, displaying main window...")
            self.showNormal()       # used instead of show() to make sure this will be opened in the foreground
        elif message == "close":
            logger.warning("Got command 'close', terminating in one second...")
            # using a timer to make sure the message handling code in main.py runs to its end before terminating this app
            if not self.closeTimer.isActive():
                self.closeTimer.start(1000)
        else:
            logger.error("Received unsupported message: '%s'!" % message)
    
    @catch_exceptions(logger=logger)
    def closeEvent(self, event):
        logger.info("Closing main window...")
        self._closing()
        self.hide()
        self.tray_icon.update_menu()
        event.ignore()
    
    @catch_exceptions(logger=logger)
    def window_resized(self, *args):
        SettingsSingleton().save_geometry(self)
    
    @catch_exceptions(logger=logger)
    def action_close(self, *args):
        self.close()
    
    @catch_exceptions(logger=logger)
    def action_quit(self, *args):
        logger.info("Closing application...")
        QtWidgets.QApplication.quit()
    
    @catch_exceptions(logger=logger)
    def action_about(self, *args):
        logger.info("Showing About Dialog...")
        about = AboutDialog()
        about.show()
        about.exec_()
    
    @catch_exceptions(logger=logger)
    def tab_changed(self, index):
        SettingsSingleton()[widget_name(self.uiTabWidget_mainTabs)] = index
    
    # *** SPH ***
    
    @catch_exceptions(logger=logger)
    def sph_enable_changed(self, *args):
        logger.info("SPH enabled changed: %d" % self.uiCheckBox_sphEnabled.isChecked())
        SettingsSingleton().set_sph("enabled", self.uiCheckBox_sphEnabled.isChecked())
        self._configure_sph_timer()
    
    @catch_exceptions(logger=logger)
    def sph_schulid_changed(self, *args):
        logger.info("Storing new SPH schulid: %d..." % self.uiSpinBox_sphSchulid.value())
        SettingsSingleton().set_sph("schulid", self.uiSpinBox_sphSchulid.value())
    
    @catch_exceptions(logger=logger)
    def sph_upload_key_changed(self, *args):
        logger.info("Stroring new SPH upload key: %s" % self.uiLineEdit_sphUploadKey.text())
        SettingsSingleton().set_sph("uploadKey", self.uiLineEdit_sphUploadKey.text())
    
    @catch_exceptions(logger=logger)
    def sph_file_changed(self, *args):
        logger.info("Storing new SPH file path: %s" % self.uiLineEdit_sphFile.text())
        SettingsSingleton().set_sph("file", self.uiLineEdit_sphFile.text().strip())
    
    @catch_exceptions(logger=logger)
    def sph_open_file(self, *args):
        logger.info("Showing SPH file open dialog...")
        filename, check = QtWidgets.QFileDialog.getOpenFileName(self, "GPU014 Datei öffnen", "", "GPU014 (GPU014.TXT)(GPU014.TXT);;All files (*)")
        if check:
            self.uiLineEdit_sphFile.setText(filename)
            self.sph_file_changed()      # this is not automatically invoked by setText()
    
    @catch_exceptions(logger=logger)
    def sph_filter_changed(self, *args):
        filter = [self.uiListWidget_sphFilter.item(i).text() for i in range(self.uiListWidget_sphFilter.count()) if self.uiListWidget_sphFilter.item(i).checkState() == QtCore.Qt.Checked]
        logger.info("Active SPH filters: %s" % str(filter))
        SettingsSingleton().set_sph("filter", filter)
    
    @catch_exceptions(logger=logger)
    def sph_interval_changed(self, *args):
        logger.info("Storing new SPH upload interval: %s" % self.uiSpinBox_sphInterval.value())
        SettingsSingleton().set_sph("interval", self.uiSpinBox_sphInterval.value())
        self._configure_sph_timer()
    
    @catch_exceptions(logger=logger)
    def sph_force_upload(self, *args):
        logger.info("Forcing SPH upload...")
        self._trigger_sph_upload(True)
    
    @catch_exceptions(logger=logger)
    def sph_timer_triggered(self, *args):
        logger.info("Timer triggered SPH upload...")
        self._trigger_sph_upload(False)
    
    # *** Web ***
    
    @catch_exceptions(logger=logger)
    def web_enable_changed(self, *args):
        logger.info("Web enabled changed: %d" % self.uiCheckBox_webEnabled.isChecked())
        SettingsSingleton().set_web("enabled", self.uiCheckBox_webEnabled.isChecked())
        self._configure_web_timer()
    
    @catch_exceptions(logger=logger)
    def web_url_changed(self, *args):
        logger.info("Stroring new web url: %s" % self.uiLineEdit_webUrl.text())
        SettingsSingleton().set_web("url", self.uiLineEdit_webUrl.text())
    
    @catch_exceptions(logger=logger)
    def web_secret_changed(self, *args):
        logger.info("Stroring new web secret: %s" % self.uiLineEdit_webSecret.text())
        SettingsSingleton().set_web("secret", self.uiLineEdit_webSecret.text())
    
    @catch_exceptions(logger=logger)
    def web_dir_changed(self, *args):
        logger.info("Storing new web dir: %s" % self.uiLineEdit_webDir.text())
        SettingsSingleton().set_web("dir", self.uiLineEdit_webDir.text().strip())
    
    @catch_exceptions(logger=logger)
    def web_open_dir(self, *args):
        logger.info("Showing web dir open dialog...")
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "PDF Ordner öffnen", self.uiLineEdit_webDir.text(), QtWidgets.QFileDialog.ShowDirsOnly)
        logger.error("dirname: %s" % str(dirname))
        if dirname != None and dirname.strip() != "":
            self.uiLineEdit_webDir.setText(dirname)
            self.web_dir_changed()      # this is not automatically invoked by setText()
    
    @catch_exceptions(logger=logger)
    def web_interval_changed(self, *args):
        logger.info("Storing new web upload interval: %s" % self.uiSpinBox_webInterval.value())
        SettingsSingleton().set_web("interval", self.uiSpinBox_webInterval.value())
        self._configure_web_timer()
    
    @catch_exceptions(logger=logger)
    def web_force_upload(self, *args):
        logger.info("Forcing web upload...")
        self._trigger_web_upload(True)
    
    @catch_exceptions(logger=logger)
    def web_timer_triggered(self, *args):
        logger.info("Timer triggered web upload...")
        self._trigger_web_upload(False)
    
    # *** internals ***
    
    def _configure_sph_timer(self):
        if not hasattr(self, "sph_timer"):
            logger.info("Creating web timer...")
            self.sph_timer = QtCore.QTimer()
            self.sph_timer.timeout.connect(self.sph_timer_triggered)
        if self.uiCheckBox_sphEnabled.isChecked():
            self.sph_timer.start(self.uiSpinBox_sphInterval.value() * 60 * 1000)    # the spinbox value is in minutes
        else:
            self.sph_timer.stop()
    
    def _trigger_sph_upload(self, force=False):
        self.uiStatusbar_statusbar.showMessage("Lade GPU014 hoch (%s)..." % ("ausgelöst durch Timer" if not force else "manuell ausgelöst"))
        QtWidgets.QApplication.processEvents()          # force ui redraw and events processing
        try:
            file = SettingsSingleton().get_sph("file")
            filterset = set(SettingsSingleton().get_sph("filter"))
            filtercode = SettingsSingleton()["supportedFilters"]
            if SPH().upload(GPU014(file, filterset, filtercode), force):
                self.tray_icon.showMessage(
                    "GPU014 Upload",
                    "GPU014 Upload erfolgreich",
                    QtWidgets.QSystemTrayIcon.Information,
                    4000
                )
        except Exception as err:
            logger.exception("Exception while uploading!")
            self.tray_icon.showMessage(
                "GPU014 Upload",
                "GPU014 Upload fehlgeschlagen",
                QtWidgets.QSystemTrayIcon.Warning,
                4000
            )
            QtWidgets.QMessageBox.warning(None, str(type(err).__name__), str(err))
        self.uiStatusbar_statusbar.showMessage("")
        self._update_sph_stats()
    
    def _update_sph_stats(self):
        stats = SPH.get_stats()
        self.uiLabel_sphUploadCount.setText(stats["upload_tries"])
        self.uiLabel_sphTimestamp.setText(stats["last_successful_upload"])
        self.uiLabel_sphStatus.setText(stats["upload_status"])
    
    def _configure_web_timer(self):
        if not hasattr(self, "web_timer"):
            logger.info("Creating sph timer...")
            self.web_timer = QtCore.QTimer()
            self.web_timer.timeout.connect(self.web_timer_triggered)
        if self.uiCheckBox_webEnabled.isChecked():
            self.web_timer.start(self.uiSpinBox_webInterval.value() * 60 * 1000)    # the spinbox value is in minutes
        else:
            self.web_timer.stop()
    
    def _trigger_web_upload(self, force=False):
        self.uiStatusbar_statusbar.showMessage("Lade PDFs hoch (%s)..." % ("ausgelöst durch Timer" if not force else "manuell ausgelöst"))
        QtWidgets.QApplication.processEvents()          # force ui redraw and events processing
        try:
            if Web().upload(PDF(SettingsSingleton().get_web("dir")), force):
                self.tray_icon.showMessage(
                    "PDF Upload",
                    "PDF Upload erfolgreich",
                    QtWidgets.QSystemTrayIcon.Information,
                    4000
                )
        except Exception as err:
            logger.exception("Exception while uploading!")
            self.tray_icon.showMessage(
                "PDF Upload",
                "PDF Upload fehlgeschlagen",
                QtWidgets.QSystemTrayIcon.Warning,
                4000
            )
            QtWidgets.QMessageBox.warning(None, str(type(err).__name__), str(err))
        self.uiStatusbar_statusbar.showMessage("")
        self._update_web_stats()
    
    def _update_web_stats(self):
        stats = Web.get_stats()
        self.uiLabel_webUploadCount.setText(stats["upload_tries"])
        self.uiLabel_webTimestamp.setText(stats["last_successful_upload"])
        self.uiLabel_webStatus.setText(stats["upload_status"])
    
    def _closing(self):
        SettingsSingleton().save_state(self)
        SettingsSingleton().save_geometry(self)
