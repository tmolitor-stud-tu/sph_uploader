import logging
logger = logging.getLogger(__name__)

class Base:
    UPLOAD_TRIES = 0
    LAST_SUCCESSFUL_UPLOAD = "Unbekannt"
    LAST_STATUS = "Unbekannt"
    
    @classmethod
    def get_stats(cls):
        return {
            "upload_tries": str(cls.UPLOAD_TRIES),
            "last_successful_upload": str(cls.LAST_SUCCESSFUL_UPLOAD),
            "upload_status": str(cls.LAST_STATUS),
        }
    
    def _report_http_error(self, text, code, reason):
        logger.error("%s: HTTP %d %s" % (text, code, reason))
        type(self).LAST_STATUS = "HTTP Error: %d %s" % (code, reason)
        raise RuntimeError("%s: HTTP %d %s" % (text, code, reason))
