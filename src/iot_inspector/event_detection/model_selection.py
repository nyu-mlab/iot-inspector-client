import os
import logging
import gdown
import zipfile
import requests
import certifi
from functools import lru_cache

# This file aims to provide a set of functions to 
from difflib import SequenceMatcher

# This files aims to provide a set of functions to 
# perform model selection for a device based on the
# data available in the database.
logger = logging.getLogger(__name__)

# Configuration
GOOGLE_DRIVE_ID = "15ZyxyqzhO-tDaBYgwo3vpM9cMq7XfanR"
# This path leads to: .../models/binary/rf/
MODELS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'models', 'binary', 'rf')
# The root folder where the zip should be extracted (one level above 'models')
PACKAGE_ROOT = os.path.abspath(os.path.join(MODELS_DIR, '..', '..', '..'))


# TODO: We probably should use 'platformdirs' on PyPi, but for now, this works...
def download_models():
    """
    Downloads models from Google Drive and extracts them.
    """
    if os.path.exists(MODELS_DIR):
        return

    logger.warning(f"Models directory not found at {MODELS_DIR}.")
    zip_path = os.path.join(PACKAGE_ROOT, "models.zip")

    # 1. Download from Google Drive
    logger.info(f"Downloading models to {zip_path}...")
    url = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_ID}"
    try:
        gdown.download(url, zip_path, quiet=False, verify=certifi.where())
    except requests.exceptions.ConnectionError:
        logger.error("Network unreachable. Check your internet connection or Caddy proxy.")
        return
    except requests.exceptions.Timeout:
        logger.error("Download timed out. The server is taking too long to respond.")
        return
    except PermissionError:
        logger.error(f"Cannot write to {zip_path}. Check folder permissions (OneDrive locking issue?).")
        return
    except Exception:
        # This is for the 'weird' stuff (like the certifi error or disk full)
        logger.exception("Unexpected failure during model download")
        return
    # Extract using native zipfile
    if os.path.exists(zip_path):
        logger.info("Extracting models...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # We extract into PACKAGE_ROOT assuming zip contains 'models/binary/rf/...'
            zip_ref.extractall(PACKAGE_ROOT)
        os.remove(zip_path)
        logger.info("Models successfully installed.")
    else:
        logger.error("Download failed; models.zip not found.")


@lru_cache(maxsize=128)
def import_models():
    # Import all models from the models directory
    # and return them as a list of models

    #  Check if the models directory exists
    if not os.path.exists(MODELS_DIR):
        logger.warning(f"Models directory not found at {MODELS_DIR}. Please ensure the models are downloaded and placed in the correct directory.")
        download_models()
        return []

    model_folders = [name for name in os.listdir(MODELS_DIR) if os.path.isdir(os.path.join(MODELS_DIR, name))]
    return model_folders


def is_close_match(str1: str, str2: str, threshold=0.75) -> int:
    match_score = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return 1 if match_score > threshold else 0


@lru_cache(maxsize=128)
def find_best_match(device_name: str, model_names=None, threshold: float = 0.75):
    best_match = None
    highest_score = 0

    if not model_names:
        model_names = import_models()

    for model_name in model_names:
        match_score = SequenceMatcher(None, device_name.lower(), model_name.lower()).ratio()
        if match_score > highest_score:
            highest_score = match_score
            best_match = model_name

    if highest_score > threshold:
        return device_name, best_match
    else:
        return device_name, "unknown"
 

def main():
    test_cases = [
        ("Hello World", "hello_world", 0.8),
        ("Hello", "H3llo", 0.6),
        ("Python", "Java", 0.5),
        ("GitHub", "GitLab", 0.7)
    ]

    for str1, str2, threshold in test_cases:
        result = is_close_match(str1, str2, threshold)
        print(f"Comparing '{str1}' with '{str2}' at threshold {threshold}: {result}")


if __name__ == "__main__":
    main()
