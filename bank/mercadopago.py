from turtledemo.forest import start

from simplelog import log
import bank.info as info

class MercadoPago:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = info.BankNames(2).name
        self.type = self.determine_type()
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_first_name = self.determine_name("sender", "name")
        self.sender_bank = self.determine_name("sender", "bank")

        self.receiver_first_name = self.determine_name("receiver", "name")
        self.receiver_bank = self.determine_name("receiver", "bank")

    def determine_type(self):
        text = f"{self.extracted_text[2]}{self.extracted_text[3]}".lower()

        if "pagamento" in text:
            return "Pagamento"
        elif "fatura" in text:
            return "Fatura"
        else:
            return "Outro"

    def determine_name(self, party, info_type):

        if self.type == "Pagamento" or self.type == "Fatura":
            return ""

        if party == "sender":
            text_id = "De"
        else:
            text_id = "Para"

        full_name_pos = info.find_position(self.extracted_text, text_id, len(text_id), (len(text_id)))
        bank_name_pos = info.find_position(self.extracted_text, "***", 3, start_pos=full_name_pos)

        if info_type == "name":
            name = self.extracted_text[full_name_pos + 1].title().split(" ")[0].strip()
        else: # Bank.
            name = self.extracted_text[bank_name_pos + 1].title()

        log(f"Detected {party} {info_type}: {name}")
        return name

    def determine_extension(self):
        return info.extract_extension(self.file_path)

    def determine_description(self):
        if self.type == "Fatura":
            return "Fatura do Cartão Mercado Pago (App)"

        description_pos = info.find_position(self.extracted_text, "$", 2)
        description = self.extracted_text[description_pos + 1].strip()

        if (description == "De") or ("R$" in description) or (":" in description):
            return info.manual_override("description", self.extracted_text)

        log(f"Detected description: '{description}'.")

        if description.endswith("."):
            return description[:-1]
        else:
            return description

    def determine_amount(self):
        if self.type == "Fatura":
            value_pos = info.find_position(self.extracted_text, "Total R$", start_pos=20)
            value_string = [self.extracted_text[value_pos]]
            return info.extract_amount(value_string)
        else:
            return info.extract_amount(self.extracted_text)
