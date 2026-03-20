import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt


def make_device_type(device_type="Smartphone"):
    if not frappe.db.exists("Device Type", device_type):
        doc = frappe.get_doc(
            {
                "doctype": "Device Type",
                "device_type": device_type,
                "description": f"Test {device_type}",
                "average_repair_hours": 2,
            }
        )
        doc.insert(ignore_permissions=True)
        return doc
    return frappe.get_doc("Device Type", device_type)


def make_technician(**kwargs):
    specialization = kwargs.get("specialization", "Smartphone")
    make_device_type(specialization)

    defaults = {
        "doctype": "Technician",
        "technician_name": "Test Technician",
        "phone": "+919876543210",
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
                "unit_price": spare_part.unit_cost,
                "quantity": 1,
                "total_price": spare_part.unit_cost,
            }
        ],
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc


class TestJobCardValidation(FrappeTestCase):
    def setUp(self):
        self.device_type = make_device_type("Smartphone")
        self.technician = make_technician(specialization="Smartphone")
        self.spare_part = make_spare_part(stock_qty=10)

    def test_job_card_can_be_created(self):
        doc = make_job_card(
            technician=self.technician,
            spare_part=self.spare_part,
        )
        self.assertTrue(frappe.db.exists("Job Card", doc.name))
        self.assertEqual(doc.docstatus, 0)

    def test_rejects_short_phone_number(self):
        with self.assertRaisesRegex(frappe.ValidationError, "Number should be exactly 10"):
            make_job_card(
                technician=self.technician,
                spare_part=self.spare_part,
                customer_phone="123456789",
            )

    def test_rejects_long_phone_number(self):
        with self.assertRaisesRegex(frappe.ValidationError, "Number should be exactly 10"):
            make_job_card(
                technician=self.technician,
                spare_part=self.spare_part,
                customer_phone="12345678901",
            )

    def test_rejects_phone_with_letters(self):
        with self.assertRaisesRegex(frappe.ValidationError, "Number should be exactly 10"):
            make_job_card(
                technician=self.technician,
                spare_part=self.spare_part,
                customer_phone="98765ABCDE",
            )

    def test_accepts_10_digit_phone_number(self):
        doc = make_job_card(
            technician=self.technician,
            spare_part=self.spare_part,
            customer_phone="9876543210",
        )
        self.assertTrue(frappe.db.exists("Job Card", doc.name))

    def test_spare_part_selling_price_less_than_cost_raises(self):
        with self.assertRaises(frappe.ValidationError):
            make_spare_part(unit_cost=500.0, selling_price=300.0)

    def test_spare_part_selling_price_equal_to_cost_raises(self):
        with self.assertRaises(frappe.ValidationError):
            make_spare_part(unit_cost=500.0, selling_price=500.0)

    def test_spare_part_one_rupee_above_cost_passes(self):
        doc = make_spare_part(unit_cost=500.0, selling_price=501.0)
        self.assertTrue(frappe.db.exists("Spare Part", doc.name))

    def test_final_amount_computed_correctly(self):
        labour = flt(
            frappe.db.get_single_value("QuickFix Settings", "default_labour_charge")
        ) or 500.0
        part = make_spare_part(selling_price=700.0, stock_qty=10)
        doc = make_job_card(
            technician=self.technician,
            spare_part=part,
        )

        expected_parts_total = flt(part.unit_cost)
        expected_final = expected_parts_total + labour

        self.assertEqual(flt(doc.parts_total), expected_parts_total)
        self.assertEqual(flt(doc.final_amount), expected_final)

    def test_in_repair_requires_technician(self):
        with self.assertRaisesRegex(frappe.ValidationError, "Assign Technician First!!"):
            make_job_card(
                technician=self.technician,
                spare_part=self.spare_part,
                status="In Repair",
                assigned_technician="",
            )

    def test_in_repair_allows_assigned_technician(self):
        doc = make_job_card(
            technician=self.technician,
            spare_part=self.spare_part,
            status="In Repair",
        )
        self.assertTrue(frappe.db.exists("Job Card", doc.name))

    def test_draft_without_technician_passes(self):
        doc = make_job_card(
            technician=self.technician,
            spare_part=self.spare_part,
            status="Draft",
            assigned_technician="",
        )
        self.assertTrue(frappe.db.exists("Job Card", doc.name))

    def test_in_repair_allows_zero_estimated_cost_with_current_validation(self):
        doc = make_job_card(
            technician=self.technician,
            spare_part=self.spare_part,
            status="In Repair",
            estimated_cost=0,
        )
        self.assertTrue(frappe.db.exists("Job Card", doc.name))

    def test_parts_table_updates_row_totals_and_grand_total(self):
        part_a = make_spare_part(unit_cost=400.0, selling_price=600.0, stock_qty=10)
        part_b = make_spare_part(unit_cost=150.0, selling_price=200.0, stock_qty=10)

        doc = make_job_card(
            technician=self.technician,
            spare_part=part_a,
            parts_used=[
                {
                    "part": part_a.name,
                    "part_name": part_a.part_name,
                    "unit_price": part_a.unit_cost,
                    "quantity": 2,
                    "total_price": 0,
                },
                {
                    "part": part_b.name,
                    "part_name": part_b.part_name,
                    "unit_price": part_b.unit_cost,
                    "quantity": 3,
                    "total_price": 0,
                },
            ],
        )
        rows = {row.part: row for row in doc.parts_used}
        self.assertEqual(flt(rows[part_a.name].total_price), flt(part_a.unit_cost) * 2)
        self.assertEqual(flt(rows[part_b.name].total_price), flt(part_b.unit_cost) * 3)
        self.assertEqual(
            flt(doc.parts_total),
            (flt(part_a.unit_cost) * 2) + (flt(part_b.unit_cost) * 3),
        )


