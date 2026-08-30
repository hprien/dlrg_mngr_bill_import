class Bill_Import:
    def __import_mitglieder(self, mitglieder_path, mitglieder_has_header, mitglieder_seperator):
        mitglieder = {}
        with mitglieder_path.open("r", encoding="iso-8859-1") as file:
            csv = file.read()
            for i, line in enumerate(csv.splitlines()):
                if mitglieder_has_header and i == 0:
                    continue

                mitglied = line.split(mitglieder_seperator)
                mitgliedsnummer = mitglied[0]
                first_name = mitglied[5].strip()
                last_name = mitglied[4].strip()
                email = mitglied[13].strip()

                mitglieder[(first_name, last_name)] = {
                    "no": mitgliedsnummer,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email
                }

        return mitglieder

    def __init__(self, bill_title, billing_date, due_days, buchhaltungskonto, sk42_sphaere, kostenstelle, mwst_satz, mitglieder_path, mitglieder_has_header, mitglieder_seperator):
        self.bill_title = bill_title
        self.billing_date = billing_date
        self.due_days = due_days
        self.buchhaltungskonto = buchhaltungskonto
        self.sk42_sphaere = sk42_sphaere
        self.kostenstelle = kostenstelle
        self.mwst_satz = mwst_satz

        self.mitglieder = self.__import_mitglieder(mitglieder_path, mitglieder_has_header, mitglieder_seperator)

        self.bills = []

    def add_bill(self, first_name, last_name):
        try:
            mitglied = self.mitglieder[(first_name, last_name)]
        except KeyError:
            print(f'{first_name} {last_name} not found in mitglieder')
            exit(10)

        self.bills.append({
            "first_name": first_name,
            "last_name": last_name,
            "mitglieds_no": mitglied["no"],
            "email": mitglied["email"],
            "bill_items": [],
        })

        return len(self.bills) - 1

    def add_bill_item(self, bill_index, product_name, price, quantity):
        bill = self.bills[bill_index]
        bill["bill_items"].append({
            "bill_title": self.bill_title,
            "item_title": product_name,
            "item_description": f"",
            "quantity": quantity,
            "price": price
        })

    def __date_plus_days(self, date_str, days):
        from datetime import datetime, timedelta

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        new_date_obj = date_obj + timedelta(days=days)
        return new_date_obj.strftime("%d.%m.%Y")
    
    def __normalize_date(self, date_str):
        from datetime import datetime

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d.%m.%Y")

    def __normalize_float(self, float):
        return f"{float:.2f}".replace(".", ",")

    def write_import_file(self, output_path):
        with output_path.open("w", encoding="utf-8") as file:
            file.write("Mitgliedsnummer;Datensatztyp;RechnungId;RechnungBezeichnung;RechnungDatum;PositionId;PositionBezeichnung;PositionBeschreibung;Menge;Einzelpreis;Inkasso;Zustellung;Zahlungsziel;Intervall;Termin;Faelligkeit;Ende;Mwst;Vermerk;Spendenfaehig;Spendenart;Buchhaltungskonto;SKR42 Sphaere;Steuerschluessel;Kostenstelle;Auswertungskennziffer;Nachlass;Nachlassgrund;Empfaengeremail;Zusatzinformationen\r\n")
            for bill_index, bill in enumerate(self.bills):
                for item_index, item in enumerate(bill["bill_items"]):
                    line = f"{bill['mitglieds_no']};2;{bill_index+1};{item['bill_title']};{self.__normalize_date(self.billing_date)};{item_index+1};{item['item_title']};{item['item_description']};{item['quantity']};{self.__normalize_float(item['price'])};1;2;{self.due_days};0;{self.__normalize_date(self.billing_date)};{self.__date_plus_days(self.billing_date, self.due_days)};31.12.2099;{self.__normalize_float(self.mwst_satz)};;;;{self.buchhaltungskonto};{self.sk42_sphaere};;{self.kostenstelle};;;;{bill['email']};\r\n"
                    file.write(line)