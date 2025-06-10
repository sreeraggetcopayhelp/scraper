import csv
import json
from uuid import uuid4

# Load JSON
with open("json_with_standardised_data.json", "r") as f:
    json_data = json.load(f)

# # Sample JSON data (replace with actual JSON input)
# json_data = [{
#     "_id": {"$oid": "683eab51c1adc57577caa64e"},
#     "fund_url": "https://accessiahealth.org/patient-programs/",
#     "prog_name": "Alpha1",
#     "prog_status": "Closed",
#     "condition_name": "Alpha1",
#     "contact": {
#         "phonenumber": "",
#         "fax": "",
#         "email": ""
#     },
#     "insurance_types": ["Other", "Private"],
#     "house_hold_income_limit_fpl_percent": 500,
#     "covered_drugs": [
#         {"name": "Alpha1-Proteinase Inhibitor", "generic": "", "standardised_drug": "zemaira"},
#         {"name": "Aralast NP", "generic": "", "standardised_drug": "zemaira"},
#         {"name": "Glassia", "generic": "", "standardised_drug": "zemaira"},
#         {"name": "Prolastin-C", "generic": "", "standardised_drug": "zemaira"},
#         {"name": "Zemaira", "generic": "", "standardised_drug": "zemaira"}
#     ],
#     "maximum_assistance_amount": 7500,
#     "minimum_assistance_amount": None,
#     "references": [
#         {"name": "Alpha 1 Foundation", "url": "https://www.alpha1.org/"},
#         # ... other references
#     ],
#     "support_organisations": [
#         {"name": "Alpha 1 Foundation", "url": "https://www.alpha1.org/"},
#         # ... other support organizations
#     ],
#     "eligibility_description": "",
#     "diagnosis_code": [
#         {"code": "E88.01", "description": "Alpha-1-antitrypsin deficiency"}
#     ],
#     "disease_description": "Alpha-1 Antitrypsin Deficiency (Alpha-1) is a genetic condition...",
#     "source": "accessia",
#     "standardised_program": "nan"
# }]

# Base CSV headers
base_headers = [
    'program_name', 'program_source', 'program_source_id', 'program_type', 'program_company',
    'program_website', 'program_status', 'min_assistant_amount', 'max_assistant_amount',
    'program_category', 'duplicate_program_id', 'maximum_savings', 'fpl_requirement',
    'email', 'phone', 'uninsured_eligibility', 'medicare_part_d_eligibility',
    'prescription_coverage_eligibility', 'denied_coverage_eligibility', 'commercial_eligibility',
    'employer_eligibility', 'medicare_eligibility', 'medicaid_eligibility', 'govt_eligibility',
    'under_insured_eligibility', 'source_drug_name', 'source_drug_source',
    'source_drug_source_id', 'source_drug_company_name', 'source_drug_generic_name',
    'standardized_drug_names'
]

# Possible insurance types from JSON
possible_insurance_types = ['Medicaid', 'Medicare', 'Other', 'Private', 'Public', 'TRICARE', 'any']

# Map insurance types to existing CSV headers (case-insensitive) or create new ones
insurance_to_column = {}
for ins_type in possible_insurance_types:
    # Check if a header matches the insurance type (case-insensitive)
    matched = False
    for header in base_headers:
        if header.lower().startswith(ins_type.lower()) and header.endswith('_eligibility'):
            insurance_to_column[ins_type] = header
            matched = True
            break
    if not matched:
        # Create new column (e.g., tricare_eligibility, any_eligibility)
        insurance_to_column[ins_type] = f"{ins_type.lower()}_eligibility"

# Create headers: base headers + new eligibility columns for insurance types not in base_headers
headers = base_headers.copy()
for ins_type, col_name in insurance_to_column.items():
    if col_name not in headers:
        headers.append(col_name)

# Function to create CSV row for a program and a single drug
def create_csv_row(program, drug):
    row = {header: 'NA' for header in headers}  # Initialize all fields as 'NA'
    
    # Program basic information
    row['program_name'] = program.get('prog_name', 'NA')
    row['program_source'] = program.get('source', 'NA')
    row['program_source_id'] = program.get('_id', {}).get('$oid', 'NA')
    row['program_type'] = 'FOUNDATION_ASSISTANCE'  # Set to FOUNDATION_ASSISTANCE as requested
    row['program_status'] = program.get('prog_status', 'NA')
    row['program_website'] = program.get('fund_url', 'NA')
    row['min_assistant_amount'] = str(program.get('minimum_assistance_amount', 'NA'))
    row['max_assistant_amount'] = str(program.get('maximum_assistance_amount', 'NA'))
    row['program_category'] = program.get('condition_name', 'NA')
    row['fpl_requirement'] = str(program.get('house_hold_income_limit_fpl_percent', 'NA'))
    row['email'] = program.get('contact', {}).get('email', 'NA')
    row['phone'] = program.get('contact', {}).get('phonenumber', 'NA')
    
    # Insurance eligibility
    insurance_types = program.get('insurance_types', [])
    for ins_type in insurance_types:
        if ins_type in insurance_to_column:
            col_name = insurance_to_column[ins_type]
            row[col_name] = 'ELIGIBLE'
    
    # Drug information
    if drug:
        row['source_drug_name'] = drug.get('name', 'NA')
        row['source_drug_source'] = program.get('source', 'NA')
        row['source_drug_source_id'] = program.get('_id', {}).get('$oid', 'NA')
        row['source_drug_generic_name'] = drug.get('generic', 'NA')
        row['standardized_drug_names'] = drug.get('standardised_drug', 'NA')
    
    return [row[header] for header in headers]

# Write to CSV
with open('programs.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)  # Write headers
    for program in json_data:
        drugs = program.get('covered_drugs', [])
        if not drugs:
            # If no drugs, create a single row with no drug info
            row = create_csv_row(program, None)
            writer.writerow(row)
        else:
            # Create a row for each drug
            for drug in drugs:
                row = create_csv_row(program, drug)
                writer.writerow(row)

print("CSV file 'programs.csv' has been created successfully.")