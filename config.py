import os
import debug
from pathlib import Path

# PDF password remover.
# Algumas faturas de cartão de crédito são protegidas por senha.
# Essa senha costuma ser os 5 ou 6 primeiros digitos do CPF.
# Coloque sua senha aqui para o script desbloquear essas faturas automaticamente.
# Também é possível usar o CPF inteiro. O script vai removendo um número até desbloquear.
# Caso não haja senha ou CPF, o script tentará desbloquear o boleto na força bruta.
# Ou seja, gerando todos os números de 5 e 6 dígitos e tentando cada um deles.
# Se nada disso der certo, o script pedirá a inserção manual da senha.
CPF = "15870465710"
BRUTE_FORCE_PWD = True  # Brute forcing the password can be slow. Setting this to False will disable it.

# OCR settings.
THRESHOLD_DARK = 60
THRESHOLD_LIGHT = 220
THRESHOLD_LIMIT = 200

# Other settings.
OPTIMISE = True  # Reduce file sizes.
USE_AI = True   # Uses AI to interpret receipt contents. Requires ollama installed and running.
OCR_ONLY = False # Performs only the OCR to facilitate the creation of new bank classes.

DEBUG_MODE = True

VERBOSE = DEBUG_MODE
DRY_RUN = DEBUG_MODE

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