class TestJobCardSubmitCancel(FrappeTestCase):
    def setUp(self):
        self.device_type = make_device_type("Smartphone")
        self.technician = make_technician(specialization="Smartphone")
        self.spare_part = make_spare_part(stock_qty=10)

    def test_submit_requires_ready_for_delivery_status(self):
        doc = make_job_card(
            technician=self.technician,
            spare_part=self.spare_part,
            status="In Repair",
        )
        with self.assertRaisesRegex(frappe.ValidationError, "Ready for Delivery"):
            doc.submit()

    def test_submit_works_for_ready_for_delivery(self):
        doc = make_job_card(
            technician=self.technician,
            spare_part=self.spare_part,
            status="Ready for Delivery",
        )
        doc.submit()
        self.assertEqual(doc.docstatus, 1)

    def test_submit_fails_when_part_is_out_of_stock(self):
        zero_stock_part = make_spare_part(stock_qty=0)
        doc = make_job_card(
            technician=self.technician,
            spare_part=zero_stock_part,
            status="Ready for Delivery",
        )
        with self.assertRaisesRegex(frappe.ValidationError, "Insufficient Stock"):
            doc.submit()

    def test_submit_works_when_stock_is_available(self):
        part = make_spare_part(stock_qty=5)
        doc = make_job_card(
            technician=self.technician,
            spare_part=part,
            status="Ready for Delivery",
        )
        doc.submit()
        self.assertEqual(doc.docstatus, 1)

    def test_submit_reduces_stock_quantity(self):
        part = make_spare_part(stock_qty=10)
        stock_before = flt(frappe.db.get_value("Spare Part", part.name, "stock_qty"))

        doc = make_job_card(
            technician=self.technician,
            spare_part=part,
            status="Ready for Delivery",
            parts_used=[
                {
                    "part": part.name,
                    "part_name": part.part_name,
                    "unit_price": part.unit_cost,
                    "quantity": 3,
                    "total_price": part.unit_cost * 3,
                }
            ],
        )
        doc.submit()
        stock_after = flt(frappe.db.get_value("Spare Part", part.name, "stock_qty"))
        self.assertEqual(stock_after, stock_before - 3)
