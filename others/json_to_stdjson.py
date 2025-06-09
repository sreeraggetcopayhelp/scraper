import json
import pandas as pd

# Load CSV
csv_file = "Final mapped drugs for db updation - Already existing drugs with std names.csv"
df_csv = pd.read_csv(csv_file)

# Normalize and extract standardization mappings
df_csv.columns = [c.strip().lower() for c in df_csv.columns]
csv_mappings = {
    (row['prog_name'].strip().lower(), row['source'].strip().lower()): {
        'standardised_drug': row.get('standardised_drug', '').strip(),
        'standardised_program': row.get('standardised_program', '').strip()
    }
    for _, row in df_csv.iterrows()
}

# Load original JSON
json_file = "dev_backup.json"
with open(json_file, "r") as f:
    json_data = json.load(f)

# Update JSON entries with standardised info
updated_count = 0
for entry in json_data:
    key = (entry['prog_name'].strip().lower(), entry['source'].strip().lower())
    if key in csv_mappings:
        std_info = csv_mappings[key]
        if std_info['standardised_drug']:
            entry['standardised_drug'] = std_info['standardised_drug']
        if std_info['standardised_program']:
            entry['standardised_program'] = std_info['standardised_program']
        updated_count += 1

# Save updated JSON
output_file = "updated_dev_backup.json"
with open(output_file, "w") as f:
    json.dump(json_data, f, indent=2)

print(f"Updated {updated_count} JSON entries. Saved to '{output_file}'.")
