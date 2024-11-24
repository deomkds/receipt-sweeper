from simplelog import log
import bank.info as info

class Inter:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = info.BankNames(4).name
        self.type = self.extracted_text[2]
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_first_name = self.determine_name("sender", "name")
        self.sender_bank = self.determine_name("sender", "bank")

        self.receiver_first_name = self.determine_name("receiver", "name")
        self.receiver_bank = self.determine_name("receiver", "bank")

    def determine_name(self, party, info_type):
        if party == "sender":
            text_id = "Quem pagou"
        else:
            text_id = "Quem recebeu"

        full_name_pos = info.find_position(self.extracted_text, text_id, len(text_id))
        bank_name_pos = info.find_position(self.extracted_text, "Instituição", 11, start_pos=full_name_pos)

        if info_type == "name":
            name = self.extracted_text[full_name_pos + 1].split(" ")[1].strip().title()
        else: # Bank.
            name = self.extracted_text[bank_name_pos].title()[12:].replace("|", "I")

        log(f"Detected {party} {info_type}: {name}")
        return name

    def determine_extension(self):
        return info.extract_extension(self.file_path)

    def determine_description(self):
        message_pos = info.find_position(self.extracted_text, "Mensagem", 9)

        if message_pos < 0:
            message = info.manual_override("description", self.extracted_text)
        else:
            message = self.extracted_text[message_pos][9:]
            log(f"Detected description: '{message}'.")

        return message

    def determine_amount(self):
        return info.extract_amount(self.extracted_text)
