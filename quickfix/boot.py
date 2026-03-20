import frappe


def extend_bootinfo(bootinfo):
    try:
        settings = frappe.get_cached_doc("QuickFix Settings", "QuickFix Settings")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "QuickFix Boot Hook Failed")
        bootinfo.quickfix_shop_name = "QuickFix"
        bootinfo.quickfix_manager_email = None
        return
    bootinfo.quickfix_shop_name = settings.shop_name or "QuickFix"
    bootinfo.quickfix_manager_email = settings.manager_email
