import os
import csv
import hashlib
import glob

import logging
logger = logging.getLogger(__name__)

class PDF:
    def __init__(self, dir):
        if dir.strip() == "":
            raise RuntimeError("Tried to acces PDF files without specifying which directory holds these!")
        self.dir = dir
    
    def get_dir(self):
        return self.dir
    
    def get_fp_dict(self):
        fps = {}
        for file in self.get_files():
            fps[os.path.basename(file)] = open(file, "rb")
        return fps
    
    def get_files(self):
        if self.dir.strip() == "":
            return []
        return glob.glob("%s/*.pdf" % self.dir)
    
    def get_hash(self):
        hash = hashlib.blake2b(person=bytes("webpdf", "UTF8"))
        for filename, fp in self.get_fp_dict().items():
            for chunk in iter(lambda: fp.read(131072), b""):
                hash.update(chunk)
        return hash.hexdigest()
