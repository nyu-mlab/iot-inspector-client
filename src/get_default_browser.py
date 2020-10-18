import plistlib
import subprocess

def get_default_browser():
    subprocess.call(['./cp_plist.sh'], shell=True)
    with open('com.apple.launchservices.secure.plist', 'rb') as fp:
        pl = plistlib.load(fp)

    words = ['com', '.','apple', 'google', 'browser']
    default_browser = ''
    for i in pl['LSHandlers']:
        for j in i.values():
            if j == 'http':
                default_browser = i['LSHandlerRoleAll']
                for word in words:
                    default_browser =default_browser.replace(word, '')
    return default_browser
print(get_default_browser)