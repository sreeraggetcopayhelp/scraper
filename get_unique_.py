import json

with open("json_with_standardised_drugs_embedded.json", "r") as f:
    data = json.load(f)

# # Extract unique prog_status values
# statuses = sorted({entry.get("prog_status", "").strip() for entry in data if "prog_status" in entry})
# print(statuses)


# # Extract unique insurance_types values
# insurance_types_set = set()
# for entry in data:
#     for insurance in entry.get("insurance_types", []):
#         insurance_types_set.add(insurance.strip())

# # Convert to sorted list and print
# insurance_types = sorted(insurance_types_set)
# print("Distinct insurance_types values:")
# print(insurance_types)


# Extract unique house_hold_income values
house_hold_income = sorted({str(entry.get("house_hold_income_limit_fpl_percent", "")).strip() for entry in data if "house_hold_income_limit_fpl_percent" in entry})
print(house_hold_income)

