import os


def ensure_dirs(directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
