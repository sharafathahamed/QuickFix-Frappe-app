# Copyright (c) 2026, Sharafath Ahamed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class SparePart(Document):
	def validate(self):
		if self.selling_price<=self.unit_cost:
			frappe.throw("Selling price must be greater than unit cost")
	def autoname(self):
		self.part_code=self.part_code.upper()
		self.name = make_autoname(f"{self.part_code}-.####")
	def on_update(self):
		low_stock_theshold=frappe.db.get_value(
			"QuickFix Settings", None, "low_stock_threshold"
		)
		threshold=float(low_stock_theshold or 0)
		if self.stock_qty<threshold:
			frappe.msgprint(
				msg=f"Item {self.name} is below the threshold: Current stock {self.stock_qty}",
				title="Low Stock Warning",
				indicator="orange"
			)