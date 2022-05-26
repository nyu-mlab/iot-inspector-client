import os 


def get_current_file_dir() -> str:
    """Returns the directory of the current file."""

    return os.path.dirname(os.path.realpath(__file__))


def get_config_dir() -> str:
    """Returns the directory with Inspector's configs."""

    return ''