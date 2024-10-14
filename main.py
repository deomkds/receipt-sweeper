import os
import time
import shutil
import pdf2image
import subprocess
import pytesseract
import ollama
from enum import Enum
from PIL import Image
from pypdf import PdfReader, PdfWriter
from datetime import datetime
from pathlib import Path


class Banks(Enum):
    Unknown = 0
    Nubank = 1
    MercadoPago = 2
    N26 = 3
    Inter = 4
    C6 = 5
    ClaroPay = 6
    XP = 7


def log(text, essential=False, line_break=False):
    if VERBOSE or essential:
        moment_obj = datetime.now()
        moment = moment_obj.strftime("%Y-%m-%d %H:%M:%S")
        path = os.path.join(src_path, 'rename_log.txt')
        br = f"\n" if line_break else f""
        output_line = f"{br}{moment}: {current_file} -> {text}"
        dbgln(output_line)
        with open(path, "a") as log_file:
            log_file.write(f"{output_line}\n")


def dbgln(*args):
    if DEBUG_MODE:
        print(*args)


def save_txt_to_disk(text_data):
    if DEBUG_MODE:
        complete_path = os.path.join(dbg_path, current_file)
        with open(f"{complete_path}.txt", "w") as text_file:
            for text in text_data:
                text_file.write(f"{text}\n")


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


def create_debug_mode_folders(home):
    dirs = ["ocr_dbg",
            "input_files",
            "Bancos"
            ]

    try_rmdir_contents(os.path.join(home, "Desktop", dirs[0]))

    for directory in dirs:
        try_mkdir(os.path.join(home, "Desktop", directory))

    for x in range(len(Banks)):
        try_mkdir(os.path.join(home, "Desktop/Bancos", Banks(x).name))


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


def ocr_image(image_object):
    # For images with white text on dark backgrounds, like N26 receipt.
    background = image_object.getpixel((1, 1))
    threshold = THRESHOLD_LIGHT if background[0] > THRESHOLD_LIMIT else THRESHOLD_DARK

    boosted_image = image_object.convert(mode="L").point(lambda pixel_value: 255 if pixel_value > threshold else 0)

    if DEBUG_MODE:
        complete_path = os.path.join(dbg_path, f"{threshold}_{current_file}")
        boosted_image.save(f"{complete_path}.png")

    log(f"File needs OCR. Threshold: {threshold}.")

    ocr_text = pytesseract.image_to_string(boosted_image, lang="por").split("\n")

    return ocr_text


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


def manual_override(info_type, extracted_text):
    log(f"Cannot identify {info_type}. Asking the user...")

    print("RECEIPT CONTENTS:")
    for line_number, line_contents in enumerate(extracted_text):
        print(f"\t{line_number:>02}: {line_contents}")
    typed_info = input(f"\nType {info_type}: ").strip()

    log(f"User provided {info_type}: '{typed_info}'.")

    return typed_info


def find_position(text_list, text, min_length=0, max_length=9000):
    for count, value in enumerate(text_list):
        value_len = len(value)
        if (text in value) and (value_len >= min_length) and (value_len <= max_length):
            return count

    return -1


def extract_amount(text_list):
    # Some receipts don't come with decimal zeroes. This method adds them.
    amount_line = find_position(text_list, "$", 2, 100)
    amount_in_string = text_list[amount_line].strip()
    value_pos = amount_in_string.find("$") + 2  # Offset for the space that comes after.
    try:
        amount_in_float = float(amount_in_string[value_pos:].replace(".", "").replace(",", ".").replace("?", ""))
    except:
        amount_in_float = 0.0

    return f"R$ {amount_in_float:.2f}".replace(".", ",")


def optimise_png(file_path):
    original_file_size_in_kib = float(os.path.getsize(file_path)) / 1024

    obj_data = subprocess.run(["oxipng", "-s", "-t", "1", "-a", "-p", "-o", "5", file_path], capture_output=True)
    raw_output = obj_data.stderr.decode("utf-8").split("\n")

    try:
        optimised_file_size_in_kib = float(raw_output[1].split(" ")[0]) / 1024
        reduction_percentage = raw_output[1].split(" ")[2][1:-1]
    except ValueError:
        optimised_file_size_in_kib = original_file_size_in_kib
        reduction_percentage = 0

    log(f"PNG file size optimised by {reduction_percentage}%, "
        f"reduced from {original_file_size_in_kib:.2f} KiB to {optimised_file_size_in_kib:.2f} KiB.", True)
    return


