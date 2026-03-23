import json
import os

import frappe


def load_test_fixtures():
    fixtures_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test")

    fixture_files = [
        "device_type.json",
        "quickfix_settings.json",
        "test_roles.json",
    ]

    fixture_errors = []

    for filename in fixture_files:
        filepath = os.path.join(fixtures_path, filename)
        with open(filepath) as f:
            records = json.load(f)

        for record in records:
            try:
                doc = frappe.get_doc(record)
                doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                frappe.db.commit()
            except Exception as e:
                fixture_errors.append(f"{filename}: {e}")

    if fixture_errors:
        frappe.throw("Fixture load failed:\n" + "\n".join(fixture_errors))
