import frappe
from frappe.client import get_count as original_get_count
from frappe.utils import now_datetime

logger = frappe.logger("quickfix", allow_site=True)

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
def send_webhook(job_card_name):
    logger.info(f"Webhook triggered for {job_card_name}")

    settings = frappe.get_single("QuickFix Settings")
    if not settings.webhook_url:
        logger.warning(f"No webhook URL configured, skipping for {job_card_name}")
        return

    import requests
    try:
        doc = frappe.get_doc("Job Card", job_card_name)
        payload = {
            "event": "job_submitted",
            "job_card": doc.name,
            "amount": doc.final_amount
        }
        r = requests.post(settings.webhook_url, json=payload, timeout=5)
        r.raise_for_status()
        logger.info(f"Webhook sent successfully for {job_card_name}")

    except Exception as e:
        logger.error(f"Webhook failed for {job_card_name}: {e}")
        frappe.log_error(
            title="Webhook Error",
            message=frappe.get_traceback()
        )

@frappe.whitelist()
def trigger_test_error():
    frappe.enqueue(
        "quickfix.api.failing_background_job",
        queue="short"
    )

def failing_background_job():
    raise Exception("Test background job failure for M3")

@frappe.whitelist()
def get_status_chart_data():
    cache_key = "quickfix_status_chart_data"
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return cached
    statuses = [
        "Draft", "Pending Diagnosis", "Awaiting Customer Approval",
        "In Repair", "Ready for Delivery", "Delivered", "Cancelled"
    ]
    values = []
    for status in statuses:
        count = frappe.db.count("Job Card", {"status": status})
        values.append(count)
    data = {
        "labels": statuses,
        "datasets": [{"name": "Job Cards", "values": values}]
    }
    frappe.cache().set_value(cache_key, data, expires_in_sec=300)
    return data

@frappe.whitelist(allow_guest=True)
def get_job_by_phone(phone):
    import re
    if not phone or not re.match(r"^\d{10}$", str(phone)):
        frappe.throw("Invalid phone number. Must be exactly 10 digits.")
    ip = frappe.local.request_ip
    cache_key = f"rate_limit_{ip}"
    count = frappe.cache().get_value(cache_key) or 0

    if int(count) >= 3:
        frappe.throw("Too many requests. Please try again later.")

    frappe.cache().set_value(cache_key, int(count) + 1, expires_in_sec=60)

    exists = frappe.db.exists("Job Card", {"customer_phone": phone})
    if not exists:
        frappe.throw("No jobs found for this phone number.")

    jobs = frappe.get_all("Job Card",
        filters={"customer_phone": phone},
        fields=["name", "status", "device_type", "device_brand", "creation"]
    )
    return jobs

@frappe.whitelist(allow_guest=True)
def payment_webhook():
    import hashlib
    import hmac
    import json
    payload = frappe.request.data
    secret = frappe.conf.get("payment_webhook_secret", "")
    signature=frappe.get_request_header("X-Signature")
    expected=hmac.new(secret.encode(),payload,hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected,signature or ""):
        frappe.throw("Invalid signature", frappe.AuthenticationError)

    data = json.loads(payload)

    if frappe.db.exists("Audit Log", {
        "action": "payment_received",
        "document_name": data.get("ref")
    }):
        return {"status": "duplicate", "message": "Already processed"}

    if data.get("job_card"):
        frappe.db.set_value("Job Card", data["job_card"], "payment_status", "Paid")

    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Job Card",
        "document_name": data.get("ref"),
        "action": "payment_received",
        "user": "Administrator"
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist(methods=["GET", "POST"])
def get_job_summary(job_card_name=None):
    if not job_card_name:
        job_card_name = frappe.form_dict.get("job_card_name")

    if not frappe.db.exists("Job Card", job_card_name):
        frappe.response.http_status_code = 404
        return {"error": "Not found"}

    doc = frappe.get_doc("Job Card", job_card_name)

    return {
        "name": doc.name,
        "status": doc.status,
        "customer_name": doc.customer_name,
        "device_type": doc.device_type,
        "device_brand": doc.device_brand,
        "device_model": doc.device_model,
        "assigned_technician": doc.assigned_technician
    }

@frappe.whitelist()
def get_technician_work_summary():
    job_cards = frappe.get_all(
        "Job Card",
        fields=["name", "assigned_technician"]
    )
    tech_ids = [jc.assigned_technician for jc in job_cards if jc.assigned_technician]
    if not tech_ids:
        return []
    technicians = frappe.get_all(
        "Technician",
        filters={"name": ["in", tech_ids]},
        fields=["name", "technician_name", "phone"]
    )
    tech_map = {t.name: t for t in technicians}
    for jc in job_cards:
        tech = tech_map.get(jc.assigned_technician)
        if tech:
            return tech.technician_name, tech.phone


