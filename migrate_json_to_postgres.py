import json
import psycopg2
from tqdm import tqdm
import uuid

# --- Configuration ---
DB_CONFIG = {
    "dbname": "get_copay_development",
    "user": "",
    "password": "",
    "host": ""
}
JSON_PATH = "json_with_standardised_drugs_embedded.json"

# --- Helper Functions ---
def connect_db():
    return psycopg2.connect(**DB_CONFIG)

def map_source(source):
    if not source:
        return "DIRECT"  # Default/fallback

    source = source.strip().lower()

    mapping = {
        "needy_meds": "NEEDY_MEDS",
        "rxassist": "RX_ASSIST",
        "rx_assist": "RX_ASSIST",
        "direct": "DIRECT",
        "drugs.com": "DRUGS_COM",
        "drugs_com": "DRUGS_COM",
        "accessia": "ACCESSIA",
        "cancer_care": "CANCER_CARE",
        "cancer care": "CANCER_CARE",
        "cancercare": "CANCER_CARE",
        "copays.org": "COPAYS_ORG",
        "copays_org": "COPAYS_ORG",
        "good days": "GOOD_DAYS",
        "good_days": "GOOD_DAYS",
        "healthwell foundation": "HEALTHWELL",
        "healthwell": "HEALTHWELL",
        "pan foundation": "PAN_FOUNDATION",
        "pan_foundation": "PAN_FOUNDATION",
        "patient advocate foundation": "PATIENT_ADVOCATE",
        "patient_advocate": "PATIENT_ADVOCATE",
        "rare diseases": "RARE_DISEASES",
        "rare_diseases": "RARE_DISEASES",
        "taf": "TAF",
    }

    return mapping.get(source, "DIRECT")  # Default fallback

def normalize_insurance_type(raw_value):
    if not raw_value:
        return None
    key = raw_value.strip().lower()

    # Constants
    UNINSURED = 'uninsured'
    MEDICAID = 'medicaid'
    MEDICARE = 'medicare'
    VETERAN_AFFAIRS = 'veteran_affairs'
    PRIVATE_COMMERCIAL = 'private_commercial'
    PRIVATE_EMPLOYER_SPONSORED = 'private_employer_sponsored'

    INSURANCE_TYPE_MAPPING = {
    'uninsured': UNINSURED,
    'medicaid': MEDICAID,
    'medicare': MEDICARE,
    'veteran affairs (va) / tricare': VETERAN_AFFAIRS,
    'va / tricare': VETERAN_AFFAIRS,
    'veteran': VETERAN_AFFAIRS,
    'private / commercial': PRIVATE_COMMERCIAL,
    'commercial': PRIVATE_COMMERCIAL,
    'private': PRIVATE_COMMERCIAL,
    'employer sponsored': PRIVATE_EMPLOYER_SPONSORED,
    'private employer sponsored': PRIVATE_EMPLOYER_SPONSORED
}
    return INSURANCE_TYPE_MAPPING.get(key)


def map_status(status):
    if not status:
        return "open"  # default fallback

    status = status.strip().lower()

    if status in ["open", "health equity open"]:
        return "open"
    elif status in ["closed", "closed health equity"]:
        return "closed"
    elif status in ["waitlist", "wait list only"]:
        return "waitlist"
    elif status in ["identified", "identified need", "health equity identified need"]:
        return "identified"
    elif status in ["seeking", "seekingfunding"]:
        return "seeking"
    elif status == "created":
        return "open"  # treating 'Created' as 'Open'
    else:
        return "open"  # default fallback


def get_or_create_program(cur, prog):
    # Check if the program already exists
    cur.execute("""
    SELECT id FROM programs WHERE LOWER(name) = %s AND source = %s
    """, (prog["prog_name"].strip().lower(), map_source(prog["source"])))
    result = cur.fetchone()
    if result:
        return result[0]

    # Insert full program record
    cur.execute("""
        INSERT INTO programs (
            name,
            source,
            source_id,
            website,
            program_type,
            company,
            category,
            duplicate_program_id,
            status,
            max_assistant_amount,
            min_assistant_amount,
            created_at,
            updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id
    """, (
        prog.get("prog_name").strip().lower(),  # instead of raw name
        map_source(prog.get("source")),
        prog.get("_id", {}).get("$oid"),                  # Assuming source_id = MongoDB _id
        prog.get("fund_url"),
        "FOUNDATION_ASSISTANCE",
        prog.get("company"),
        prog.get("category"),
        None,                                            # duplicate_program_id – can be linked later if needed
        map_status(prog.get("prog_status")),
        prog.get("maximum_assistance_amount"),
        prog.get("minimum_assistance_amount")
    ))
    return cur.fetchone()[0]


