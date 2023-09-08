import requests
import io
import datetime

from .base import Base
from storage import SettingsSingleton

import logging
logger = logging.getLogger(__name__)

class Web(Base):
    def __init__(self):
        pass

    def upload(self, pdf, force=False):
        hash = pdf.get_hash()
        if not force and hash == SettingsSingleton().get_web("last_upload_hash"):
            logger.info("Hash of PDF files did not change and upload was not forced, doing nothing...")
            return
        if len(pdf.get_files()) == 0:
            logger.info("Not uploading PDF files, no files found at '%s'!" % pdf.get_dir())
            if force:
                raise RuntimeError("Not uploading PDF files, no files found at '%s'!" % pdf.get_dir())
            return
        
        type(self).UPLOAD_TRIES += 1
        logger.info("Uploading PDF files: %s" % str(pdf.get_files()))
        response = requests.post(SettingsSingleton().get_web("url"), headers={
            "X-SECRET": SettingsSingleton().get_web("secret"),
        }, files=pdf.get_fp_dict())
        if response.status_code != 200:
            self._report_http_error("Failed to upload PDF files", response.status_code, response.reason)
        logger.debug("PDF upload response text: '%s'" % response.text.strip())
        if response.text.strip() == "":
            logger.error("Failed to upload PDF files: Result unexpectedly empty, is your secret wrong?")
            type(self).LAST_STATUS = "Upload result unexpectedly empty!"
            raise RuntimeError("Failed to upload PDF files: Result unexpectedly empty, is your secret wrong?")
        logger.info("PDF files uploaded successfully :)")
        SettingsSingleton().set_web("last_upload_hash", hash)
        type(self).LAST_SUCCESSFUL_UPLOAD = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        type(self).LAST_STATUS = "OK"
