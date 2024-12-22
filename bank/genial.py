from simplelog import log
import bank.info as info

class Genial:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = info.BankNames(8).name
        self.type = ""
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_first_name = self.determine_name("sender", "name")
        self.sender_bank = self.determine_name("sender", "bank")

        self.receiver_first_name = self.determine_name("receiver", "name")
        self.receiver_bank = self.determine_name("receiver", "bank")

    def determine_name(self, party, info_type):
        name_offset = 1
        text_id = "Nome"
        full_name_pos = info.find_position(self.extracted_text, text_id, len(text_id)) + name_offset

        if party == "sender":
            full_name_pos = info.find_position(self.extracted_text, text_id, len(text_id), start_pos=full_name_pos) + name_offset

        bank_name_pos = info.find_position(self.extracted_text, "Instituição", 11, start_pos=full_name_pos)

        if info_type == "name":
            name = self.extracted_text[full_name_pos].split(" ")[0].strip().title()
        else: # Bank.
            name = self.extracted_text[bank_name_pos].title()

        log(f"Detected {party} {info_type}: {name}")
        return name

    def determine_extension(self):
        return info.extract_extension(self.file_path)

    def determine_amount(self):
        return info.extract_amount(self.extracted_text)

    def determine_description(self):
        description_pos = info.find_position(self.extracted_text, "Mensagem", 1)

        description = self.extracted_text[description_pos + 1]

        if description_pos < 0:
            description = info.manual_override("description", self.extracted_text)

        return description