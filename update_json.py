import pandas as pd
import json

# Load CSV data
csv_path = "flattened_covered_drugs_standardized.csv"
df = pd.read_csv(csv_path)

# Group by prog_name to gather standerdised_drug and standerdised_program
grouped_data = (
    df.groupby("prog_name")
    .apply(lambda x: {
        "standerdised_drug": sorted(set(x["standerdised_drug"].dropna())),
        "standerdised_program": sorted(set(x["standerdised_program"].dropna()))
    })
    .to_dict()
)

# Load original JSON data
json_path = "dev_backup.json"
with open(json_path, "r") as f:
    json_data = json.load(f)

# Update JSON records with data from CSV
for entry in json_data:
    prog_name = entry.get("prog_name")
    if prog_name in grouped_data:
        entry["standerdised_drug"] = grouped_data[prog_name]["standerdised_drug"]
        entry["standerdised_program"] = grouped_data[prog_name]["standerdised_program"]

# Save updated JSON
output_path = "dev_backup_updated.json"
with open(output_path, "w") as f:
    json.dump(json_data, f, indent=2)

print("Updated JSON saved to:", output_path)
