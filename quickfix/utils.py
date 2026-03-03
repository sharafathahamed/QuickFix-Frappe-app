import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def updated_technician_id(old_name,new_name):
    frappe.rename_doc("Technician",old_name,new_name,merge=False)
    return f"Succesfull update {old_name} to {new_name}"

    #merge=True is dangerous because it combines two different records into one.
def get_shop_name():
    return frappe.db.get_single_value("QuickFix Settings", "shop_name")

def format_job_id(txt):
    return f"JOB#{txt or ''}"

def send_urgent_alert(manager, job_card):
    subject = "URGENT: Technician in need"
    message = f"The Job card {job_card} is in need of technician urgently. Assign it!"
    frappe.sendmail(
        recipients=manager,
        subject=subject,
        message=message,
        now=True
    )

def send_job_ready_email(job_card):
    job = frappe.get_doc("Job Card", job_card)
    if not job.customer_email:
        return

    frappe.sendmail(
        recipients=[job.customer_email],
        subject=f"Your device is ready - {job.name}",
        message=f"Hi {job.customer_name or 'Customer'}, your job card {job.name} is ready for delivery.",
        now=True,
    )
def valid_external(doc,method):
    frappe.msgprint("Running doc_events validation")


def handle_session_creation(login_manager):
    user = login_manager.user if login_manager else frappe.session.user
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "System",
        "document_name": user,
        "action": "Login",
        "user": user,
        "timestamp": now_datetime(),
    }).insert(ignore_permissions=True)

def handle_logout(login_manager):
    user = frappe.session.user
    if not user or user == "Guest":
        return
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "System",
        "document_name": user,
        "action": "Logout",
        "user": user,
        "timestamp": now_datetime(),
    }).insert(ignore_permissions=True)
