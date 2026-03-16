import frappe
import unittest
from frappe.tests.utils import FrappeTestCase

def make_device_type(device_type="Smartphone"):
    if not frappe.db.exists("Device Type",device_type):
        doc=frappe.get_doc({
            "doctype":"Device Type",
            "device_type":device_type,
            "description":f"Test {device_type}",
            "average_repair_hours":2
        })
        doc.insert(ignore_permissions=True)
        return doc
    return frappe.get_doc("Device Type", device_type)

def make_technician(**kwargs):
    specialization = kwargs.get("specialization", "Smartphone")
    make_device_type(specialization)
    defaults = {
        "doctype": "Technician",
        "technician_name": "Test Technician",
        "phone": "9876543210",
        "email": "tech@quickfix.test",
        "specialization": specialization,
        "status": "Active",
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc

def make_spare_part(stock_qty=10, **kwargs):
    part_code = kwargs.pop("part_code", f"TEST-PART-{frappe.generate_hash(length=6).upper()}")
    defaults = {
        "doctype": "Spare Part",
        "part_name": "Test Screen",
        "part_code": part_code,
        "unit_cost": 500.0,
        "selling_price": 700.0,
        "stock_qty": stock_qty,
        "reorder_level": 2,
        "is_active": 1,
    }
    defaults.update(kwargs)

    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc

def make_job_card(technician=None, spare_part=None, **kwargs):
    device_type_doc = make_device_type("Smartphone")

    if technician is None:
        technician = make_technician(specialization="Smartphone")

    if spare_part is None:
        spare_part = make_spare_part(stock_qty=10)

    defaults = {
        "doctype": "Job Card",
        "customer_name": "Test Customer",
        "customer_phone": "9876543210",
        "customer_email": "customer@test.com",
        "device_type": device_type_doc.name,
        "device_brand": "Apple",
        "device_model": "iPhone 13",
        "problem_description": "Screen cracked",
        "assigned_technician": technician.name,
        "diagnosis_notes": "Screen replacement needed",
        "estimated_cost": 700.0,
        "diagnosis_date": frappe.utils.today(),
        "priority": "Normal",
        "status": "Ready for Delivery",
        "labour_charge": 500.0,
        "parts_used": [
            {
                "part": spare_part.name,
                "part_name": spare_part.part_name,
                "unit_price": spare_part.selling_price,
                "quantity": 1,
                "total_price": spare_part.selling_price,
            }
        ],
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc



class TestJobCard(FrappeTestCase):
    def setUp(self):
        self.device_type = make_device_type("Smartphone")
        self.technician = make_technician(specialization="Smartphone")
        self.spare_part = make_spare_part(stock_qty=10)
