import frappe

def get_permission_query_conditions(user):
    if not user:
        user=frappe.session.user
    if "QF Technician" in frappe.get_roles(user):
        return f"assigned_technician = (select name from `tabTechnician` where user='{user}')"
    
def has_permission(doc,ptype,user):
    if "QF Manager" in frappe.get_roles(user):
        return True
    payment_status=frappe.db.get_value("Job Card", doc.job_card,"payment_status")
    return payment_status == "Paid"