import bank.info as info

class Unknown:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = info.BankNames(0).name
        self.type = ""
        self.amount = 0
        self.description = ""
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_full_name = ""
        self.sender_first_name = ""
        self.sender_bank = ""

        self.receiver_full_name = ""
        self.receiver_first_name = ""
        self.receiver_bank = ""

    def determine_extension(self):
        return info.extract_extension(self.file_path)
