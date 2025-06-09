
import json
import psycopg2
from tqdm import tqdm

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
    return {
        "SeekingFunding": "open",
        "Closed": "closed"
    }.get(status, "open")

def get_or_create_program(cur, prog):
    cur.execute("""
        SELECT id FROM programs WHERE name = %s AND source = %s
    """, (prog["prog_name"], prog["source"]))
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("""
        INSERT INTO programs (name, source, status, website, max_assistant_amount, min_assistant_amount)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (
        prog["prog_name"], prog["source"],
        map_status(prog.get("prog_status")),
        prog.get("fund_url"),
        prog.get("maximum_assistance_amount"),
        prog.get("minimum_assistance_amount")
    ))
    return cur.fetchone()[0]

def get_or_create_drug(cur, name):
    if not name or name.lower() == "nan":
        return None
    cur.execute("SELECT id FROM drugs WHERE name = %s", (name,))
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("INSERT INTO drugs (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()[0]

def get_or_create_source_drug(cur, drug):
    name = drug["name"]
    source = "accessia"
    cur.execute("SELECT id FROM source_drugs WHERE name = %s AND source = %s", (name, source))
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("""
        INSERT INTO source_drugs (name, generic_name, source)
        VALUES (%s, %s, %s) RETURNING id
    """, (name, drug.get("generic", ""), source))
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

            for drug in entry.get("covered_drugs", []):
                src_id = get_or_create_source_drug(cur, drug)
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
