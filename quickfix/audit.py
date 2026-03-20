import frappe
from frappe.utils import now_datetime


def log_change(doc, method):
    if doc.doctype=="Audit Log":
        return
    frappe.get_doc({
        "doctype":"Audit Log",
        "doctype_name":doc.doctype,
        "document_name":doc.name,
        "action":method,
        "user":frappe.session.user,
        "timestamp":now_datetime()
    }).insert(ignore_permissions=True)