def get_or_create_drug(cur, name):
    if not name or name.lower() == "nan":
        return None

    # Check if already exists
    name_lower = name.strip().lower()

    cur.execute("SELECT id FROM drugs WHERE LOWER(name) = %s", (name_lower,))
    result = cur.fetchone()
    if result:
        return result[0]

    # Generate a UUID (can also be hash-based if preferred)
    drug_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, name.lower()))

    cur.execute("""
        INSERT INTO drugs (
            name,
            uuid,
            active,
            class_type,
            created_at,
            updated_at
        ) VALUES (%s, %s, %s, %s, NOW(), NOW())
        RETURNING id
    """, (
        name_lower,
        str(uuid.uuid5(uuid.NAMESPACE_DNS, name_lower)),
        True,       # active: default True
        None        # class_type: not available in JSON
    ))
    return cur.fetchone()[0]

def get_or_create_source_drug(cur, drug, source):
    name = drug["name"].strip().lower()
    source=map_source(source)
    # Check if already exists (unique index on name + source)
    cur.execute("""
    SELECT id FROM source_drugs WHERE LOWER(name) = %s AND source = %s
    """, (name, source))
    result = cur.fetchone()
    if result:
        return result[0]

    # Insert full source_drug record
    cur.execute("""
        INSERT INTO source_drugs (
            name,
            source_id,
            source,
            equivalent,
            generic,
            company_name,
            generic_name,
            created_at,
            updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id
    """, (
        name,
        None,                              # No source_id in drug JSON
        source,
        None,                              # equivalent not present in JSON
        None,                              # generic not present in JSON (True/False)
        None,                              # company_name not present
        drug.get("generic", "")            # generic_name from JSON
    ))
    return cur.fetchone()[0]

def insert_program_contact_details(cur, program_id, contact):
    for key in ["phonenumber", "fax", "email"]:
        value = contact.get(key)
        if value:
            if key=="phonenumber":
                key="phone"
            cur.execute("""
                INSERT INTO program_details (program_id, attr, value, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
            """, (program_id, key, value))

def insert_disease_description(cur, program_id, description):
    if description  and description.strip():
        cur.execute("""
            INSERT INTO program_details (program_id, attr, value, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
        """, (program_id, "disease_description", description))

def insert_eligibility_description(cur, program_id, description):
    if description and description.strip():
        cur.execute("""
            INSERT INTO program_details (program_id, attr, value, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
        """, (program_id, "eligibility_description", description))

def insert_diagnosis_code(cur, program_id, code):
    if isinstance(code, str):
        code = [code]  # wrap string into list

    if isinstance(code, list):
        for c in code:
            if c and isinstance(c, str) and c.strip():
                cur.execute("""
                    INSERT INTO program_details (program_id, attr, value, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                """, (program_id, "diagnosis_code", c.strip()))