def optimise_jpg(file_path):
    original_file_size_in_kib = float(os.path.getsize(file_path)) / 1024

    obj_data = subprocess.run(["jpegoptim", "-p", "-t", "-s", "-w1", file_path], capture_output=True)
    raw_output = obj_data.stdout.decode("utf-8").split("\n")

    try:
        optimised_file_size_in_kib = float(raw_output[0].split(" [OK] ")[1].split(" ")[2]) / 1024
        reduction_percentage = raw_output[0].split(" [OK] ")[1].split(" ")[4][1:-3]
    except ValueError:
        optimised_file_size_in_kib = original_file_size_in_kib
        reduction_percentage = 0

    log(f"JPG file size optimised by {reduction_percentage}%, "
        f"reduced from {original_file_size_in_kib:.2f} KiB to {optimised_file_size_in_kib:.2f} KiB.", True)
    return


def decrypt_pdf(pdf_object, cpf):
    if len(cpf) < 1:
        log("Can't decrypt PDF. Asking the user...")
        pwd = input("Type PDF password: ").strip()
        if pdf_object.decrypt(pwd) == 0:
            log("Wrong password.")
            return False
        else:
            log("PDF decrypted.")
            return True

    log(f"Trying password: '{cpf}'")

    if pdf_object.decrypt(cpf) == 0:
        return decrypt_pdf(pdf_object, cpf[:-1])
    else:
        log("PDF decrypted.")
        return True


def ai_parse(text, info):

    if not USE_AI:
        log(f"AI usage is not enabled.")
        return None

    prompts = {
        "date": f"Com base no texto abaixo, retorne a data em que essa transação aconteceu no formato"
                f"ANO-MÊS-DIA. É importantíssimo e urgente que retorne apenas nesse formato."
                f"Não retorne nenhum texto adicional além da data solicitada.",
        "amount": f"Com base no texto abaixo, retorne o valor dessa transação."
                  f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                  f"Não retorne nenhum texto adicional além do valor solicitado."
                  f"Não retorne ponto final no texto.",
        "bank": f"Com base no texto abaixo, retorne o nome do banco ou da instiuição onde ocorreu essa transação."
                f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                f"Não retorne nenhum texto adicional além do nome solicitado."
                f"Não retorne ponto final no texto.",
        "person1": f"Você está fazendo o reconhecimento de texto de uma imagem."
                   f"Com base no texto abaixo, retorne o nome de quem enviou o dinheiro nessa transação."
                   f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                   f"Não retorne nenhum texto adicional além do nome solicitado.",
        "person2": f"Você está fazendo o reconhecimento de texto de um comprovante de transferência."
                   f"Com base no texto abaixo, retorne o nome de quem recebeu o dinheiro nessa transação."
                   f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                   f"Não retorne nenhum texto adicional além do nome solicitado.",
        "description": f"Com base no texto abaixo, retorne a descrição da transação, se tiver."
                       f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                       f"Não retorne nenhum texto adicional além da descrição solicitada."
    }

    model = ["llama3.2:1b", "llama3.2"]

    response = ollama.chat(model=model[1], messages=[
        {
            'role': 'user',
            'content': f"{prompts[info]}\n\n{text}",
        },
    ])

    answer = response['message']['content']

    log(f"String for '{info}' found using AI: '{answer}'.")
    return answer


