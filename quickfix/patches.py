import frappe


def apply_patches(*args, **kwargs):
	frappe.logger("quickfix").info("QuickFix patches hook loaded; no runtime patches applied")
