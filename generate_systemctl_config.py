"""
Generates a systemd service configuration file for a Python application, and deploys and installs it at the systemd directory.

Must be run with root privileges, e.g.,

```
sudo $(which uv) run generate_systemctl_config.py
```

Usage: Edit the template below and run it with `uv` in the same directory as this script.

"""
import sys
import os
import subprocess


service_file_content = f"""
[Unit]
Description=IoT Inspector Packet Collector
After=network.target

[Service]
# ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 src.iot_inspector.server.packet_collector:app 
ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --access-logformat '%%(h)s "%%(r)s" %%(s)s %%(b)s' src.iot_inspector.server.packet_collector:app
WorkingDirectory={os.path.dirname(os.path.abspath(__file__))}
User={os.getenv("SUDO_USER", "root")}
Environment=PYTHONUNBUFFERED=1

# Restart service automatically if it crashes
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

"""

def main():
    # Check if the script is run with root privileges
    if os.geteuid() != 0:
        print("This script must be run with root privileges.")
        sys.exit(1)

    # Write the service file to the systemd directory
    systemd_dir = "/etc/systemd/system"
    service_name = "iot-inspector-packet-collector.service"
    service_file_path = os.path.join(systemd_dir, service_name)
    with open(service_file_path, "w") as f:
        f.write(service_file_content)

    commands = [
        ["systemctl", "daemon-reload"],
        ["systemctl", "enable", service_name],
        ["systemctl", "start", service_name],
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Command {' '.join(cmd)} failed (exit {e.returncode}): {e.stderr.strip()}")
            sys.exit(e.returncode)
        else:
            print(f"Success: {' '.join(cmd)}")

if __name__ == "__main__":
    main()