class UnknownReceipt:
    def __init__(self, file_path):
        self.file_path = file_path
        self.extracted_text = self.extract_text()
        self.timestamp = self.timestamp_of_file()
        self.bank_guess = self.guess_bank()

    def extract_text(self, force_ocr=False):
        if self.file_path.endswith(".pdf"):
            log("File is a PDF.")

            reader = PdfReader(self.file_path)

            if reader.is_encrypted:
                log("File is encrypted.")

                if not decrypt_pdf(reader, CPF):
                    return None

                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                writer.write(self.file_path)

                # Load decrypted file.
                reader = PdfReader(self.file_path)

            page = reader.pages[0]

            try:  # We have to try here because some PDFs cause PdfReader to crash.
                log("Attempting to read text layer...")
                list_of_text = page.extract_text().split("\n")
                if len(list_of_text) < 2:
                    log("File does not seem to have a text layer, reverting to OCR...")
                    list_of_text = ocr_image(pdf2image.convert_from_path(self.file_path)[0])
                else:
                    if force_ocr:
                        log("Forcing OCR in PDF file...")
                        list_of_text = ocr_image(pdf2image.convert_from_path(self.file_path)[0])
                    else:
                        log("File has text layer, no OCR needed.")
            except IndexError:
                log("PdfReader crashed, reverting to OCR...")
                list_of_text = ocr_image(pdf2image.convert_from_path(self.file_path)[0])
        else:
            log("File is an image, OCR will be used.")
            list_of_text = ocr_image(Image.open(self.file_path))

        clean_list_of_text = [text for text in list_of_text if text.strip()]
        save_txt_to_disk(clean_list_of_text)

        return clean_list_of_text

    def guess_bank(self):
        detected_bank = self.detect_bank()
        if (detected_bank == Banks.Unknown) and (self.file_path.endswith(".pdf")):
            log("Couldn't identify bank from PDF, forcing OCR...")
            self.extracted_text = self.extract_text(True)
            detected_bank = self.detect_bank()

        return detected_bank

    def detect_bank(self):
        try:
            common_text = self.extracted_text[0]
        except IndexError:
            return Banks.Unknown

        id_string = f"{self.extracted_text[0].lower()}{self.extracted_text[1].lower()}"

        log(f"String used to identify bank: '{id_string}'.")

        ai_parse(self.extracted_text, "bank")
        ai_parse(self.extracted_text, "date")
        ai_parse(self.extracted_text, "amount")
        ai_parse(self.extracted_text, "person1")
        ai_parse(self.extracted_text, "person2")

        if len(self.extracted_text) < 2:
            return Banks.Unknown
        elif (common_text == "NU") or ("Olá" in common_text):
            return Banks.Nubank
        elif "mercado" in common_text:  # or "Comprovante" in self.extracted_text[0]:
            return Banks.MercadoPago
        elif "N26" in common_text:
            return Banks.N26
        elif "aunterpix" in id_string:
            return Banks.Inter
        elif "cobank" in id_string or "c6bank" in id_string:
            return Banks.C6
        else:
            return Banks.Unknown

    def timestamp_of_file(self):
        file_modification_time = os.path.getmtime(self.file_path)  # In seconds since epoch.
        timestamp_string = time.ctime(file_modification_time)  # As a timestamp string.
        time_object = time.strptime(timestamp_string)  # To a timestamp object.
        return time.strftime("%Y %m %d", time_object)  # To my format.


class Nubank:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = Banks(1).name
        self.type = self.determine_type()
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        # Nubank's receipts are too messy for this.
        self.sender_full_name = ""
        self.sender_first_name = ""
        self.sender_bank = ""

        self.receiver_full_name = ""
        self.receiver_first_name = ""
        self.receiver_bank = ""

    def determine_extension(self):
        split_tuple = os.path.splitext(self.file_path)
        return split_tuple[1]

    def determine_type(self):
        field = self.extracted_text[2].lower()

        if "pagamento" in field:
            return "Comprovante de Pagamento"
        elif "transferência" in field:
            return "Comprovante de Transferência"
        elif "agendamento" in field:
            return "Comprovante de Agendamento"
        elif "no valor de" in field:
            return "Fatura"
        else:
            return "Outro"

    def determine_amount(self):
        return extract_amount(self.extracted_text)

    def determine_description(self):
        start_pos = 0
        end_pos = 0
        description = ""

        if self.type == "Fatura":
            log("Description for predefined type: 'Fatura'.")
            return "Fatura"

        if self.type == "Comprovante de Pagamento":
            log("Description for predefined type: 'Fatura do Cartão Nubank (App)'.")
            return "Fatura do Cartão Nubank (App)"

        for i in range(5, len(self.extracted_text)):
            if self.extracted_text[i].find("Descrição") >= 0:
                start_pos = i + 1
                continue

            if self.extracted_text[i].find("Destino") >= 0:
                end_pos = i
                break

        if start_pos == 0:
            return manual_override("description", self.extracted_text)

        for j in range(start_pos, end_pos):
            description += self.extracted_text[j]

        log(f"Description auto detected: '{description}'.")

        return description


