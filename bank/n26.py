from bank.info import BankNames as Banks

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