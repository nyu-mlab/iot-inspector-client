# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['start_inspector.py'],
             pathex=['C:\\Users\\debug\\Documents\\research\\iot-inspector-client\\v2-src'],
             binaries=[],
             datas=[('C:\\Users\\debug\\AppData\\Local\\Programs\\Python\\Python38-32\\Lib\\site-packages\\netdisco\\discoverables\*', 'netdisco\discoverables')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
	  a.binaries,
	  a.zipfiles,
	  a.datas,
	  [],
          name='start_inspector_win',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
