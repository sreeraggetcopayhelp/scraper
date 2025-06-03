import json
import csv

# Load JSON data from a file
with open("dev_backup.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Prepare the flattened data
flattened_data = []
for entry in data:
    _id = entry.get("_id", {}).get("$oid", "")
    prog_name = entry.get("prog_name", "")
    source = entry.get("source", "")
    covered_drugs = entry.get("covered_drugs", [])

    # Handle records with no covered_drugs
    if not covered_drugs:
        flattened_data.append({
            "id": _id,
            "prog_name": prog_name,
            "source": source,
            "covered_drugs.name": "",
            "covered_drugs.generic": "",
            "standerdised_drug": "",
            "standerdised_program": ""

        })
    else:
        for drug in covered_drugs:
            flattened_data.append({
                "id": _id,
                "prog_name": prog_name,
                "source": source,
                "covered_drugs.name": drug.get("name", ""),
                "covered_drugs.generic": drug.get("generic", ""),
                "standerdised_drug": "",
                "standerdised_program": ""
            })

# Write to CSV
with open("flattened_covered_drugs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "prog_name", "source", "covered_drugs.name", "covered_drugs.generic", "standerdised_drug", "standerdised_program"])
    writer.writeheader()
    writer.writerows(flattened_data)

print("CSV file has been created: flattened_covered_drugs.csv")
