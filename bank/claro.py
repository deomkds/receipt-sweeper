from simplelog import log
import bank.info as info

class Claro:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = info.BankNames(6).name
        self.type = self.determine_type()
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        # Not applicable.
        self.sender_full_name = ""
        self.sender_first_name = ""
        self.sender_bank = ""

        self.receiver_full_name = ""
        self.receiver_first_name = ""
        self.receiver_bank = ""

    def determine_extension(self):
        return info.extract_extension(self.file_path)

    def determine_type(self):
        field = self.extracted_text[0].lower()

        if "sucesso!" in field:
            return "Recarga"
        else:
            return "Outro"

    def determine_amount(self):
        return info.extract_amount(self.extracted_text)

    def determine_description(self):
        if self.type == "Recarga":
            log("Description for predefined type: 'Recarga Claro'.")
            description = "Recarga Claro"
        else:
            return info.manual_override("description", self.extracted_text)

        log(f"Description auto detected: '{description}'.")

        return description
