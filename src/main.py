#!/usr/bin/env python3

import sys
import os
import signal
import _thread
import time
import shutil
import argparse
from PyQt5 import QtWidgets, QtCore, QtNetwork

from utils import paths

# prepare platform dirs and copy over logger.json
os.makedirs(paths.user_data_dir(), exist_ok=True)
os.makedirs(paths.user_log_dir(), exist_ok=True)
os.makedirs(paths.user_cache_dir(), exist_ok=True)
logger_config_file = os.path.join(paths.user_data_dir(), "logger.json")
try:
    shutil.copy2(os.path.join(paths.get_basedir_path(), "data", "conf", "logger.json"), logger_config_file)
except FileExistsError:
    pass

# parse commandline
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="SPH Uploader")
parser.add_argument("--log", metavar='LOGLEVEL', help="Loglevel to log", default="INFO")
parser.add_argument("--forcerun", help="Force run even if another instance is already running", action="store_true", default=False)
parser.add_argument("--replace", help="Replace already running executable", action="store_true", default=False)
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

app = None
tray_icon = None
window = None
def sigint_handler(sig, frame):
    global app
    logger.warning('Main thread got interrupted, shutting down...')
    if app != None:
        app.quit()
        del app
    #os._exit(1)
    sys.exit(1)
signal.signal(signal.SIGINT, sigint_handler)

# needed to properly bind our signal
# see https://stackoverflow.com/a/8795563
class Application(QtWidgets.QApplication):
    messageAvailable = QtCore.pyqtSignal(object)
    
    def __init__(self, argv, already_running):
        super().__init__(argv)
        self.socket_name = "sph_uploader_single_app_socket"
        if args.forcerun or not already_running:
            logger.info("We are the first launch, starting local server...")
            self.server = QtNetwork.QLocalServer(self)
            self.server.newConnection.connect(self._handle_message)
            QtNetwork.QLocalServer.removeServer(self.socket_name)
            self.server.listen(self.socket_name)
            if not self.server.isListening() and not args.forcerun:
                raise RuntimeError("Could not start local server on '%s': %s" % (self.socket_name, self.server.errorString()))
    
    def send_message(self, message, ignore_error=False):
        socket = QtNetwork.QLocalSocket(self)
        socket.connectToServer(self.socket_name, QtCore.QIODevice.WriteOnly)
        if not socket.waitForConnected(1000):
            if not ignore_error:
                raise RuntimeError("Failed to wait for connection on socket: %s" % socket.errorString())
            else:
                logger.error("Failed to wait for connection on socket: %s" % socket.errorString())
        if not isinstance(message, bytes):
            message = message.encode("utf-8")
        socket.write(message)
        if not socket.waitForBytesWritten(1000):
            if not ignore_error:
                raise RuntimeError("Failed to wait for bytes on socket: %s" % socket.errorString())
            else:
                logger.error("Failed to wait for bytes on socket: %s" % socket.errorString())
        socket.disconnectFromServer()
    
    def _handle_message(self):
        logger.debug("Got new local connection...")
        socket = self.server.nextPendingConnection()
        logger.debug("Next connection: %s" % str(socket))
        if socket and socket.waitForReadyRead(100):
            msg = socket.readAll().data().decode('utf-8')
            logger.info("Got local message: '%s'..." % msg)
            self.messageAvailable.emit(msg)
            socket.disconnectFromServer()
        else:
            logger.error("Failed to read from message socket: %s" % socket.errorString())

# ignore pyinstaller splashscreen errors
try:
    import pyi_splash
    pyi_splash.close()
except:
    pass

try:
    # initialize qt application
    lockfile = QtCore.QLockFile(os.path.join(paths.user_data_dir(), "lockfile.lock"))
    if args.replace:
        logger.info("Replace requested, waiting for old application to terminate...")
        app = Application(sys.argv, True)
        while not lockfile.tryLock(100):
            app.send_message("close", ignore_error=True)
            time.sleep(1.1)
        logger.info("Lockfile aquired now, old application did terminate...")
        app.quit()
        del app
        lockfile.unlock()
    already_running = not lockfile.tryLock(100)
    app = Application(sys.argv, already_running)
    app.setQuitOnLastWindowClosed(False) 
    if not already_running or args.forcerun:
        logger.info("Application not running, starting up gui...")
        
        # initialize gui
        from ui import TrayIcon, MainWindow
        window = MainWindow(app)
        tray_icon = TrayIcon(window)
        window.tray_icon = tray_icon
        tray_icon.show()
        # show and hide again to properly initialize it (we sometimes get an empty window otherwise)
        window.show()
        window.hide()
        
        # run qt mainloop
        app.exec_()
    else:
        logger.info("Application already running, sending it a message to bring main window to foreground...")
        app.send_message("show")
except Exception as err:
    logger.exception("Catched top level exception!")
    QtWidgets.QMessageBox.critical(None, "Fatal Top-Level Error!", "%s: %s" % (str(type(err).__name__), str(err)))
except:
    logger.exception("Catched unknown top level exception!")
    QtWidgets.QMessageBox.critical(None, "Fatal Top-Level Error!", "Catched unknown top level exception!")
logger.info("Main event loop returned, shutting down...")
if tray_icon != None and tray_icon.thread:
    try:
        logger.info("Waiting for download thread to terminate...")
        tray_icon.thread.requestInterruption()
        tray_icon.thread.wait()
        logger.info("Download thread terminated...")
    except:
        pass
app.quit()
del app
sys.exit(0)