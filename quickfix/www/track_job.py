import frappe
import re

def get_context(context):
    context.no_cache = 1
    context.title = "Track My Job"
    context.jobs = []
    context.error = None

    phone = frappe.form_dict.get("phone", "").strip()

    if not phone:
        return

    if not re.match(r"^\d{10}$", phone):
        context.error = "Invalid phone number. Must be exactly 10 digits."
        return

    ip = frappe.local.request_ip
    cache_key = f"track_job_rate_{ip}"
    count = frappe.cache().get_value(cache_key) or 0

    if int(count) >= 10:
        context.error = "Too many requests. Please try again later."
        return

    frappe.cache().set_value(cache_key, int(count) + 1, expires_in_sec=60)

    exists = frappe.db.exists("Job Card", {"customer_phone": phone})
    if not exists:
        context.error = "No jobs found for this phone number."
        return

    context.jobs = frappe.get_all("Job Card",
        filters={"customer_phone": phone},
        fields=["name", "status", "device_type", "device_brand", "creation"]
    )