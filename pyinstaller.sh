#!/bin/bash

cd "$(dirname "$0")"

pyinstaller --log-level DEBUG --name "sph_uploader" --add-data conf:conf --add-data ui/*.ui:ui --add-data ../art/icon.png:art --splash ../art/splash.png --specpath src --windowed --icon ../art/icon.png --onefile src/main.py 

# spec is now removed from repo
# # fix icon definition in spec (needed for windows build)
# sed -i "s|icon=\\['../art/icon.png'\\],|icon='../art/icon.png',|g" src/sph_uploader.spec
