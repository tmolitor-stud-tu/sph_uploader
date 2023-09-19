import chardet
import csv
import hashlib

from .settings import SettingsSingleton

import logging
logger = logging.getLogger(__name__)

class GPU014:
    def __init__(self, file, filter=set(), filtercode={}):
        self.file = file
        self.filter = filter
        
        if file.strip() == "":
            raise RuntimeError("Tried to access GPU014.TXT without specifying where to find this file!")
        
        logger.info("Processing file '%s'...", file)
        self.data = []
        with open(file, "rb") as fp:
            sniffdata = fp.read(10000)
            chardet_result = chardet.detect(sniffdata)
            dialect = csv.Sniffer().sniff(str(sniffdata, chardet_result["encoding"]))
        logger.debug("Chardet result: %s" % str(chardet_result))
        logger.debug("CSV Sniffer dialect: (delimiter='%s', quotechar='%s')" % (dialect.delimiter, dialect.quotechar))
        with open(file, newline="", encoding=chardet_result["encoding"]) as fp:
            for row in csv.reader(fp, dialect=dialect):
                # filter anwenden
                ignore = False
                for f in filter:
                    if f in filtercode:
                        globals_dict = {
                            "true": True,
                            "false": False,
                        }
                        locals_dict = {
                            "row": row,
                        }
                        exec(filtercode[f]["pre-exec"], globals_dict, locals_dict)
                        if eval(filtercode[f]["eval"], globals_dict, locals_dict) == True:
                            if SettingsSingleton()["log_filter_decisions"]:
                                logger.debug("Filter '%s' ignores row: %s" % (f, str(row)))
                            ignore = True
                            break;
                if ignore:
                    continue
                self.data.append(row)
        self.data = "\n".join([";".join(row) for row in self.data])
        logger.debug("Filtered and parsed data:\n%s" % self.data)
        logger.info("Processing done...")
    
    def get_file(self):
        return self.file
    
    def get_filter(self):
        return self.filter
    
    def get_data(self):
        return self.data
    
    def get_hash(self):
        return hashlib.blake2b(bytes(self.data, "UTF8"), person=bytes("schulportal", "UTF8")).hexdigest()
