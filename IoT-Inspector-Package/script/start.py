"""
Entry point for Inspector 2 for Windows.

Manually start: ..\.bundle\python\python.exe start.py

"""
import subprocess as sp
import os
import urllib.request
import time


current_file_path = os.path.dirname(os.path.abspath(__file__))

BUNDLE_PATH = os.path.join(
    current_file_path,
    '..',
    '3rd-party-software'
)

GIT_BUNDLE_EXE_PATH = os.path.join(BUNDLE_PATH, 'PortableGit-2.41.0.3-64-bit.7z.exe')
GIT_BASE_DIR = os.path.join(BUNDLE_PATH, 'git')
GIT_EXE_PATH = os.path.join(GIT_BASE_DIR, 'bin', 'git.exe')
NPCAP_INSTALLER_PATH = os.path.join(BUNDLE_PATH, 'npcap-1.76.exe')
PYTHON_PATH = os.path.join(BUNDLE_PATH, 'python', 'tools', 'python.exe')
INSPECTOR_PATH = os.path.join(current_file_path, 'iot-inspector-client')



INSPECTOR_URL = 'http://localhost:33761/inspector_dashboard'
GITHUB_REPO_URL = 'https://github.com/nyu-mlab/iot-inspector-client.git'


def main():

    # Quit if Inspector is already running
    try:
        urllib.request.urlopen(INSPECTOR_URL)
    except Exception:
        pass
    else:
        print('IoT Inspector is already running. Aborted.')
        return

    # Check if git is installed
    if not os.path.isfile(GIT_EXE_PATH):
        print('Setting up portable Git...')
        if not os.path.isdir(GIT_BASE_DIR):
            os.mkdir(GIT_BASE_DIR)
        sp.call([GIT_BUNDLE_EXE_PATH, '-o', GIT_BASE_DIR, '-y'])

    # Check if npcap is installed
    npcap_path = os.path.join(os.environ['WINDIR'], 'System32', 'Npcap')
    if not os.path.isdir(npcap_path):
        print('Setting up Npcap...')
        sp.call(
            f"""powershell Start-Process -FilePath '{NPCAP_INSTALLER_PATH}' -Verb RunAs""",
            shell=True
        )
        while not os.path.isdir(npcap_path):
            time.sleep(5)
            print('Waiting for Npcap to be installed...')

    # Init the git repo
    if not os.path.exists(INSPECTOR_PATH):
        print('Downloading the latest version of IoT Inspector...')
        # Check if there is a file called DEBUG.txt in the current directory
        # If so, use the test repo for debugging and testing
        if os.path.isfile(os.path.join(current_file_path, 'DEBUG.txt')):
            sp.call([GIT_EXE_PATH, 'clone', '--depth', '1', '--branch', 'inspector2-dev', GITHUB_REPO_URL])
        else:
            sp.call([GIT_EXE_PATH, 'clone', '--depth', '1', GITHUB_REPO_URL])

    # Update the git repo by pulling
    os.chdir(INSPECTOR_PATH)
    sp.call([GIT_EXE_PATH,  'pull'])

    # Install the dependencies
    print('Installing dependences...')
    os.chdir(INSPECTOR_PATH)
    sp.call([
        PYTHON_PATH,
        '-m', 'pip', 'install', '-r',
        os.path.join(INSPECTOR_PATH, 'requirements.txt'),
        '--no-warn-script-location'
    ])

    # Start Inspector in a separte browser window
    print('Starting IoT Inspector...')
    ui_dir = os.path.join(INSPECTOR_PATH, 'ui')
    sp.call(
        f"""cd "{ui_dir}" && powershell Start-Process -FilePath '{PYTHON_PATH}' -Verb RunAs -ArgumentList '-m streamlit run Device_List.py --server.port 33761 --browser.gatherUsageStats false --server.headless true --server.baseUrlPath inspector_dashboard'""",
        shell=True
    )

    # Wait for the Inspector to start on the port
    for _ in range(60):
        print('Waiting for IoT Inspector to start...')
        time.sleep(1)
        try:
            urllib.request.urlopen(INSPECTOR_URL)
            break
        except Exception:
            continue

    print('IoT Inspector started.')
    sp.call(f'start {INSPECTOR_URL}', shell=True)


if __name__ == '__main__':
    main()