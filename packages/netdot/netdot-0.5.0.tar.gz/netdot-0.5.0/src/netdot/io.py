"""Functions that help with Input/Output, e.g. to filesystem or network.
"""
import os


def ensure_directory_exist(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
