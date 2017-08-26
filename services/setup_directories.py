import os


DIRECTORIES_TO_SET_UP = [
    './reports'
    './cache'
]


def setup_directories():
    for directory in DIRECTORIES_TO_SET_UP:
        if not os.path.exists(directory):
            os.makedirs(directory)