class MercadoPago:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = Banks(2).name
        self.type = self.extracted_text[2]
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_first_name = self.determine_info("sender", "first_name")
        self.sender_full_name = self.determine_info("sender", "full_name")
        self.sender_bank = self.determine_info("sender", "bank")

        self.receiver_first_name = self.determine_info("receiver", "first_name")
        self.receiver_full_name = self.determine_info("receiver", "full_name")
        self.receiver_bank = self.determine_info("receiver", "bank")

    def determine_info(self, party, info_type):
        if party == "sender":
            magic_number = find_position(self.extracted_text, "De", 2, 5)
        else:
            magic_number = find_position(self.extracted_text, "Para", 4, 7)

        log(f"Magic number found for {party}: {magic_number}.")

        if info_type == "first_name":
            info = self.extracted_text[magic_number + 1].title().split(" ")[0].strip()
        elif info_type == "full_name":
            info = self.extracted_text[magic_number + 1].title()
        else:
            info = self.extracted_text[magic_number + 3].title()

        log(f"Detected {party} {info_type}: {info}")
        return info

    def determine_extension(self):
        split_tuple = os.path.splitext(self.file_path)
        return split_tuple[1]

    def determine_description(self):
        description = self.extracted_text[5].strip()

        if (description == "De") or ("R$" in description):
            return manual_override("description", self.extracted_text)

        log(f"Description auto detected: '{description}'.")

        if description.endswith("."):
            return description[:-1]
        else:
            return description

    def determine_amount(self):
        return extract_amount(self.extracted_text)


class C6:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = Banks(5).name
        self.type = self.determine_type()
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_first_name = self.determine_info("sender", "first_name")
        self.sender_full_name = self.determine_info("sender", "full_name")
        self.sender_bank = self.determine_info("sender", "bank")

        self.receiver_first_name = self.determine_info("receiver", "first_name")
        self.receiver_full_name = self.determine_info("receiver", "full_name")
        self.receiver_bank = self.determine_info("receiver", "bank")

    def determine_type(self):
        field = f"{self.extracted_text[1].lower()}{self.extracted_text[2].lower()}"

        if "pagamento" in field:
            return "Fatura"
        else:
            return "Outro"

    def determine_info(self, party, info_type):
        if self.type == "Fatura":
            return "Banco C6 S.A."

        banks = []
        for pos, line in enumerate(self.extracted_text):
            if "Banco: " in line:
                banks.append(pos)

        banks_index = 1 if party == "sender" else 0

        if info_type == "full_name":
            return self.extracted_text[banks[banks_index] - 1]
        elif info_type == "first_name":
            return self.extracted_text[banks[banks_index] - 1].split(" ")[0]
        else:  # info_type == "bank"
            clean_name = self.extracted_text[banks[banks_index]].split("-")[1].strip()
            return clean_name

    def determine_extension(self):
        split_tuple = os.path.splitext(self.file_path)
        return split_tuple[1]

    def determine_description(self):
        if self.type == "Fatura":
            return "Fatura do Cartão C6 (App)"

        # It has to be a manual override because I can't type descriptions on my phone.
        return manual_override("description", self.extracted_text)

    def determine_amount(self):
        return extract_amount(self.extracted_text)


class Inter:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = Banks(4).name
        self.type = self.extracted_text[2]
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_first_name = self.determine_info("sender", "first_name")
        self.sender_full_name = self.determine_info("sender", "full_name")
        self.sender_bank = self.determine_info("sender", "bank")

        self.receiver_first_name = self.determine_info("receiver", "first_name")
        self.receiver_full_name = self.determine_info("receiver", "full_name")
        self.receiver_bank = self.determine_info("receiver", "bank")

    def determine_info(self, party, info_type):
        if party == "sender":
            magic_number = self.extracted_text.index("Quem pagou")
        else:
            magic_number = self.extracted_text.index("Quem recebeu")

        if info_type == "first_name":
            info = self.extracted_text[magic_number + 1].title().split(" ")[1].strip()
        elif info_type == "full_name":
            info = self.extracted_text[magic_number + 1].title()[5:]
        else:
            # Bank name.
            info = self.extracted_text[magic_number + 3].title()[12:]

        log(f"Detected {party} {info_type}: {info}")
        return info

    def determine_extension(self):
        split_tuple = os.path.splitext(self.file_path)
        return split_tuple[1]

    def determine_description(self):
        message = self.extracted_text[8]
        if "Descri" in message:
            descript = message[10:]
            log(f"Description auto detected: '{descript}'.")
            return descript
        else:
            return manual_override("description", self.extracted_text)

    def determine_amount(self):
        return extract_amount(self.extracted_text)


