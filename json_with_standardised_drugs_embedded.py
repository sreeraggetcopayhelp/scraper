import json
import pandas as pd

# Load CSV
csv_file = "Final mapped drugs for db updation - Already existing drugs with std names.csv"
df = pd.read_csv(csv_file)

# Normalize column names
df.columns = [col.strip().lower() for col in df.columns]

# Detect relevant columns
def detect_column(possibilities):
    for name in possibilities:
        for col in df.columns:
            if name in col:
                return col
    return None

prog_col = detect_column(['prog_name', 'program'])
source_col = detect_column(['source'])
std_drug_col = detect_column(['standerdised_drug'])
std_prog_col = detect_column(['standerdised_program'])

if not prog_col or not source_col or not std_drug_col:
    raise ValueError("Required columns not found in CSV.")

# Build mapping from CSV
mapping = {
    (str(row[prog_col]).strip().lower(), str(row[source_col]).strip().lower()): {
        'standardised_drug': str(row.get(std_drug_col, '')).strip(),
        'standardised_program': str(row.get(std_prog_col, '')).strip() if std_prog_col else ''
    }
    for _, row in df.iterrows()
}

# Load JSON
with open("dev_backup.json", "r") as f:
    data = json.load(f)

# Update JSON
updated_count = 0
for program in data:
    key = (program.get('prog_name', '').strip().lower(), program.get('source', '').strip().lower())
    if key in mapping:
        std_data = mapping[key]

        # Set standardised_program at top level
        if std_data['standardised_program']:
            program['standardised_program'] = std_data['standardised_program']

        # Inject standardised_drug into each covered_drug
        if std_data['standardised_drug'] and isinstance(program.get('covered_drugs'), list):
            for drug in program['covered_drugs']:
                drug['standardised_drug'] = std_data['standardised_drug']

        updated_count += 1

# Save updated JSON
output_path = "json_with_standardised_drugs_embedded.json"
with open(output_path, "w") as f:
    json.dump(data, f, indent=2)

print(f"✅ Updated {updated_count} programs and saved to '{output_path}'")
