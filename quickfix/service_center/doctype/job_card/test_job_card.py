import frappe
import unittest

class TestJobCard(unittest.TestCase):
    def test_super_call_integrity(self):
        job = frappe.get_doc({
            "doctype": "Job Card",
            "customer_name": "Test Customer",
            "priority": "Urgent",
            "parts_used": [
                {
                    "spare_part": "Battery", 
                    "qty": 1,
                    "rate": 1000
                }
            ],
            "labour_charge": 500
        })
        job.insert()
        self.assertNotEqual(job.final_amount, 0, "Core validate() was bypassed! final_amount is still 0.")