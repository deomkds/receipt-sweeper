import os
import simplelog as log

def manual_override(info_type, extracted_text):
    log(f"Cannot identify {info_type}. Asking the user...")

    print("RECEIPT CONTENTS:")
    for line_number, line_contents in enumerate(extracted_text):
        print(f"\t{line_number:>02}: {line_contents}")
    typed_info = input(f"\nType {info_type}: ").strip()

    log(f"User provided {info_type}: '{typed_info}'.")

    return typed_info


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


def find_position(text_list, text, min_length=0, max_length=9000):
    for count, value in enumerate(text_list):
        value_len = len(value)
        if (text in value) and (value_len >= min_length) and (value_len <= max_length):
            return count

    return -1


class Nubank:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = "Nubank"
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