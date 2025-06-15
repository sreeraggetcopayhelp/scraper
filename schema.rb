# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.1].define(version: 2025_06_12_145147) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "admin_users", force: :cascade do |t|
    t.string "email", default: "", null: false
    t.string "encrypted_password", default: "", null: false
    t.string "reset_password_token"
    t.datetime "reset_password_sent_at"
    t.datetime "remember_created_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["email"], name: "index_admin_users_on_email", unique: true
    t.index ["reset_password_token"], name: "index_admin_users_on_reset_password_token", unique: true
  end

  create_table "api_request_logs", force: :cascade do |t|
    t.string "vendor_name"
    t.string "username"
    t.string "ip_address"
    t.string "path"
    t.string "request_method"
    t.text "params"
    t.text "response"
    t.integer "status"
    t.boolean "auth_success"
    t.float "api_call_time"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "conditions", force: :cascade do |t|
    t.string "name"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["name"], name: "index_conditions_on_name"
  end

  create_table "drug_conditions", force: :cascade do |t|
    t.bigint "drug_id", null: false
    t.bigint "condition_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["condition_id"], name: "index_drug_conditions_on_condition_id"
    t.index ["drug_id"], name: "index_drug_conditions_on_drug_id"
  end

  create_table "drug_source_drugs", force: :cascade do |t|
    t.bigint "drug_id", null: false
    t.bigint "source_drug_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["drug_id", "source_drug_id"], name: "index_drug_source_drugs_on_drug_id_and_source_drug_id", unique: true
    t.index ["drug_id"], name: "index_drug_source_drugs_on_drug_id"
    t.index ["source_drug_id"], name: "index_drug_source_drugs_on_source_drug_id"
  end

  create_table "drugs", force: :cascade do |t|
    t.string "name"
    t.string "uuid"
    t.boolean "active", default: true
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "class_type"
    t.index ["name"], name: "index_drugs_on_name"
    t.index ["uuid"], name: "index_drugs_on_uuid", unique: true
  end

  create_table "duplicate_programs", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "rx_assist_program_id"
    t.integer "needy_meds_program_id"
    t.integer "drugs_com_program_id"
  end

  create_table "eligibilities", force: :cascade do |t|
    t.string "uninsured", null: false
    t.string "medicare_part_d", null: false
    t.string "prescription_coverage", null: false
    t.string "denied_coverage", null: false
    t.string "commercial", null: false
    t.string "employer", null: false
    t.string "medicare", null: false
    t.string "medicaid", null: false
    t.string "govt", null: false
    t.bigint "program_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "under_insured"
    t.index ["program_id"], name: "index_eligibilities_on_program_id"
  end

  create_table "eligibility_checks", force: :cascade do |t|
    t.boolean "us_resident"
    t.string "uuid", null: false
    t.boolean "has_prescription_coverage"
    t.boolean "has_medicare_part_d"
    t.boolean "ever_coverage_denied"
    t.integer "monthly_household_income"
    t.integer "house_hold_size"
    t.integer "monthly_medication_expense"
    t.integer "insurance_deductible"
    t.bigint "drug_id"
    t.bigint "state_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "insurance_types", default: [], array: true
    t.string "drug_name"
    t.string "gcphtoken"
    t.string "vendor_uuid"
    t.string "vendor_request_uuid"
    t.string "flow"
    t.index ["drug_id"], name: "index_eligibility_checks_on_drug_id"
    t.index ["state_id"], name: "index_eligibility_checks_on_state_id"
    t.index ["uuid"], name: "index_eligibility_checks_on_uuid", unique: true
    t.index ["vendor_request_uuid"], name: "index_eligibility_checks_on_vendor_request_uuid", unique: true
    t.index ["vendor_uuid"], name: "index_eligibility_checks_on_vendor_uuid"
  end

  create_table "eligibility_verdicts", force: :cascade do |t|
    t.string "residency_eligibility", null: false
    t.string "insurance_type", null: false
    t.bigint "program_id"
    t.bigint "eligibility_check_id", null: false
    t.bigint "fpl_household_limit_id"
    t.bigint "income_eligibility_id"
    t.bigint "eligibility_id", null: false
    t.string "prescription_coverage_eligibility"
    t.string "medicare_part_d_eligibility"
    t.string "income_eligibility"
    t.boolean "under_insured"
    t.string "coverage_denied_eligibility"
    t.decimal "deductible_threshold"
    t.decimal "oop_threshold"
    t.string "under_insured_eligibility"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["eligibility_check_id"], name: "index_eligibility_verdicts_on_eligibility_check_id"
    t.index ["eligibility_id"], name: "index_eligibility_verdicts_on_eligibility_id"
    t.index ["fpl_household_limit_id"], name: "index_eligibility_verdicts_on_fpl_household_limit_id"
    t.index ["income_eligibility_id"], name: "index_eligibility_verdicts_on_income_eligibility_id"
    t.index ["program_id"], name: "index_eligibility_verdicts_on_program_id"
  end

  create_table "fpl_household_limits", force: :cascade do |t|
    t.integer "year", null: false
    t.bigint "state_id", null: false
    t.integer "household_size", null: false
    t.integer "limit", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["state_id"], name: "index_fpl_household_limits_on_state_id"
  end

  create_table "income_eligibilities", force: :cascade do |t|
    t.bigint "program_id", null: false
    t.bigint "state_id", null: false
    t.integer "monthly_household_income", default: 0, null: false
    t.integer "household_size", default: 0, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "income_limit_in_percent", default: 999999999, null: false
    t.index ["program_id"], name: "index_income_eligibilities_on_program_id"
    t.index ["state_id"], name: "index_income_eligibilities_on_state_id"
  end

  create_table "patient_detail_submissions", force: :cascade do |t|
    t.string "facility_name"
    t.string "name"
    t.string "email"
    t.string "phone"
    t.string "gcphtoken"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["gcphtoken"], name: "index_patient_detail_submissions_on_gcphtoken"
  end

  create_table "program_changes", force: :cascade do |t|
    t.text "data"
    t.string "source"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "program_conditions", force: :cascade do |t|
    t.bigint "program_id", null: false
    t.bigint "condition_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["condition_id"], name: "index_program_conditions_on_condition_id"
    t.index ["program_id"], name: "index_program_conditions_on_program_id"
  end

  create_table "program_details", force: :cascade do |t|
    t.bigint "program_id", null: false
    t.string "attr", null: false
    t.text "value", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["program_id"], name: "index_program_details_on_program_id"
  end

  create_table "program_links", force: :cascade do |t|
    t.string "name"
    t.text "link"
    t.string "link_type"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "program_id", null: false
    t.index ["program_id"], name: "index_program_links_on_program_id"
  end

  create_table "programs", force: :cascade do |t|
    t.string "name", null: false
    t.string "source", null: false
    t.string "source_id"
    t.text "website"
    t.string "program_type"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "company"
    t.string "category"
    t.bigint "duplicate_program_id"
    t.string "status", default: "open", null: false
    t.integer "max_assistant_amount"
    t.integer "min_assistant_amount"
    t.index ["duplicate_program_id"], name: "index_programs_on_duplicate_program_id"
    t.index ["name"], name: "index_programs_on_name"
  end

  create_table "source_drug_programs", force: :cascade do |t|
    t.bigint "source_drug_id", null: false
    t.bigint "program_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["program_id"], name: "index_source_drug_programs_on_program_id"
    t.index ["source_drug_id"], name: "index_source_drug_programs_on_source_drug_id"
  end

  create_table "source_drugs", force: :cascade do |t|
    t.string "name", null: false
    t.string "source_id"
    t.string "source", null: false
    t.string "equivalent"
    t.boolean "generic"
    t.string "company_name"
    t.string "generic_name"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["name", "source"], name: "index_source_drugs_on_name_and_source", unique: true
  end

  create_table "states", force: :cascade do |t|
    t.string "name"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["name"], name: "index_states_on_name", unique: true
  end

  add_foreign_key "drug_conditions", "conditions"
  add_foreign_key "drug_conditions", "drugs"
  add_foreign_key "drug_source_drugs", "drugs"
  add_foreign_key "drug_source_drugs", "source_drugs"
  add_foreign_key "eligibilities", "programs"
  add_foreign_key "eligibility_checks", "drugs"
  add_foreign_key "eligibility_checks", "states"
  add_foreign_key "eligibility_verdicts", "eligibilities"
  add_foreign_key "eligibility_verdicts", "eligibility_checks"
  add_foreign_key "eligibility_verdicts", "fpl_household_limits"
  add_foreign_key "eligibility_verdicts", "income_eligibilities"
  add_foreign_key "eligibility_verdicts", "programs"
  add_foreign_key "fpl_household_limits", "states"
  add_foreign_key "income_eligibilities", "programs"
  add_foreign_key "income_eligibilities", "states"
  add_foreign_key "program_conditions", "conditions"
  add_foreign_key "program_conditions", "programs"
  add_foreign_key "program_details", "programs"
  add_foreign_key "program_links", "programs"
  add_foreign_key "programs", "duplicate_programs"
  add_foreign_key "source_drug_programs", "programs"
  add_foreign_key "source_drug_programs", "source_drugs"
end
