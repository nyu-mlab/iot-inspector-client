#!/bin/bash

pyinstaller start_inspector_mac.spec

zip -r dist/start_inspector_mac.zip start_inspector.app
