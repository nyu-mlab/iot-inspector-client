#!/bin/bash

pyinstaller start_inspector_mac.spec

zip -r dist/start_inspector_mac.zip start_inspector.app

shasum -a 256 dist/start_inspector_mac.zip > dist/start_inspector_mac.sha256.txt
