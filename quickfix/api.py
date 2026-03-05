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