class N26:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = Banks(3).name
        self.type = self.extracted_text[3]
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        # Not enough data to precisely determine this information.
        self.sender_first_name = ""
        self.sender_full_name = ""
        self.sender_bank = ""

        self.receiver_first_name = ""
        self.receiver_full_name = ""
        self.receiver_bank = ""

    def determine_extension(self):
        split_tuple = os.path.splitext(self.file_path)
        return split_tuple[1]

    def determine_description(self):
        return manual_override("description", self.extracted_text)

    def determine_amount(self):
        return extract_amount(self.extracted_text)


CPF = "15870465710"
THRESHOLD_DARK = 60
THRESHOLD_LIGHT = 220
THRESHOLD_LIMIT = 200
DEBUG_MODE = False
VERBOSE = DEBUG_MODE
DRY_RUN = DEBUG_MODE
OCR_ONLY = False
OPTIMISE = True
USE_AI = False

current_file = ""
home_dir = Path.home()

if DEBUG_MODE:
    dbg_path = os.path.join(home_dir, "Desktop/ocr_dbg/")
    src_path = os.path.join(home_dir, "Desktop/input_files/")
    dst_path = os.path.join(home_dir, "Desktop/Bancos/")
    create_debug_mode_folders(home_dir)
    options = "debug mode"
    if OCR_ONLY:
        options += ", ocr only"
    if DRY_RUN:
        options += ", dry run"
else:
    src_path = os.path.join(home_dir, "OneDrive/")
    dst_path = os.path.join(home_dir, "OneDrive/Documentos/Bancos/")
    options = "normal mode"

log(f"EXECUTION STARTED ({options})", True)

list_of_files = list_files_in(src_path)
total_file_num = len(list_of_files)

for file_num, file in enumerate(list_of_files):

    current_file = file.name

    log(f"Processing file {file_num + 1} of {total_file_num}: '{current_file}'", True, True)

    unknown_receipt = UnknownReceipt(file.path)

    if OCR_ONLY and DEBUG_MODE:
        log("OCR only mode enabled.")
        continue

    if unknown_receipt.bank_guess == Banks.MercadoPago:
        receipt = MercadoPago(unknown_receipt)
    elif unknown_receipt.bank_guess == Banks.Nubank:
        receipt = Nubank(unknown_receipt)
    elif unknown_receipt.bank_guess == Banks.N26:
        receipt = N26(unknown_receipt)
    elif unknown_receipt.bank_guess == Banks.Inter:
        receipt = Inter(unknown_receipt)
    elif unknown_receipt.bank_guess == Banks.C6:
        receipt = C6(unknown_receipt)
    else:
        receipt = None
        log(f"[ERROR] Couldn't identify bank. Skipping...", True)
        continue

    log(f"Receipt belongs to {receipt.bank}.")

    full_dst_path = os.path.join(dst_path, receipt.folder)
    sender = receipt.sender_first_name
    receiver = receipt.receiver_first_name

    if sender == receiver:
        sender = receipt.sender_bank
        receiver = receipt.receiver_bank

    amount = format_amount(receipt.amount)
    parties = format_parties(sender, receiver)

    new_file_name = f"{receipt.timestamp} {receipt.description}{amount}{parties}{receipt.extension}"

    final_path = os.path.join(full_dst_path, new_file_name)

    try:
        if not DRY_RUN:
            os.rename(file.path, final_path)
            if OPTIMISE:
                log(f"Optimisation enabled.")
                if receipt.extension.startswith(".pn"):
                    log(f"Optimising with 'oxipng'...")
                    optimise_png(final_path)
                elif receipt.extension.startswith(".jp"):
                    log(f"Optimising with 'jpegoptim'...")
                    optimise_jpg(final_path)
                else:
                    log(f"File is not JPEG or PNG. Leaving as is...", True)
        else:
            log("Dry run enabled. No changes will be made to the filesystem.")
        log(f"Renamed to {new_file_name}!", True)
    except IsADirectoryError:
        log(f"[ERROR] Destination + New File Name is a directory: {final_path}.", True)
    except PermissionError:
        log(f"[ERROR] Operation not permitted.", True)
    except OSError as error:
        log(f"[ERROR] {error}", True)

# input("Execution finished. Press Enter to quit.")
