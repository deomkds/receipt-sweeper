import os
from simplelog import log
from enum import Enum

class BankNames(Enum):
    Unknown = 0
    Nubank = 1
    MercadoPago = 2
    N26 = 3
    Inter = 4
    C6 = 5
    Claro = 6
    XP = 7      # Not implemented yet.
    Genial = 8

def manual_override(info_type, extracted_text, default_info="Descrição Não Informada"):
    print("RECEIPT CONTENTS:")
    for line_number, line_contents in enumerate(extracted_text):
        print(f"\t{line_number:>02}: {line_contents}")

    typed_info = input(f"\nType {info_type}: ").strip()

    if typed_info == "":
        return default_info
    else:
        log(f"User provided {info_type}: '{typed_info}'.")
        return typed_info

def extract_amount(text_list, start_pos=0):
    # Some receipts come without decimal zeroes. This method adds them.
    amount_pos = find_position(text_list, "$", 2, 100, start_pos=start_pos)

    amount_string = text_list[amount_pos].strip()
    value_pos = amount_string.find("$") + 2  # Offset for the space that comes after.
    try:
        amount = float(amount_string[value_pos:].replace(".", "").replace(",", ".").replace("?", ""))
    except:
        amount = 0.0
    return f"R$ {amount:.2f}".replace(".", ",")

def find_position(text_list, text, min_length=0, max_length=9000, start_pos=0):
    for count, value in enumerate(text_list):
        value_len = len(value)
        if (text in value) and (value_len >= min_length) and (value_len <= max_length) and (count >= start_pos):
            return count
    return -1

def extract_extension(file_path):
    return os.path.splitext(file_path)[1]