import frappe

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