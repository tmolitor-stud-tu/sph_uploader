import sys
import os
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from collections import defaultdict
import json
from PyQt5 import QtCore

from utils import widget_name, paths

import logging
logger = logging.getLogger(__name__)

INITIAL_VALUES = {
    "sph_upload": {
        "enabled": False,
        "url": "https://start.schulportal.hessen.de/vertretungsplan.php",       # this is currently not exposed in the ui
        "schulid": 0,
        "uploadKey": "",
        "file": "",
        "filter": [],
        "interval": 1,
        "last_upload_hash": "",                                                 # this is not exposed in the ui
    },
    "web_upload": {
        "enabled": False,
        "url": "",
        "secret": "",
        "dir": "",
        "interval": 1,
        "last_upload_hash": "",                                                 # this is not exposed in the ui
    },
    "misc": {
        "mainTabIndex": 0,
        "supportedFilters": {
            "Freistellungen": "row[19] == \"L\"",
        },
    },
    "states": {},
    "geometries": {},
}

# see https://stackoverflow.com/a/52838324
def json_default(obj):
    if isinstance(obj, datetime):
        return { '_isoformat': obj.isoformat() }
    raise TypeError('...')

# see https://stackoverflow.com/a/52838324
def json_obj_hook(obj):
    _isoformat = obj.get('_isoformat')
    if _isoformat is not None:
        return datetime.fromisoformat(_isoformat)
    return obj


class SettingsSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsSingleton, cls).__new__(cls)
            cls._instance.path = os.path.join(paths.user_data_dir(), "settings.json")
            logger.info("Settings will be stored at '%s'..." % cls._instance.path)
            cls._instance._load()
            logger.debug("Instanciated SettingsSingleton...")
        return cls._instance
    
    def get_sph(self, key):
        if not key in self.data["sph_upload"]:
            return None
        return self.data["sph_upload"][key]
    
    def set_sph(self, key, value):
        self.data["sph_upload"][key] = value
        self._store()    # automatically save on change
    
    def get_web(self, key):
        if not key in self.data["web_upload"]:
            return None
        return self.data["web_upload"][key]
    
    def set_web(self, key, value):
        self.data["web_upload"][key] = value
        self._store()    # automatically save on change
    
    def restore_state(self, widget):
        name = widget_name(widget)
        if name == None:
            raise Exception("Widget '%s' has no object name set!" % widget)
        if name in self.data["states"]:
            widget.restoreState(QtCore.QByteArray.fromBase64(bytes(self.data["states"][name], "UTF-8")))
    
    def save_state(self, widget):
        name = widget_name(widget)
        if name == None:
            raise Exception("Widget '%s' has no object name set!" % widget)
        self.data["states"][name] = str(widget.saveState().toBase64(), "UTF-8")
        self._store()    # automatically save on change
    
    def restore_geometry(self, widget):
        name = widget_name(widget)
        if name == None:
            raise Exception("Widget '%s' has no object name set!" % widget)
        if name in self.data["geometries"]:
            widget.restoreGeometry(QtCore.QByteArray.fromBase64(bytes(self.data["geometries"][name], "UTF-8")))
    
    def save_geometry(self, widget):
        name = widget_name(widget)
        if name == None:
            raise Exception("Widget '%s' has no object name set!" % widget)
        self.data["geometries"][name] = str(widget.saveGeometry().toBase64(), "UTF-8")
        self._store()    # automatically save on change
    
    def __getitem__(self, key):
        if not key in self.data["misc"]:
            return None
        return self.data["misc"][key]
    
    def __setitem__(self, key, value):
        self.data["misc"][key] = value
        self._store()    # automatically save on change
    
    def __delitem__(self, key):
        if not key in self.data["misc"]:
            return
        del self.data["misc"][key]
        self._store()    # automatically save on change
    
    def __len__(self):
        return len(self.data["misc"])
    
    def keys(self):
        return self.data["misc"].keys()
    
    def values(self):
        return self.data["misc"].values()
    
    def items(self):
        return self.data["misc"].items()
    
    def _load(self):
        try:
            with open(self.path, "rb") as fp:
                # merge initial values into stored settings to do an upgrade (e.g. add new values not yet stored in json)
                self.data = json.load(fp, object_hook=json_obj_hook)
                for category in INITIAL_VALUES:
                    if category not in self.data:
                        self.data[category] = INITIAL_VALUES[category]
                        continue
                    for key in INITIAL_VALUES[category]:
                        if key not in self.data[category]:
                            self.data[category][key] = INITIAL_VALUES[category][key]
                # supportedFilters is special (always add new filters, but don't change or remove existing ones)
                for key in INITIAL_VALUES["misc"]["supportedFilters"]:
                        if key not in self.data["misc"]["supportedFilters"]:
                            self.data["misc"]["supportedFilters"][key] = INITIAL_VALUES["misc"]["supportedFilters"][key]
        except Exception as ex:
            logger.warn("Could not load settings.json, propagating using default data: %s" % str(ex))
            # if we couldn't load this, we use a hardcoded default dict
            self.data = INITIAL_VALUES
            self._store()
    
    def _store(self):
        with open(self.path, "w") as fp:
            json.dump(self.data, fp, indent=4, sort_keys=True, default=json_default)
