# Builtin.
import os
import shutil
# First party.
import config
from bank.info import BankNames

def save_txt_to_disk(text_data):
    if config.DEBUG_MODE:
        complete_path = os.path.join(config.dbg_path, config.current_file)
        with open(f"{complete_path}.txt", "w") as text_file:
            for text in text_data:
                text_file.write(f"{text}\n")

def create_debug_mode_folders(home):
    dirs = ["ocr_dbg",
            "input_files",
            "Bancos"
            ]

    try_rmdir_contents(os.path.join(home, "Desktop", dirs[0]))

    for directory in dirs:
        try_mkdir(os.path.join(home, "Desktop", directory))

    for x in range(len(BankNames)):
        try_mkdir(os.path.join(home, "Desktop/Bancos", BankNames(x).name))


def try_mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def try_rmdir_contents(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass