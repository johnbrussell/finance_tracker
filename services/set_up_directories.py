import os


DIRECTORIES_TO_SET_UP = [
    './balances',
    './reports/',
    './transactions/unreconciled/'
]


def set_up_directories():
    for directory in DIRECTORIES_TO_SET_UP:
        if not os.path.exists(directory):
            os.makedirs(directory)
