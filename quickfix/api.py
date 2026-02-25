import frappe


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
def get_job_details_safe():
    return frappe.get_list("Job Card", fields=["name", "status"])