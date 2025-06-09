import json

with open("json_with_standardised_drugs_embedded.json", "r") as f:
    data = json.load(f)

# Extract unique prog_status values
statuses = sorted({entry.get("prog_status", "").strip() for entry in data if "prog_status" in entry})
print(statuses)
