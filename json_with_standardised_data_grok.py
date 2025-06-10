import json
import csv
from pathlib import Path

def load_json_file(json_path):
    """Load JSON file and return its contents."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in input file")

def load_csv_file(csv_path):
    """Load CSV file and return its rows as a list of dictionaries."""
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

def update_json_with_csv(json_data, csv_data):
    """Update JSON data by adding standardised_drug to covered_drugs and standerdised_program."""
    # Create lookup dictionaries from CSV for drug and program standardization
    csv_drug_lookup = {}
    csv_program_lookup = {}
    for row in csv_data:
        prog_name = row['prog_name'].lower().strip()
        drug_name = row['covered_drugs.name'].lower().strip()
        # Store the first occurrence of drug standardization for this (prog_name, drug_name)
        if (prog_name, drug_name) not in csv_drug_lookup:
            csv_drug_lookup[(prog_name, drug_name)] = row['standerdised_drug']
        # Store the first non-empty standardized program name for this prog_name
        if prog_name not in csv_program_lookup and row['standerdised_program']:
            csv_program_lookup[prog_name] = row['standerdised_program']
    
    updated_drug_count = 0
    updated_prog_count = 0
    unmatched_drugs = []
    unmatched_progs = []
    
    # Handle both single JSON object and list of JSON objects
    json_items = [json_data] if isinstance(json_data, dict) else json_data
    
    for item in json_items:
        prog_name = item.get('prog_name', '').lower().strip()
        covered_drugs = item.get('covered_drugs', [])
        
        # Update covered drugs with standardised_drug
        for drug in covered_drugs:
            drug_name = drug.get('name', '').lower().strip()
            key = (prog_name, drug_name)
            
            if key in csv_drug_lookup:
                drug['standardised_drug'] = csv_drug_lookup[key]
                updated_drug_count += 1
            else:
                unmatched_drugs.append((prog_name, drug_name))
        
        # Add standardised program name if available
        if prog_name in csv_program_lookup:
            item['standerdised_program'] = csv_program_lookup[prog_name]
            updated_prog_count += 1
        else:
            unmatched_progs.append(prog_name)
    
    return json_items, updated_drug_count, updated_prog_count, unmatched_drugs, unmatched_progs

def save_json_file(json_data, output_path):
    """Save updated JSON data to a file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
    except Exception as e:
        raise IOError(f"Failed to save JSON file: {str(e)}")

def main(json_path, csv_path, output_path):
    """Main function to process JSON and CSV files."""
    try:
        # Load files
        json_data = load_json_file(json_path)
        csv_data = load_csv_file(csv_path)
        
        # Update JSON with CSV data
        updated_json, updated_drug_count, updated_prog_count, unmatched_drugs, unmatched_progs = update_json_with_csv(json_data, csv_data)
        
        # Save updated JSON
        save_json_file(updated_json[0] if isinstance(json_data, dict) else updated_json, output_path)
        
        print(f"Updated {updated_drug_count} drug entries with standardised_drug and {updated_prog_count} program names.")
        print(f"Saved to {output_path}")
        if unmatched_drugs:
            print(f"Unmatched drug entries: {len(unmatched_drugs)}")
            for prog, drug in unmatched_drugs:
                print(f"  - Program: {prog}, Drug: {drug}")
        if unmatched_progs:
            print(f"Unmatched program names: {len(unmatched_progs)}")
            for prog in set(unmatched_progs):
                print(f"  - Program: {prog}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    # File paths (update these as needed)
    json_path = "dev_backup.json"  # Path to your JSON file
    csv_path = "Final mapped drugs for db updation - Already existing drugs with std names.csv"    # Path to your CSV file
    output_path = "json_with_standardised_data.json"  # Path for the updated JSON file
    
    main(json_path, csv_path, output_path)