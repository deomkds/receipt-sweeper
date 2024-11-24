from simplelog import log
import bank.info as info

class Nubank:
    def __init__(self, receipt_object):
        self.file_path = receipt_object.file_path
        self.timestamp = receipt_object.timestamp
        self.extracted_text = receipt_object.extracted_text

        self.bank = info.BankNames(1).name
        self.type = self.determine_type()
        self.amount = self.determine_amount()
        self.description = self.determine_description()
        self.extension = self.determine_extension()
        self.folder = self.bank

        self.sender_first_name = self.determine_name("sender", "name")
        self.sender_bank = self.determine_name("sender", "bank")

        self.receiver_first_name = self.determine_name("receiver", "name")
        self.receiver_bank = self.determine_name("receiver", "bank")

    def determine_name(self, party, info_type):

        if (self.type != "Transferência") and (self.type != "Agendamento"):
            return ""

        if party == "sender":
            text_id = "Origem"
        else:
            text_id = "Destino"

        full_name_pos = info.find_position(self.extracted_text, text_id, len(text_id))
        bank_name_pos = info.find_position(self.extracted_text, "Instituição", 11, start_pos=full_name_pos)

        if info_type == "name":
            name = self.extracted_text[full_name_pos + 1].replace("Nome", "").strip().split(" ")[0].strip().title()
        else: # Bank.
            name = self.extracted_text[bank_name_pos].title()[12:].replace("|", "I")

        log(f"Detected {party} {info_type}: {name}")
        return name

    def determine_extension(self):
        return info.extract_extension(self.file_path)

    def determine_type(self):
        field = self.extracted_text[2].lower()

        if "pagamento" in field:
            return "Pagamento"
        elif "transferência" in field:
            return "Transferência"
        elif "agendamento" in field:
            return "Agendamento"
        elif "no valor de" in field:
            return "Fatura"
        else:
            return "Outro"

    def determine_amount(self):
        return info.extract_amount(self.extracted_text)

    def determine_description(self):
        start_pos = 0
        end_pos = 0
        description = ""

        if self.type == "Fatura":
            log("Description for predefined type: 'Fatura'.")
            return "Fatura"

        if self.type == "Pagamento":
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
            return info.manual_override("description", self.extracted_text)

        for j in range(start_pos, end_pos):
            description += self.extracted_text[j]

        log(f"Description auto detected: '{description}'.")

        return description
