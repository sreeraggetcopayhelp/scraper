import pandas as pd
import numpy as np

# Load the CSV file
df = pd.read_csv("flattened_covered_drugs.csv")

# Helper function to standardize drug names
def standardize_drug(name):
    if pd.isna(name):
        return np.nan
    name = name.strip().title()
    name = name.replace("Np", "")  # remove suffix like 'NP'
    name = name.replace("-", " ")
    return " ".join(name.split())

# Helper function to standardize program names
def standardize_program(prog):
    if pd.isna(prog):
        return np.nan
    prog = prog.replace("Fund", "").strip()
    return prog.title()

# Apply standardization
df["standerdised_drug"] = df["covered_drugs.name"].apply(standardize_drug)
df["standerdised_program"] = df["prog_name"].apply(standardize_program)

# Save the updated CSV
df.to_csv("flattened_covered_drugs_standardized.csv", index=False)
