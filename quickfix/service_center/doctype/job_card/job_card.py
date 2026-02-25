# Copyright (c) 2026, Sharafath Ahamed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
	def before_insert(self):
		settings=frappe.db.get_single_value("QuickFix Settings","default_labour_change")
		self.labour_charge=settings
