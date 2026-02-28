# Copyright (c) 2026, Sharafath Ahamed and contributors
# For license information, please see license.txt

from erpnext.crm.frappe_crm_api import link_doc
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class JobCard(Document):
	def validate(self):
		if len(self.customer_phone)!=10:
			frappe.throw("Number should be exactly 10")

		if self.status not in ["Draft","Pending Diagnosis","Awaiting Customer Approval"] and not self.assigned_technician:
			frappe.throw("Assign Technician First!!")

		settings=frappe.db.get_single_value("QuickFix Settings","default_labour_change")
		
		self.labour_charge=settings
		self.calculate_total()

	def calculate_total(self):
		parts_total=0

		for row in self.parts_used:
			row.total_price=row.quantity*row.unit_price
			parts_total+=row.total_price

		self.parts_total=parts_total
		self.final_amount = self.parts_total + self.labour_charge
		

	def before_submit(self):
		if self.status!="Ready for Delivery":
			frappe.throw("Can't Submit without 'Ready for Delivery'")

		for row in self.parts_used:
			curr_stck=frappe.db.get_value("Spare Part",row.part,"sock_qty")

			if flt(curr_stck)<flt(row.quantity):
				frappe.throw(f"Insufficient Stock for {row.part_name}. Available: {curr_stck}, Required: {row.quantity}")

	def on_submit(self):
		for row in self.parts_used:
			curr_stk=frappe.db.get_value("Spare Part",row.part,"sock_qty")
			
			frappe.db.set_value("Spare Part",
					   row.part,
					   "sock_qty",
					   flt(curr_stk)-flt(row.quantity), 
					   ignore_permissions=True)

		invoice= frappe.get_doc({
			"doctype":"Service Invoice",
			"job_card":self.name,
			"labour_charge": self.labour_charge,
            "parts_total": self.parts_total,
            "total_amount": self.final_amount
		})

		invoice.insert(ignore_permissions=True)
		frappe.publish_realtime("job_ready",{
			"job:":self.name
		},user=self.owner)
		frappe.enqueue("quickfix.utils.send_job_ready_email", job_card=self.name)

	def on_cancel(self):
		self.db_set("status", "Cancelled")
		for row in self.parts_used:
			current_stock = frappe.db.get_value("Spare Part", row.part, "stock_qty")
			frappe.db.set_value("Spare Part", row.part, "stock_qty", flt(current_stock) + flt(row.quantity))
		invoice_name = frappe.db.get_value("Service Invoice", {"job_card": self.name}, "name")

		if invoice_name:
			inv_doc = frappe.get_doc("Service Invoice", invoice_name)
			inv_doc.cancel()

	def on_trash(self):
		if self.status not in ["Draft", "Cancelled"]:
			frappe.throw("You can only delete only if you cancel")
	
	def on_update(self):
		self.save()