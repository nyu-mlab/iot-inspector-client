# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Please set the developer's name first, so that pyinstaller can use the correct paths.
developer_name = 'danny'

if developer_name == 'deepak':
    var_pathex = ['C:\\Users\\debug\\Documents\\research\\iot-inspector-client\\v2-src']
    var_datas = [('C:\\Users\\debug\\AppData\\Local\\Programs\\Python\\Python38-32\\Lib\\site-packages\\netdisco\\discoverables\*', 'netdisco\discoverables')]
elif developer_name == 'danny':
    var_pathex = [r'C:\Users\yuxingh\dev\iot-inspector-client\src']
    var_datas = [(r'C:\Users\yuxingh\dev\iot-inspector-client\env\Lib\site-packages\netdisco\discoverables\*', 'netdisco\discoverables')]
else:
    raise RuntimeError('developer_name not set!')


a = Analysis(['start_inspector.py'],
             pathex=var_pathex,
             binaries=[],
             datas=var_datas,
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
