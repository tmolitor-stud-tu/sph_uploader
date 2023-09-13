import requests
import io
import datetime

from .base import Base
from storage import SettingsSingleton

import logging
logger = logging.getLogger(__name__)

class SPH(Base):
    def __init__(self):
        pass
    
    def upload(self, gpu, force=False):
        # read both at once to minimize race conditions
        data = gpu.get_data()
        hash = gpu.get_hash()
        
        if not force and hash == SettingsSingleton().get_sph("last_upload_hash"):
            logger.info("Hash of GPU014.TXT did not change and upload was not forced, doing nothing...")
            return False
        if len(data.strip()) == 0:
            logger.info("Not uploading GPU014.TXT, file at '%s' empty!" % gpu.get_file())
            if force:
                raise RuntimeError("Not uploading GPU014.TXT, file at '%s' empty!" % gpu.get_file())
            return False
        
        type(self).UPLOAD_TRIES += 1
        logger.info("Locking SPH Vertretungsplan...")
        response = requests.post(SettingsSingleton().get_sph("url"), data={
            "i": SettingsSingleton().get_sph("schulid"),
            "c": SettingsSingleton().get_sph("uploadKey"),
            "a": "untis-dif-manuell",
            "reset": "1",
            "upload": "1",
        })
        if response.status_code != 200:
            self._report_http_error("Failed to lock and clear Vertretungsplan", response.status_code, response.reason)
        result = response.text.split("|")
        if result[0] != "1":
            self._report_sph_error("Failed to lock and clear Vertretungsplan", result)
        logger.info("Locking successful...")

        logger.info("Uploading Vertretungsplan...")
        logger.debug("Uploading bytes: %s" % bytes(data, "ISO-8859-1"))
        with io.BytesIO(bytes(data, "ISO-8859-1")) as fp:
            logger.debug("Read from bytesio: %s" % fp.read(1048000))
        data = """Datum;Stunde;AbsenterLehrer;VertretenderLehrer;Fach;Vertretungsfach;Raum;Vertretungsraum;Klassen;TextZurVertretung;Vertretungsklassen;Art;Vertretungsart;LetzteAenderung
20230913;4;HEL;EL;WPU;;Reli;Reli;07C~08C;;07C~08C;;;202309120715
20230913;1;HEL;RE;;;;;;;;17;B;202309120714
20230914;1;SH;;E12ge.11;;KP12;;E12;eigenst. Arbeiten;E12;0,21;C;202309131010
20230914;2;SH;;E12ge.11;;KP12;;E12;eigenst. Arbeiten;E12;0,21;C;202309131010
20230914;3;SH;;Bereit;;;;;;;21;;202309131007
20230914;5;SH;;Q12gbio.23;;BUE;;Q12;eigenst. Arbeiten;Q12;0,21;C;202309131010
20230914;6;SH;;Q12gbio.23;;BUE;;Q12;eigenst. Arbeiten;Q12;0,21;C;202309131010
20230914;3;SH;BOE;;;;;;;;17,21;B;202309131009
20230914;5;FÖ;LÖL;RKA;;MW26;MW26;05A~05B~05C;;05A~05B~05C;21;;202309131413
20230914;7;WIN;BER;Kl-St;;MW23;MW23;10B;;10B;21;;202309131434
"""
        response = requests.post(SettingsSingleton().get_sph("url"), data={
            "i": SettingsSingleton().get_sph("schulid"),
            "c": SettingsSingleton().get_sph("uploadKey"),
            "a": "untis-dif-manuell",
            "upload": "1",
        }, files={"d": io.StringIO(data)})      # convert to ISO-8859-1 (needed by sph)
        if response.status_code != 200:
            self._report_http_error("Failed to upload Vertretungsplan", response.status_code, response.reason)
        result = response.text.split("|")
        if result[0] != "1":
            self._report_sph_error("Failed to upload Vertretungsplan", result)
        logger.info("Upload successful...")

        logger.info("Unlocking SPH Vertretungsplan...")
        response = requests.post(SettingsSingleton().get_sph("url"), data={
            "i": SettingsSingleton().get_sph("schulid"),
            "c": SettingsSingleton().get_sph("uploadKey"),
            "a": "untis-dif-manuell",
            "unlock": "1",
            "upload": "1",
        })
        if response.status_code != 200:
            self._report_http_error("Failed to unlock Vertretungsplan", response.status_code, response.reason)
        result = response.text.split("|")
        if result[0] != "1":
            self._report_sph_error("Failed to unlock Vertretungsplan", result)
        logger.info("Unlocking successful...")

        logger.info("Vertretungsplan successfully updated :)")
        SettingsSingleton().set_sph("last_upload_hash", hash)
        type(self).LAST_SUCCESSFUL_UPLOAD = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        type(self).LAST_STATUS = "OK"
        return True
    
    def _report_sph_error(self, text, result):
        logger.error("%s: %s (code: %s)" % (text, result[1], result[0]))
        type(self).LAST_STATUS = "SPH Error: %s (code: %s)" % (result[1], result[0])
        raise RuntimeError("%s: %s (code: %s)" % (text, result[1], result[0]))
    
