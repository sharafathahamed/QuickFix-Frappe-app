import frappe

no_cache = 1


def get_context(context):
    context.no_cache = 1
    context.title = "Track Job"
    context.route_ok = True
    context.job_id = frappe.form_dict.get("job_id")
    context.request_path = (
        frappe.local.request.path
        if getattr(frappe.local, "request", None)
        else None
    )
