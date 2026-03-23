import frappe
from frappe import _


def after_install():
	default_types = ["Laptop", "SmartPhone", "Tablet"]
	for def_type in default_types:
		if not frappe.db.exists("Device Type", def_type):
			frappe.get_doc({"doctype": "Device Type", "device_type": def_type}).insert(
				ignore_permissions=True
			)
	if not frappe.db.exists("QuickFix Settings", "QuickFix Settings"):
		frappe.get_doc(
			{
				"doctype": "QuickFix Settings",
				"shop_name": "ABC Electronics",
				"manager_email": "admin@example.com",
				"default_labour_charge": 500.0,
				"low_stock_threshold": 1,
			}
		).insert(ignore_permissions=True)
	frappe.make_property_setter(
		{
			"doctype": "Job Card",
			"fieldname": "remarks",
			"property": "bold",
			"value": "1",
			"property_type": "Check",
		}
	)

	frappe.db.commit()

	frappe.msgprint(_("Quickfix app is succesfully installed with default setting"))


def before_uninstall():
	if frappe.db.exists("Job Card", {"docstatus": 0}):
		frappe.throw(("Cancel draft Job Cards before uninstall"), frappe.ValidationError)
