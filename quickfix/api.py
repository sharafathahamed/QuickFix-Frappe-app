import frappe
from frappe.client import get_count as original_get_count
from frappe.utils import now_datetime

@frappe.whitelist()
def share_job_card(job_card_name, user_email):
    frappe.share.add(
        "Job Card",
        job_card_name,
        user_email,
        read=1
    )
    return "Shared successfully"

@frappe.whitelist()
def get_technician_work_summary():
    job_cards = frappe.get_all(
        "Job Card",
        fields=["name", "assigned_technician"]
    )
    tech_ids = [jc.assigned_technician for jc in job_cards if jc.assigned_technician]
    if not tech_ids:
        return []
    technicians = frappe.get_all(
        "Technician",
        filters={"name": ["in", tech_ids]},
        fields=["name", "technician_name", "phone"]
    )
    tech_map = {t.name: t for t in technicians}
    for jc in job_cards:
        tech = tech_map.get(jc.assigned_technician)
        if tech:
            print(tech.technician_name, tech.phone)


@frappe.whitelist()
def cancel_old_draft_jobs():
    import time
    start = time.time()
    frappe.db.sql("""
        UPDATE `tabJob Card` 
        SET status = 'Cancelled'
        WHERE status = 'Draft'
        AND creation < DATE_SUB(NOW(), INTERVAL 365 DAY)
        LIMIT 1000
    """)
    frappe.db.commit()
    sql_time = time.time() - start
    frappe.log_error(f"SQL UPDATE time: {sql_time}", "Benchmark")
    return f"Done in {sql_time} seconds"

@frappe.whitelist()
def bulk_insert_audit_logs():
    import time
    
    start = time.time()
    records = []
    for i in range(50):
        records.append([
            f"BULK-TEST-{i}",
            "Job Card",
            f"TEST-{i}",
            "bulk_test",
            "Administrator"
        ])
    frappe.db.bulk_insert(
        "Audit Log",
        fields=["name", "doctype_name", "document_name", "action", "user"],
        values=records
    )
    frappe.db.commit()
    bulk_time = time.time() - start
    frappe.log_error(f"Bulk insert time: {bulk_time}", "Benchmark")
    return f"Done in {bulk_time} seconds"

@frappe.whitelist()
def manager_only_action():
    frappe.only_for("QF Manager")
    return "Manager action allowed"

@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
    frappe.get_doc(
        {
            "doctype": "Audit Log",
            "doctype_name": doctype,
            "document_name": doctype,
            "action": "count_queried",
            "user": frappe.session.user,
            "timestamp": now_datetime(),
        }
    ).insert(ignore_permissions=True)
    frappe.db.commit()
    return original_get_count(doctype, filters, debug, cache)

@frappe.whitelist()
def get_job_details_safe():
    return frappe.get_list("Job Card", fields=["name", "status"])

#Unsafe
@frappe.whitelist()
def get_job_unsafe():
    return frappe.get_all("Job Card",fields=["*"])

@frappe.whitelist()
def reject_job(job_card, reason):
    doc=frappe.get_doc("Job Card",job_card)
    doc.status="Cancelled"
    doc.remarks=f"Rejected {reason}"
    doc.save(ignore_permissions=True)
    return "rejected"

@frappe.whitelist()
def transfer_technician(job_card, new_technician):
    frappe.db.set_value(
        "Job Card",
        job_card,
        "assigned_technician", new_technician
    )
    frappe.db.commit()
    return "transferred"

@frappe.whitelist()
def get_status_chart_data():
    statuses = [
        "Draft",
        "Pending Diagnosis", 
        "Awaiting Customer Approval",
        "In Repair",
        "Ready for Delivery",
        "Delivered",
        "Cancelled"
    ]
    values = []
    for status in statuses:
        count = frappe.db.count("Job Card", {"status": status})
        values.append(count)
    
    return {
        "labels": statuses,
        "datasets": [{"name": "Job Cards", "values": values}]
    }