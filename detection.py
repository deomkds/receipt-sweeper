# Builtin
import os
import time
# Third party.
import pdf2image
import pytesseract
from PIL import Image
from pypdf import PdfReader, PdfWriter
# First party.
import config
import debug
from simplelog import log
from bank.info import BankNames as Banks  # Too lazy to refactor?


def ocr_image(image_object):
    # For images with white text on dark backgrounds, like N26 receipt.
    background = image_object.getpixel((1, 1))
    threshold = config.THRESHOLD_LIGHT if background[0] > config.THRESHOLD_LIMIT else config.THRESHOLD_DARK

    boosted_image = image_object.convert(mode="L").point(lambda pixel_value: 255 if pixel_value > threshold else 0)

    if config.DEBUG_MODE:
        complete_path = os.path.join(config.dbg_path, f"{threshold}_{config.current_file}")
        boosted_image.save(f"{complete_path}.png")

    log(f"File needs OCR. Threshold: {threshold}.")

    ocr_text = pytesseract.image_to_string(boosted_image, lang="por").split("\n")

    return ocr_text

def brute_force_pwd(pdf_object, digits):
    if not config.BRUTE_FORCE_PWD:
        log(f"Brute forcing PDF password is disabled.")
        return False

    log(f"Brute forcing PDF password...")
    top = int("9" * digits)
    for pwd in range(0, top):
        if pdf_object.decrypt(f"{pwd:0{digits}d}") != 0:
            log("PDF decrypted.")
            return True

    log("Wrong password.")
    return False

def decrypt_pdf(pdf_object, cpf):
    if len(cpf) < 1:
        log("Can't decrypt PDF. Brute forcing with 5 digits...")
        if brute_force_pwd(pdf_object, digits=5):
            return True

        log("Can't decrypt PDF. Brute forcing with 6 digits...")
        if brute_force_pwd(pdf_object, digits=6):
            return True

        log("Can't decrypt PDF. 😧 Asking the user...")
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

                if not decrypt_pdf(reader, config.CPF):
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
        debug.save_txt_to_disk(clean_list_of_text)

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
        elif "sucesso!valor" in id_string:
            return Banks.Claro
        elif "genial" in id_string:
            return Banks.Genial
        else:
            return Banks.Unknown

    def timestamp_of_file(self):
        file_modification_time = os.path.getmtime(self.file_path)  # In seconds since epoch.
        timestamp_string = time.ctime(file_modification_time)  # As a timestamp string.
        time_object = time.strptime(timestamp_string)  # To a timestamp object.
        return time.strftime("%Y %m %d", time_object)  # To my format.