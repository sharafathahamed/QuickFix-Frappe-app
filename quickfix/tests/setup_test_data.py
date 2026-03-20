import frappe
import json
import os

def load_test_fixtures():
    fixtures_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "fixtures",
        "test"
    )

    fixture_files = [
        "device_type.json",
        "quickfix_settings.json",
        "test_roles.json",
    ]

    for filename in fixture_files:
        filepath = os.path.join(fixtures_path, filename)
        with open(filepath, "r") as f:
            records = json.load(f)

        for record in records:
            try:
                doc = frappe.get_doc(record)
                doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(
                    title=f"Fixture load failed: {filename}",
                    message=str(e)
                )

    print("Test fixtures loaded successfully")