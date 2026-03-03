import frappe

def extend_bootinfo(bootinfo):
    settings = frappe.get_doc("QuickFix Settings")

    bootinfo.quickfix_shop_name = settings.shop_name or "QuickFix"
    bootinfo.quickfix_manager_email = settings.manager_email