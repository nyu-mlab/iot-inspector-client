# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['start_inspector.py', 'start_inspector.spec'],
             pathex=['C:\\Users\\debug\\Documents\\research\\iot-inspector-client\\v2-src'],
             binaries=[('npcap-0.9984.exe', '.'),('start_inspector.bat', '.')],
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
          [],
          exclude_binaries=True,
          name='start_inspector',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='start_inspector')
