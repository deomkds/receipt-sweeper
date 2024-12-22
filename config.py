import os
import debug
from pathlib import Path

# PDF password remover.
# Some credit card statements are password-protected.
# The password is usually the first 5 or 6 digits of your CPF.
# Provide the password or full CPF for automatic unlocking.
# If no password or CPF is given, the script will try every 5- and 6-digit combination.
# If all attempts fail, you'll be asked to enter the password manually.

# Removedor de senha de PDF.
# Algumas faturas de cartão de crédito são protegidas por senha.
# A senha geralmente corresponde aos primeiros 5 ou 6 digitos do CPF.
# Informe a senha ou o CPF completo para remoção automática.
# Caso nenhuma senha ou CPF seja informado, o script tentará todas as combinações possíveis.
# Caso a força bruta falhe, o script solicitará a senha ao usuário.
CPF = ""
BRUTE_FORCE_PWD = True  # Desativar a força bruta | disable brute force.

# File size optimization.
# Redução de tamanho de arquivo.
OPTIMISE = True  # Reduzir o tamanho dos arquivos | reduce file sizes.

# Relative file paths.
# Caminhos relativos à pasta `home`.
PASTA_ORIGEM  = "OneDrive/"
PASTA_DESTINO = "OneDrive/Documentos/Bancos/"

# ================================== NÃO ALTERE AS CONFIGURAÇÕES A PARTIR DESSA LINHA ==================================

# Debug settings, don't change.
DEBUG_MODE = False # Enables debug mode.
OCR_ONLY = False # Performs OCR and saves the extracted text to help with debugging.
VERBOSE = DEBUG_MODE # Log everything!
DRY_RUN = DEBUG_MODE # With dry run enabled, no changes are committed to disk.

# OCR settings. Don't change.
THRESHOLD_DARK = 60
THRESHOLD_LIGHT = 220
THRESHOLD_LIMIT = 200

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
    src_path = os.path.join(home_dir, PASTA_ORIGEM)
    dst_path = os.path.join(home_dir, PASTA_DESTINO)
    options = "normal mode"