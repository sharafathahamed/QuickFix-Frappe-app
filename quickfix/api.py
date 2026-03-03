import frappe
from frappe.client import get_count as original_get_count

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
def custom_get_count(doctype,filters=None, debug=None, cache=None):
    frappe.get_doc({"doctype":"Audit Log",
                    "doctype_name":doctype,
                    "action":"count_queried",
                    "user":frappe.session.user
                    }).insert(ignore_permissions=True)
    return original_get_count(doctype, filters, debug, cache)

@frappe.whitelist()
def get_job_details_safe():
    return frappe.get_list("Job Card", fields=["name", "status"])

#Unsafe
@frappe.whitelist()
def get_job_unsafe():
    return frappe.get_all("Job Card",fields=["*"])