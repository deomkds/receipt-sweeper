import os
import debug
from pathlib import Path

# PDF password remover.
# Some credit card statements are password-protected.
# The password is usually the first 5 or 6 digits of your CPF.
# Provide the password or full CPF for automatic unlocking.
# If no password or CPF is given, the script will try every 5- and 6-digit combination.
# If all attempts fail, you'll be asked to enter the password manually.
CPF = ""
BRUTE_FORCE_PWD = True  # Attempting every combination can be slow. Disable it by changing this to False.

# OCR settings.
THRESHOLD_DARK = 60
THRESHOLD_LIGHT = 220
THRESHOLD_LIMIT = 200

# Other settings.
OPTIMISE = True  # Reduce file sizes.
OCR_ONLY = False # Performs OCR and saves the extracted text to help with debugging.

DEBUG_MODE = False # Enables debug mode.
VERBOSE = DEBUG_MODE # Log everything!
DRY_RUN = DEBUG_MODE # With dry run enabled, no changes are committed to disk.

current_file = ""
home_dir = Path.home()

if DEBUG_MODE:
    dbg_path = os.path.join(home_dir, "Desktop/ocr_dbg/")
    src_path = os.path.join(home_dir, "Desktop/input_files/")
    dst_path = os.path.join(home_dir, "Desktop/Bancos/")
    debug.create_debug_mode_folders(home_dir)
    options = "debug mode"
    if OCR_ONLY:
        options += ", ocr only"
    if DRY_RUN:
        options += ", dry run"
else:
    src_path = os.path.join(home_dir, "OneDrive/")
    dst_path = os.path.join(home_dir, "OneDrive/Documentos/Bancos/")
    options = "normal mode"