# Copyright (c) 2026, Sharafath Ahamed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Technician(Document):
	def before_insert(self):
		if not self.email:
			frappe.throw("Email is required to create the linked User for Technician.")

		email = self.email.strip().lower()
		self.email = email

		if not frappe.db.exists("User", email):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": self.technician_name,
					"send_welcome_email": 1,
					"roles": [{"role": "QF Technician"}],
				}
			)
			user.insert(ignore_permissions=True)
			self.user = user.name
		else:
			user = frappe.get_doc("User", email)
			user.add_roles("QF Technician")
			self.user = user.name
