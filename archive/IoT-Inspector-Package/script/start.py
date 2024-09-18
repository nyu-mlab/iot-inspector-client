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
    first_install = False
    if not os.path.exists(INSPECTOR_PATH):
        first_install = True
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

    # Update pip
    sp.call([
        PYTHON_PATH,
        '-m', 'pip', 'install', '--upgrade', 'pip',
        '--no-warn-script-location'
    ])

    # Actually doing the pip install
    proc = sp.Popen([
        PYTHON_PATH,
        '-m', 'pip', 'install', '-r',
        os.path.join(INSPECTOR_PATH, 'requirements.txt'),
        '--no-warn-script-location'
    ])

    # Show which packages are installed one by one upon first install. This is a
    # length process. We need to provide the user with some visual feedback.
    if first_install:
        print('Installing Python packages, this may take a few minutes...')
        # Extract all the package names from requirements.txt
        all_package_set = set()
        with open(os.path.join(INSPECTOR_PATH, 'requirements.txt'), 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    package_name = line.split('==')[0]
                    all_package_set.add(package_name)
        all_package_count = len(all_package_set)
        # Show which package is installed
        while True:
            # Get the list of installed packages
            installed_package_list = sp.check_output([
                PYTHON_PATH, '-m', 'pip', 'list'
            ]).decode('utf-8').split('\n')
            installed_package_set = set([line.strip().split()[0] for line in installed_package_list if line.strip()])
            package_left_set = all_package_set - installed_package_set
            package_left_count = len(package_left_set)
            percent_complete = int((all_package_count - package_left_count) * 100.0 / all_package_count)
            print('\n' * 80)
            print(f'Installing Python packages - {percent_complete}% complete.')
            print('\n\nThis initial setup process will take several minutes, as we are preparing IoT Inspector to run for the first time. Please be patient. If this process appears to be stuck, it is normal. Please do not close this window.\n')
            if package_left_count == 0 or proc.poll() is not None:
                break
            for _ in range(3):
                # Show an animated character
                for char in ['|', '/', '-', '\\']:
                    print('\r' + char, end='', flush=True)
                    time.sleep(0.5)
    else:
        proc.wait()

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