@frappe.whitelist()
def cancel_old_draft_jobs():
    import time
    start = time.time()
    frappe.db.sql("""
        UPDATE `tabJob Card`
        SET status = 'Cancelled'
        WHERE status = 'Draft'
        AND creation < DATE_SUB(NOW(), INTERVAL 365 DAY)
        LIMIT 1000
    """)
    frappe.db.commit()
    sql_time = time.time() - start
    frappe.log_error(f"SQL UPDATE time: {sql_time}", "Benchmark")
    return f"Done in {sql_time} seconds"

@frappe.whitelist()
def bulk_insert_audit_logs():
    import time

    start = time.time()
    records = []
    for i in range(50):
        records.append([
            f"BULK-TEST-{frappe.generate_hash(length=6)}",
            "Job Card",
            f"TEST-{i}",
            "bulk_test",
            "Administrator"
        ])
    frappe.db.bulk_insert(
        "Audit Log",
        fields=["name", "doctype_name", "document_name", "action", "user"],
        values=records,
        ignore_duplicates=True
    )
    frappe.db.commit()
    bulk_time = time.time() - start
    frappe.log_error(f"Bulk insert time: {bulk_time}", "Benchmark")
    return f"Done in {bulk_time} seconds"

@frappe.whitelist()
def manager_only_action():
    frappe.only_for("QF Manager")
    return "Manager action allowed"

@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
    frappe.get_doc(
        {
            "doctype": "Audit Log",
            "doctype_name": doctype,
            "document_name": doctype,
            "action": "count_queried",
            "user": frappe.session.user,
            "timestamp": now_datetime(),
        }
    ).insert(ignore_permissions=True)
    frappe.db.commit()
    return original_get_count(doctype, filters, debug, cache)

@frappe.whitelist()
def get_job_details_safe():
    return frappe.get_list("Job Card", fields=["name", "status"])

#Unsafe
@frappe.whitelist()
def get_job_unsafe():
    return frappe.get_all("Job Card",fields=["*"])

@frappe.whitelist()
def reject_job(job_card, reason):
    doc=frappe.get_doc("Job Card",job_card)
    doc.status="Cancelled"
    doc.remarks=f"Rejected {reason}"
    doc.save(ignore_permissions=True)
    return "rejected"

@frappe.whitelist()
def transfer_technician(job_card, new_technician):
    frappe.db.set_value(
        "Job Card",
        job_card,
        "assigned_technician", new_technician
    )
    frappe.db.commit()
    return "transferred"

# UNSAFE - f-string SQL (NEVER do this)
@frappe.whitelist()
def unsafe_search(customer_name):
    # VULNERABLE TO SQL INJECTION
    results = frappe.db.sql(f"""
        SELECT name, customer_name, status
        FROM `tabJob Card`
        WHERE customer_name = '{customer_name}'
    """, as_dict=True)
    return results

@frappe.whitelist()
def safe_search(customer_name):
    results = frappe.db.sql("""
        SELECT name, customer_name, status
        FROM `tabJob Card`
        WHERE customer_name = %s
    """, (customer_name,), as_dict=True)
    return results

@frappe.whitelist()
def escaped_search(customer_name):
    escaped = frappe.db.escape(customer_name)
    results = frappe.db.sql(f"""
        SELECT name, customer_name, status
        FROM `tabJob Card`
        WHERE customer_name = {escaped}
    """, as_dict=True)
    return results

@frappe.whitelist(allow_guest=True)
def track_job_by_phone(phone=None):
    import re

    if not phone or not re.match(r"^\d{10}$", str(phone)):
        frappe.throw("Invalid phone number. Must be exactly 10 digits.")

    ip = frappe.local.request_ip
    cache_key = f"track_job_rate_{ip}"
    count = frappe.cache().get_value(cache_key) or 0

    if int(count) >= 10:
        frappe.throw("Too many requests. Please try again later.")

    frappe.cache().set_value(cache_key, int(count) + 1, expires_in_sec=60)

    exists = frappe.db.exists("Job Card", {"customer_phone": phone})
    if not exists:
        frappe.throw("No jobs found for this phone number.")

    jobs = frappe.get_all("Job Card",
        filters={"customer_phone": phone},
        fields=["name", "status", "device_type", "device_brand", "creation"]
    )
    return jobs
