from pathlib import Path
from typing import Any
import dlrg_manager

BILL_TITLE = "Pfingstzeltlager 2026"
BILLING_DATE = "2026-07-01"
DUE_DAYS = 14
BUCHHALTUNGSKONTO = "42035"
SK42_SPHAERE = "01"
KOSTENSTELLE = "J051"
MWST_SATZ = 0.0

KAUFE_FILENAME = "pzl.csv"
KAUFE_SEPERATOR = ";"
KAUFE_HAS_HEADER = True

MITGLIEDER_FILENAME = "mitglieder.csv"
MITGLIEDER_SEPERATOR = ";"
MITGLIEDER_HAS_HEADER = True

def normalize_price(price: str) -> float:
    price = price.replace(",", ".")
    price = price.replace("€", "")
    price = price.replace("\"", "").strip()
    
    return float(price)

def normalize_string(s: str) -> str:
    return s.replace("\"", "").strip()

def extract_bill_item(bill_item: list[str]) -> dict[str, Any]:
    return {
        "first_name": normalize_string(bill_item[0]),
        "last_name": normalize_string(bill_item[1]),
        "product_name": normalize_string(bill_item[2]),
        "price": normalize_price(bill_item[3]),
        "quantity": int(bill_item[4])
    }

def import_bills(file_path: Path) -> dict[tuple, list[dict[str: Any]]]:
    bills: dict[tuple, list[dict[str: Any]]] = {}

    with file_path.open("r", encoding="utf-8") as file:
        csv = file.read()
        for i, line in enumerate(csv.splitlines()):
            if KAUFE_HAS_HEADER and i == 0:
                continue

            bill_item = line.split(KAUFE_SEPERATOR)
            bill_item = extract_bill_item(bill_item)

            if (bill_item["first_name"], bill_item["last_name"]) not in bills:
                bills[(bill_item["first_name"], bill_item["last_name"])] = []

            bills[(bill_item["first_name"], bill_item["last_name"])].append(bill_item)

    return bills

if __name__ == "__main__":
    import_path = Path.cwd() / KAUFE_FILENAME
    bills: dict[tuple, list[dict[str: Any]]] = import_bills(import_path)

    manager_bill_import = dlrg_manager.Bill_Import(
        bill_title=BILL_TITLE,
        billing_date=BILLING_DATE,
        due_days=DUE_DAYS,
        buchhaltungskonto=BUCHHALTUNGSKONTO,
        sk42_sphaere=SK42_SPHAERE,
        kostenstelle=KOSTENSTELLE,
        mwst_satz=MWST_SATZ,
        mitglieder_path=Path.cwd() / MITGLIEDER_FILENAME,
        mitglieder_has_header=MITGLIEDER_HAS_HEADER,
        mitglieder_seperator=MITGLIEDER_SEPERATOR
    )

    for bill_key, bill_items in bills.items():
        total = sum(item['price'] * item['quantity'] for item in bill_items)

        if total <= 0.0:
            continue

        bill_index = manager_bill_import.add_bill(bill_key[0], bill_key[1])
        for item in bill_items:
            manager_bill_import.add_bill_item(
                bill_index,
                item['product_name'],
                item['price'],
                item['quantity']
            )

    manager_bill_import.write_import_file(Path.cwd() / "bill_import.csv")