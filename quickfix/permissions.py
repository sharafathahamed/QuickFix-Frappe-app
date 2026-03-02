import frappe

def get_permission_query_conditions(user):
    if not user:
        user=frappe.session.user
    roles=frappe.get_roles(user)
    if "QF Manager" in roles or "Administrator" in roles or "System Manager" in roles or "QF Service Staff":
        return ""
    if "QF Technician" in roles:    
        return f"assigned_technician = (select name from `tabTechnician` where user='{user}')"
    return "1=0"
def has_permission(doc,ptype,user=None):
    if not user:
        user=frappe.session.user
    roles=frappe.get_roles(user)
    if "QF Manager" in roles or "Administrator" in roles or "System Manager" in roles:
        return True
    if doc.doctype == "Service Invoice" and doc.get("job_card"):
        payment_status=frappe.db.get_value("Job Card", doc.job_card,"payment_status")
        return payment_status == "Paid"
    return False