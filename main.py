# Builtin
import os
# First party.
import config
from simplelog import log
from optimise import optimise
from bank.info import BankNames as Banks  # Too lazy to refactor?
import detection

# Enabled banks.
from bank.c6 import C6
from bank.inter import Inter
from bank.mercadopago import MercadoPago
from bank.nubank import Nubank
from bank.claro import Claro
from bank.genial import Genial


def list_files_in(path):
    all_files = os.scandir(path)
    receipt_files = []

    for one_file in all_files:
        if one_file.name.endswith(".pdf"):
            receipt_files.append(one_file)
        elif one_file.name.endswith(".png"):
            receipt_files.append(one_file)
        elif one_file.name.endswith(".jpg"):
            receipt_files.append(one_file)

    return receipt_files


def format_amount(value):
    if value != "":
        return f" ({value})"
    else:
        return ""


def format_parties(sender_name, receiver_name):
    if sender_name != "" and receiver_name != "":
        return f" ({sender_name} para {receiver_name})"
    else:
        return ""


def main():
    log(f"EXECUTION STARTED ({config.options})", True)

    list_of_files = list_files_in(config.src_path)
    total_file_num = len(list_of_files)

    for file_num, file in enumerate(list_of_files):

        config.current_file = file.name

        log(f"Processing file {file_num + 1} of {total_file_num}: '{config.current_file}'", True, True)

        unknown_receipt = detection.UnknownReceipt(file.path)

        if config.OCR_ONLY:
            log("OCR only mode enabled.")
            continue

        if unknown_receipt.bank_guess == Banks.MercadoPago:
            receipt = MercadoPago(unknown_receipt)
        elif unknown_receipt.bank_guess == Banks.Nubank:
            receipt = Nubank(unknown_receipt)
        elif unknown_receipt.bank_guess == Banks.Inter:
            receipt = Inter(unknown_receipt)
        elif unknown_receipt.bank_guess == Banks.C6:
            receipt = C6(unknown_receipt)
        elif unknown_receipt.bank_guess == Banks.Claro:
            receipt = Claro(unknown_receipt)
        elif unknown_receipt.bank_guess == Banks.Genial:
            receipt = Genial(unknown_receipt)
        else:
            log(f"[ERROR] Couldn't identify bank. Skipping...", True)
            continue

        log(f"Receipt belongs to {receipt.bank}.")

        full_dst_path = os.path.join(config.dst_path, receipt.folder)
        sender = receipt.sender_first_name
        receiver = receipt.receiver_first_name

        if sender == receiver:
            sender = receipt.sender_bank
            receiver = receipt.receiver_bank

        amount = format_amount(receipt.amount)
        parties = format_parties(sender, receiver)

        new_file_name = f"{receipt.timestamp} {receipt.description}{amount}{parties}{receipt.extension}"

        final_path = os.path.join(str(full_dst_path), str(new_file_name))

        try:
            if config.DRY_RUN:
                log("Dry run enabled. Changes not commited to disk.")
            else:
                os.rename(file.path, final_path)
                optimise(final_path)

            log(f"Renamed to {new_file_name}!", True)

        except IsADirectoryError:
            log(f"[ERROR] Destination + New File Name is a directory: {final_path}.", True)
        except PermissionError:
            log(f"[ERROR] Operation not permitted.", True)
        except OSError as error:
            log(f"[ERROR] {error}", True)


if __name__ == "__main__":
    main()
