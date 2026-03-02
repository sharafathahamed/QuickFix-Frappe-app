import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def updated_technician_id(old_name,new_name):
    frappe.rename_doc("Technician",old_name,new_name,merge=False)
    return f"Succesfull update {old_name} to {new_name}"

    #merge=True is dangerous because it combines two different records into one.

def send_urgent_alert(manager,job_card,self):
    subject=f"URGENT: Technician in need"
    message=f"The Job card {job_card} is in need of technician urgently. Assign it!"
    frappe.sendmail(
        recipients=manager,
        subject=subject,
        content=message,
        now=True
    )
def valid_external(doc,method):
    frappe.msgprint("Running doc_events validation")


def extend_bootinfo(bootinfo):
    if not frappe.db.exists("QuickFix Settings", "QuickFix Settings"):
        return

    settings = frappe.get_single("QuickFix Settings")
    bootinfo.quickfix_shop_name = settings.shop_name
    bootinfo.quickfix_manager_email = settings.manager_email


def log_session_event(user=None, event_type=None):
    action = event_type or "Session Event"

    frappe.get_doc(
        {
            "doctype":"Audit Log",
            "doctype_name":"System",
            "document_name": user,
            "action":action,
            "user":user,
            "timestamp": now_datetime(),
        }
    ).insert(ignore_permissions=True)
