import os 


def get_current_file_dir():
    """Returns the directory of the current file."""

    return os.path.dirname(os.path.realpath(__file__))
