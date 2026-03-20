import frappe
from frappe.utils import now, now_datetime, today

@frappe.whitelist()
def updated_technician_id(old_name,new_name):
    frappe.rename_doc("Technician",old_name,new_name,merge=False)
    return f"Succesfull update {old_name} to {new_name}"

    #merge=True is dangerous because it combines two different records into one.
def get_shop_name():
    return frappe.db.get_single_value("QuickFix Settings", "shop_name")

def check_low_stock():
    last_run=frappe.db.get_value(
        "Audit Log",
        {"action":"low_stock_check","creation":["like",f"{today()}%"]},
        "name"
    )
    if last_run:
        return
    
    frappe.get_doc({
        "doctype": "Audit Log",
        "action": "low_stock_check",
        "doctype_name": "System",
        "document_name": "Daily Low Stock Check",
        "user": "Administrator",
        "timestamp": now()
    }).insert(ignore_permissions=True)
    frappe.db.commit()

def failing_job():
    raise Exception("Deliberate failure for testing RQ error handling")
    
def get_qr_code(job_card_name):
    import qrcode
    import base64
    from io import BytesIO
    url=f"{frappe.utils.get_url()}/app/job-card/{job_card_name}"
    qr= qrcode.make(url)
    buffer=BytesIO()
    qr.save(buffer,format="PNG")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def generate_monthly_revenue_report():
    job_cards=frappe.get_all("Job Card",
            filters={"status":"Delivered"},
            fields=["name","final_amount","delivery_date"])
    frappe.log_error("Monthly revenue report generated","Report")

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


def extend_bootinfo(bootinfo):
    from quickfix.boot import extend_bootinfo as boot_extend_bootinfo
    return boot_extend_bootinfo(bootinfo)

def handle_session_creation(login_manager):
    user = login_manager.user if login_manager else frappe.session.user
    try:
        frappe.get_doc({
            "doctype": "Audit Log",
            "doctype_name": "System",
            "document_name": user,
            "action": "Login",
            "user": user,
            "timestamp": now_datetime(),
        }).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "QuickFix Session Creation Hook Failed")

def handle_logout(login_manager):
    user = frappe.session.user
    if not user or user == "Guest":
        return
    try:
        frappe.get_doc({
            "doctype": "Audit Log",
            "doctype_name": "System",
            "document_name": user,
            "action": "Logout",
            "user": user,
            "timestamp": now_datetime(),
        }).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "QuickFix Logout Hook Failed")

def send_webhook(job_card_name, retry_count=0):
    import requests,hashlib
    settings=frappe.get_single("QuickFix Settings")
    if not settings.webhook_url:
        return
    doc = frappe.get_doc("Job Card", job_card_name)
    payload={
        "event":"job_submitted",
        "job_card": doc.name,
        "amount": doc.final_amount
    }
    webhook_id=hashlib.md5(
        f"{doc.name}job_submitted".encode()
    ).hexdigest()
    if frappe.db.exists("Audit Log",{"action":"webhook_sent","document_name":webhook_id}):
        return
    try:
        r=requests.post(settings.webhook_url,json=payload,timeout=5)
        r.raise_for_status()
        frappe.get_doc({
            "doctype": "Audit Log",
            "doctype_name": "Job Card",
            "document_name": webhook_id,
            "action": "webhook_sent",
            "user": "Administrator"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Webhook failed: {e}", "Webhook Error")
        if retry_count < 3:
            frappe.enqueue(
                "quickfix.utils.send_webhook",
                queue="short",
                job_card_name=job_card_name,
                retry_count=retry_count + 1,
                enqueue_after_commit=True,
                at_front=False,
                eta=60 
            )
            
