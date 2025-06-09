
import json
import psycopg2
from tqdm import tqdm
import uuid

# --- Configuration ---
DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_pass",
    "host": "localhost"
}
JSON_PATH = "json_with_standardised_drugs_embedded.json"

# --- Helper Functions ---
def connect_db():
    return psycopg2.connect(**DB_CONFIG)

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
        SELECT id FROM programs WHERE name = %s AND source = %s
    """, (prog["prog_name"], prog["source"]))
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
        prog.get("prog_name"),
        prog.get("source"),
        prog.get("_id", {}).get("$oid"),                  # Assuming source_id = MongoDB _id
        prog.get("fund_url"),
        prog.get("program_type"),
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
    cur.execute("SELECT id FROM drugs WHERE name = %s", (name,))
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
        name,
        drug_uuid,
        True,       # active: default True
        None        # class_type: not available in JSON
    ))
    return cur.fetchone()[0]

def get_or_create_source_drug(cur, drug, source):
    name = drug["name"]

    # Check if already exists (unique index on name + source)
    cur.execute("""
        SELECT id FROM source_drugs WHERE name = %s AND source = %s
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



def link_tables(cur, table, cols, values):
    cur.execute(f"""
        SELECT 1 FROM {table} WHERE {' AND '.join([f"{c} = %s" for c in cols])}
    """, values)
    if not cur.fetchone():
        cur.execute(f"""
            INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(values))})
        """, values)

# --- Main Migration Function ---
def migrate_data():
    with open(JSON_PATH) as f:
        programs = json.load(f)

    conn = connect_db()
    cur = conn.cursor()

    try:
        for entry in tqdm(programs, desc="Migrating programs"):
            prog_id = get_or_create_program(cur, entry)
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
