import os
import sys
import stat
import requests
from packaging import version
import platform
from collections import defaultdict 
import shutil
import subprocess
from dateutil import parser as dateparser

from .base import Base
from utils import paths, VERSION, GITHUB_USER, GITHUB_PROJECT

import logging
logger = logging.getLogger(__name__)

class Github(Base):
    def __init__(self):
        super().__init__()
    
    def has_update(self):
        try:
            current_version = version.parse(VERSION)
        except:
            #current_version = version.parse("0.0")
            return None
        logger.info("Current version: %s" % str(current_version))
        data = self._fetch_latest_release_metadata()
        logger.info("Latest release on github: tag=%s, name=%s, published_at=%s" % (data["tag_name"], data["name"], data["published_at"]))
        if version.parse(data["tag_name"]) > current_version:
            return {
                "version": data["tag_name"],
                "name": data["name"],
                "date": dateparser.parse(data["published_at"]),
            }
        else:
            return None
    
    def download_latest_release(self, progress_callback=None):
        asset = self.get_latest_download_asset()
        path = os.path.join(paths.user_cache_dir(), asset["name"])
        url = asset["browser_download_url"]
        
        logger.info("Downloading new executable from '%s' to '%s'..." % (url, path))
        with requests.get(url, stream=True, timeout=2) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=None):
                    if progress_callback != None and progress_callback():
                        logger.info("Download got aborted by progress_callback...")
                        return      # abort download if requested
                    if chunk: 
                        f.write(chunk)
        logger.info("Download succeeded...")
        
        # don't auto-replace if not using packaged executable
        if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
            raise Exception("Bitte Update manuell von hier installieren: %s" % path)
        
        # auto-replace executable, if possible (on darwin only open dmg file)
        if platform.system() == "Darwin":
            logger.info("Opening newly downloaded dmg file at '%s' and showing alert to user..." % path)
            os.system("open %s" % path)
            raise Exception("Bitte Update manuell von hier installieren: %s" % path)
        else:
            logger.info("Renaming currently running executable to '%s.bak' and spawn newly downloaded executable at '%s'..." % (sys.executable, sys.executable))
            os.replace(sys.executable, "%s.bak" % sys.executable)
            shutil.copy2(path, sys.executable)
            try:
                current_permissions = os.stat(sys.executable)
                os.chmod(sys.executable, current_permissions.st_mode | stat.S_IEXEC)
            except:
                logger.exception("Ignoring exception while trying to make downloaded file executable:")
            cmds = [sys.executable] + sys.argv[1:] + ["--replace"]
            logger.info("CMDs: %s" % str(cmds))
            subprocess.Popen(cmds, start_new_session=True)
            logger.info("Spawned newly downloaded executable at '%s' with '--replace'..." % sys.executable)
    
    def get_latest_download_asset(self):
        data = self._fetch_latest_release_metadata()
        # we default to the linux name, if the platform is unknown to us
        system2filename = defaultdict(lambda: "sph_uploader", {
            "Windows": "sph_uploader.exe",
            "Darwin": "sph_uploader.dmg",
            "Linux": "sph_uploader",
        })
        expected_name = system2filename[platform.system()]
        for asset in data["assets"]:
            if asset["name"] == expected_name:
                logger.info("Download url for this platform: %s at %s" % (asset["name"], asset["browser_download_url"]))
                return asset
        logger.warn("Could not determine release asset metadata!")
        return None
    
    def _fetch_latest_release_metadata(self):
        response = requests.get("https://api.github.com/repos/%s/%s/releases/latest" % (GITHUB_USER, GITHUB_PROJECT), timeout=2)
        if response.status_code != 200:
            self._report_http_error("Failed to fetch latest release metadata from github", response.status_code, response.reason)
        return response.json()
