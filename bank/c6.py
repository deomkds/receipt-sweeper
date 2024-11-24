import bank.info as info

class C6:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = info.BankNames(5).name
        self.type = self.determine_type()
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_first_name = self.determine_name("sender", "first_name")
        self.sender_full_name = self.determine_name("sender", "full_name")
        self.sender_bank = self.determine_name("sender", "bank")

        self.receiver_first_name = self.determine_name("receiver", "first_name")
        self.receiver_full_name = self.determine_name("receiver", "full_name")
        self.receiver_bank = self.determine_name("receiver", "bank")

    def determine_type(self):
        field = f"{self.extracted_text[1].lower()}{self.extracted_text[2].lower()}"

        if "pagamento" in field:
            return "Fatura"
        else:
            return "Outro"

    def determine_name(self, party, info_type):
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
        return info.extract_extension(self.file_path)

    def determine_description(self):
        if self.type == "Fatura":
            return "Fatura do Cartão C6 (App)"

        # It has to be a manual override because I can't type descriptions on my phone.
        return info.manual_override("description", self.extracted_text)

    def determine_amount(self):
        return info.extract_amount(self.extracted_text)
