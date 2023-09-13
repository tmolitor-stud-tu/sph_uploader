#!/bin/bash

cd "$(dirname "$0")"

pyinstaller --log-level DEBUG --name "sph_uploader" --add-data "data:data" --add-data "ui/*.ui:ui" --splash data/art/splash.png --specpath src --windowed --icon data/art/icon.png --onefile src/main.py 

# spec is now removed from repo
# # fix icon definition in spec (needed for windows build)
# sed -i "s|icon=\\['../art/icon.png'\\],|icon='../art/icon.png',|g" src/sph_uploader.spec
