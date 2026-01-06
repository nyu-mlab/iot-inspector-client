import subprocess
import os
import sys
from typing import Dict


def run_ls_command(path: str = ".") -> str:
    """
    Runs the 'ls -alR' command on the specified path and captures the output.

    Args:
        path: The directory to start the recursive listing from. Defaults to the current directory.

    Returns:
        The stdout output of the command as a string, or an empty string if the command fails.
    """
    print(f"Executing: ls -alR {path}...")
    try:
        # We run 'ls -alR' on the current directory ('.').
        # capture_output=True collects stdout and stderr.
        # text=True decodes the output to a Python string.
        result = subprocess.run(
            ['ls', '-alR', path],
            capture_output=True,
            text=True,
            check=True,  # Raise an exception for non-zero exit codes
            encoding='utf-8'
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Handles errors like 'directory not found' or permission issues
        print(f"Error executing ls -alR: {e}")
        print(f"Stderr: {e.stderr}")
        return ""
    except FileNotFoundError:
        print("Error: 'ls' command not found. Is it installed and in your PATH?")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""


def get_label_summary(ls_output: str, user_dir_name: str) -> Dict[str, int]:
    """
    Parses the ls -alR output string to count the number of files
    in each 'Device/Activity Label' directory.

    This function is generic and relies on counting the directory depth (slashes)
    to correctly identify the Device and Activity Label names.

    Args:
        ls_output: The string output of the recursive directory listing.
        user_dir_name: The top-level user directory name to strip from the path.

    Returns:
        A dictionary mapping "Device:Label" -> file_count.
    """
    summary_data = {}
    current_device = None
    current_label = None
    file_count = 0

    lines = ls_output.strip().split('\n')

    for line in lines:
        line = line.strip()

        # 1. Identify Directory Header (start of a new counting block)
        # Directory lines end with ':' and must contain the user's base directory name
        if line.endswith(":") and user_dir_name in line:

            # Check for the Device/Label level (3rd level deep, meaning at least 2 slashes)
            if line.count(os.path.sep) >= 2:
                # Store the count for the PREVIOUS label before starting a new one
                if current_device and current_label and file_count > 0:
                    key = f"{current_device}:{current_label}"
                    summary_data[key] = file_count

                # Reset counter for the new label
                file_count = 0

                # Extract the path, removing surrounding quotes and the trailing ':'
                path_section = line.replace("'", "").rstrip(':')

                # Split the path into components
                parts = path_section.split(os.path.sep)

                # The Device is parts[-2], the Label is parts[-1].
                if len(parts) >= 3:
                    current_device = parts[-2]
                    current_label = parts[-1]
                else:
                    # Ignore high-level directories
                    current_device = None
                    current_label = None
            else:
                 # Ignore high-level directories (User/ or User/Device)
                current_device = None
                current_label = None

        # 2. Identify Files (lines starting with '-' indicating a file, not a directory 'd')
        elif line.startswith('-') and current_device and current_label:
            # A file found under an identified Device/Label directory
            file_count += 1

    # 3. Handle the count for the very last directory processed
    if current_device and current_label and file_count > 0:
        key = f"{current_device}:{current_label}"
        summary_data[key] = file_count

    return summary_data


def format_summary_for_user(summary_data: Dict[str, int]) -> str:
    """
    Formats the dictionary data into a clean, readable message for the user.
    """
    if not summary_data:
        return "No completed label files found in the directory structure."

    formatted_lines = []

    # Sort the output by device name for readability
    for full_label, count in sorted(summary_data.items()):
        try:
            # Split only on the first colon to handle activity labels that might contain colons
            device, activity_label = full_label.split(':', 1)
            formatted_lines.append(f"- **{device}**: \"{activity_label}\" ({count} files)")
        except ValueError:
             formatted_lines.append(f"- **{full_label}**: ({count} files) (Parsing Error)")


    header = "### ✅ Completed Labeling Status\n"
    header += "I've checked the directory structure and here are the current file counts for each activity label:\n"

    return header + "\n" + "\n".join(formatted_lines)


# --- Execution ---
if __name__ == "__main__":
    if len(sys.argv) != 2:
        user = 'AndrewQuijano'
    else:
        user = sys.argv[1]
    # 1. Run the command to get the live output
    live_ls_output = run_ls_command(os.path.join('packets', user))

    # 2. Check if we got any output
    if not live_ls_output:
        print("\nCould not retrieve directory listing. Cannot generate summary.")
    else:
        # 3. Process the live output
        label_counts = get_label_summary(live_ls_output, user)

        print("\n--- Python Dictionary Output (Ready for internal use) ---")
        print(label_counts)

        print("\n--- Formatted Message for User ---")
        user_message = format_summary_for_user(label_counts)
        print(user_message)