def insert_program_links(cur, program_id, entries, link_type):
    for entry in entries:
        url = entry.get("url")
        name = entry.get("name") or url
        if url:
            cur.execute("""
                INSERT INTO program_links (program_id, name, link, link_type, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (program_id, name, url, link_type))


def insert_income_eligibility(cur, program_id, fpl_percent, state_id=1):
    if fpl_percent is None:
        return
    cur.execute("""
        INSERT INTO income_eligibilities (
            program_id,
            state_id,
            income_limit_in_percent,
            created_at,
            updated_at
        ) VALUES (%s, %s, %s, NOW(), NOW())
    """, (program_id, state_id, fpl_percent))

def link_tables(cur, table, cols, values):
    cur.execute(f"""
        SELECT 1 FROM {table} WHERE {' AND '.join([f"{c} = %s" for c in cols])}
    """, values)
    if not cur.fetchone():
        # Add created_at and updated_at to the columns and values
        cols_with_timestamps = cols + ['created_at', 'updated_at']
        values_with_timestamps = values + ['NOW()', 'NOW()']
        cur.execute(f"""
            INSERT INTO {table} ({', '.join(cols_with_timestamps)}) 
            VALUES ({', '.join(['%s'] * len(values) + ['NOW()', 'NOW()'])})
        """, values)

def get_or_create_condition(cur, name):
    if not name or name.lower() == "nan":
        return None
    
    name = name.strip().lower()
    cur.execute("SELECT id FROM conditions WHERE LOWER(name) = %s", (name,))
    result = cur.fetchone()
    if result:
        return result[0]
    
    cur.execute("""
        INSERT INTO conditions (name, created_at, updated_at)
        VALUES (%s, NOW(), NOW())
        RETURNING id
    """, (name,))
    return cur.fetchone()[0]

def insert_program_condition(cur, program_id, condition_name):
    if not condition_name or condition_name.lower() == "nan":
        return
    
    condition_id = get_or_create_condition(cur, condition_name)
    if condition_id:
        cur.execute("""
            INSERT INTO program_conditions (program_id, condition_id, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING
        """, (program_id, condition_id))

def insert_eligibility(cur, program_id, insurance_types):
    if not insurance_types:
        return
    
    # Constants from EligibilityCheck model
    UNINSURED = 'uninsured'
    MEDICAID = 'medicaid'
    MEDICARE = 'medicare'
    VETERAN_AFFAIRS = 'veteran_affairs'
    PRIVATE_COMMERCIAL = 'private_commercial'
    PRIVATE_EMPLOYER_SPONSORED = 'private_employer_sponsored'
    
    # Constants from Eligibility model
    ELIGIBLE = 'ELIGIBLE'
    NOT_ELIGIBLE = 'NOT ELIGIBLE'
    MAY_BE_ELIGIBLE = 'MAY BE ELIGIBLE'
    
    # Initialize eligibility data with default values
    eligibility_data = {
        'uninsured': NOT_ELIGIBLE,
        'medicare_part_d': NOT_ELIGIBLE,
        'prescription_coverage': NOT_ELIGIBLE,
        'denied_coverage': NOT_ELIGIBLE,
        'commercial': NOT_ELIGIBLE,
        'employer': NOT_ELIGIBLE,
        'medicare': NOT_ELIGIBLE,
        'medicaid': NOT_ELIGIBLE,
        'govt': NOT_ELIGIBLE,
        'under_insured': NOT_ELIGIBLE
    }
    
    # Map insurance types to eligibility fields
    for ins_type in insurance_types:
        ins_type = ins_type.lower()
        if 'private' in ins_type or 'commercial' in ins_type:
            eligibility_data['commercial'] = ELIGIBLE
        elif 'medicare' in ins_type:
            eligibility_data['medicare'] = ELIGIBLE
        elif 'medicaid' in ins_type:
            eligibility_data['medicaid'] = ELIGIBLE
        elif 'employer' in ins_type:
            eligibility_data['employer'] = ELIGIBLE
        elif 'other' in ins_type:
            eligibility_data['uninsured'] = ELIGIBLE
    
    cur.execute("""
        INSERT INTO eligibilities (
            program_id, uninsured, medicare_part_d, prescription_coverage,
            denied_coverage, commercial, employer, medicare, medicaid, govt,
            under_insured, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
    """, (
        program_id,
        eligibility_data['uninsured'],
        eligibility_data['medicare_part_d'],
        eligibility_data['prescription_coverage'],
        eligibility_data['denied_coverage'],
        eligibility_data['commercial'],
        eligibility_data['employer'],
        eligibility_data['medicare'],
        eligibility_data['medicaid'],
        eligibility_data['govt'],
        eligibility_data['under_insured']
    ))

def insert_diagnosis_code(cur, program_id, diagnosis_codes):
    if not diagnosis_codes:
        return
    
    for code_entry in diagnosis_codes:
        if isinstance(code_entry, dict):
            code = code_entry.get('code')
            description = code_entry.get('description', '')
            if code:
                cur.execute("""
                    INSERT INTO program_details (program_id, attr, value, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                """, (program_id, 'diagnosis_code', f"{code}: {description}"))
        elif isinstance(code_entry, str):
            cur.execute("""
                INSERT INTO program_details (program_id, attr, value, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
            """, (program_id, 'diagnosis_code', code_entry))

# --- Main Migration Function ---
def migrate_data():
    with open(JSON_PATH) as f:
        programs = json.load(f)

    conn = connect_db()
    cur = conn.cursor()

    try:
        for entry in tqdm(programs, desc="Migrating programs"):
            prog_id = get_or_create_program(cur, entry)

            # Add program contact info if present
            if "contact" in entry:
                insert_program_contact_details(cur, prog_id, entry["contact"])

            # Add condition
            if "condition_name" in entry:
                insert_program_condition(cur, prog_id, entry["condition_name"])

            # Add disease description
            if "disease_description" in entry:
                insert_disease_description(cur, prog_id, entry["disease_description"])

            # Add eligibility description
            if "eligibility_description" in entry:
                insert_eligibility_description(cur, prog_id, entry["eligibility_description"])

            # Add diagnosis codes
            if "diagnosis_code" in entry:
                insert_diagnosis_code(cur, prog_id, entry["diagnosis_code"])

            # Add insurance types to eligibilities
            if "insurance_types" in entry:
                insert_eligibility(cur, prog_id, entry["insurance_types"])

            # Add income_eligibility info if present
            fpl = entry.get("house_hold_income_limit_fpl_percent")
            if fpl:
                try:
                    fpl = int(float(fpl))  # Ensure it's an integer
                    insert_income_eligibility(cur, prog_id, fpl, state_id=1)
                except ValueError:
                    pass  # Skip if the value is malformed

            # Insert reference links
            if isinstance(entry.get("references"), list):
                insert_program_links(cur, prog_id, entry["references"], "references")

            # Insert support organisation links
            if isinstance(entry.get("support_organisations"), list):
                insert_program_links(cur, prog_id, entry["support_organisations"], "support_organisations")

            program_source = entry.get("source", "unknown")
            for drug in entry.get("covered_drugs", []):
                src_id = get_or_create_source_drug(cur, drug, program_source)
                drug_id = get_or_create_drug(cur, drug.get("standardised_drug"))

                if drug_id:
                    link_tables(cur, "drug_source_drugs", ["drug_id", "source_drug_id"], [drug_id, src_id])

                link_tables(cur, "source_drug_programs", ["source_drug_id", "program_id"], [src_id, prog_id])

        conn.commit()
    finally:
        cur.close()
        conn.close()

# --- Run Script ---
if __name__ == "__main__":
    migrate_data()
