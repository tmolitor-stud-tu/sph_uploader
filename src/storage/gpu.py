import chardet
import csv
import hashlib

import logging
logger = logging.getLogger(__name__)

def map_art(art, arttext, row):
    ARTMAPPING = {
        ("0", ""): "",
        ("2097153", "C"): "0,21",
        ("2228224", ""): "17,21",
        ("1", "C"): "0",
        ("131072", "B"): "17",
        ("2097152", ""): "21",
        ("2228224", "B"): "17,21",
        ("65536", "R"): "16",
        ("2162688", "R"): "16,21",
        ("2097168", "L"): "4,21",
        ("16", "L"): "4",
    }
    if (art, arttext) in ARTMAPPING:
        logger.debug("Mapping '%s' having arttext '%s' to '%s'..." % (art, arttext, ARTMAPPING[(art, arttext)]))
        return ARTMAPPING[(art, arttext)]
    logger.warning("NOT mapping '%s' having arttext '%s': %s" % (art, arttext, str(row)))
    raise RuntimeError("Inform developer: Unknown mapping for ('%s', '%s') in row: %s" % (art, arttext, str(row)))
    return art

class GPU014:
    def __init__(self, file, filter=set(), filtercode={}):
        self.file = file
        self.filter = filter
        
        if file.strip() == "":
            raise RuntimeError("Tried to access GPU014.TXT without specifying where to find this file!")
        
        logger.info("Processing file '%s'...", file)
        self.data = [
            ["Datum", "Stunde", "AbsenterLehrer", "VertretenderLehrer", "Fach", "Vertretungsfach", "Raum", "Vertretungsraum", "Klassen", "TextZurVertretung", "Vertretungsklassen", "Art", "Vertretungsart", "LetzteAenderung"]
        ]
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
                        if eval(filtercode[f], {
                            "true": True,
                            "false": False,
                        }, {
                            "row": row,
                        }) == True:
                            ignore = True
                            break;
                if ignore:
                    continue
                
                # verwendete daten in erwartetes format umwandeln
                self.data.append([
                    row[1],
                    row[2],
                    row[5],
                    row[6],
                    row[7],
                    row[9],
                    row[11],
                    row[12],
                    row[14],
                    row[16],
                    row[18],
                    map_art(row[17], row[19], row),
                    row[19],
                    row[20],
                ])
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
