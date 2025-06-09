import pandas as pd
import json

# Load CSV
csv_path = "flattened_covered_drugs_standardized.csv"
df = pd.read_csv(csv_path)

# Filter out rows with missing drug names
df = df.dropna(subset=["covered_drugs.name", "standerdised_drug"])

# Build a lookup: {(prog_name, covered_drugs.name): standerdised_drug}
drug_lookup = {
    (row["prog_name"], row["covered_drugs.name"]): row["standerdised_drug"]
    for _, row in df.iterrows()
}

# Load JSON
with open("dev_backup.json", "r") as f:
    data = json.load(f)

# Update JSON covered_drugs
for entry in data:
    prog_name = entry.get("prog_name")
    for drug in entry.get("covered_drugs", []):
        drug_name = drug.get("name")
        key = (prog_name, drug_name)
        if key in drug_lookup:
            drug["standerdised_drug"] = drug_lookup[key]

# Save updated JSON
with open("dev_backup_updated.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated JSON saved as dev_backup_updated.json")
