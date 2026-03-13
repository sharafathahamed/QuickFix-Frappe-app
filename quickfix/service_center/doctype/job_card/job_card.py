# Copyright (c) 2026, Sharafath Ahamed and contributors
# For license information, please see license.txt

import frappe
import logging
from frappe.model.document import Document
from frappe.utils import flt

logger = logging.getLogger(__name__)

class JobCard(Document):
	def validate(self):
		frappe.msgprint("Running Controller Validation")
		phone = (self.customer_phone or "").strip()
		if len(phone) != 10 or not phone.isdigit():
			frappe.throw("Number should be exactly 10")

		status = self.status or "Draft"
		if status not in ["Draft","Pending Diagnosis","Awaiting Customer Approval"] and not self.assigned_technician:
			frappe.throw("Assign Technician First!!")

		settings=frappe.db.get_single_value("QuickFix Settings","default_labour_change")
		if self.assigned_technician:
			specialization=frappe.db.get_value("Technician", self.assigned_technician,"specialization")
			if(specialization!=self.device_type):
				frappe.throw(f"The assigned technician is specialized in {specialization} and it doesnt match for {self.device_type}")
		
		self.labour_charge=settings
		self.calculate_total()

	def calculate_total(self):
		parts_total=0
		for row in self.parts_used:
			row.total_price=row.quantity*row.unit_price
			parts_total+=row.total_price
		self.parts_total=parts_total
		self.final_amount = self.parts_total + self.labour_charge
		self.amount=self.final_amount
		
	def before_print(self, settings=None):
		self.print_summary = f"{self.customer_name} - {self.device_brand} {self.device_model}"

	def before_submit(self):
		if self.status!="Ready for Delivery":
			frappe.throw("Can't Submit without 'Ready for Delivery'")
		for row in self.parts_used:
			curr_stck=frappe.db.get_value("Spare Part",row.part,"stock_qty")
			if flt(curr_stck)<flt(row.quantity):
				part_label = row.data or row.part
				frappe.throw(f"Insufficient Stock for {part_label}. Available: {curr_stck}, Required: {row.quantity}")

	def on_submit(self):
		frappe.enqueue(
			"quickfix.utils.send_webhook",
			queue="short",
			job_card_name=self.name
		)
		for row in self.parts_used:
			curr_stk=frappe.db.get_value("Spare Part",row.part,"stock_qty")
			
			frappe.db.set_value("Spare Part",
						row.part,
						"stock_qty",
						flt(curr_stk)-flt(row.quantity))
			
		invoice= frappe.get_doc({
			"doctype":"Service Invoice",
			"job_card":self.name,
			"labour_charge": self.labour_charge,
			"parts_total": self.parts_total,
			"total_amount": self.final_amount
		})
		invoice.insert(ignore_permissions=True)
		frappe.publish_realtime("job_ready",{
			"job": self.name
			},user=self.owner)
		frappe.enqueue("quickfix.utils.send_job_ready_email", queue="short",job_card=self.name)
		self.send_completion_email()
	def send_completion_email(self):
		try:
			# Correct way in Frappe 15
			pdf = frappe.get_print(
				doctype="Job Card",
				name=self.name,
				print_format="Job Card Receipt",
				as_pdf=True
			)
			
			frappe.sendmail(
				recipients=[self.customer_email],
				subject=f"Job Card {self.name} - Ready for Delivery",
				message=f"""
					Dear {self.customer_name},<br><br>
					Your device is ready for delivery.<br>
					Job ID: {self.name}<br>
					Total Amount: {self.final_amount}<br><br>
					Regards
				""",
				attachments=[{
					"fname": f"{self.name}.pdf",
					"fcontent": pdf
				}]
			)
			frappe.logger("quickfix").info(f"Completion email sent for {self.name}")
			
		except Exception as e:
			frappe.logger("quickfix").error(f"Email failed for {self.name}: {e}")
			frappe.log_error(
				title="Job Completion Email Failed",
				message=frappe.get_traceback()
			)

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
		frappe.cache().delete_value("quickfix_status_chart_data")