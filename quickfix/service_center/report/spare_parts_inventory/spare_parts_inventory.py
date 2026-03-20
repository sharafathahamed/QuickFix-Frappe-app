# Copyright (c) 2026, Sharafath Ahamed and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_column()
    data = get_data()
    summary = get_summary(data)
    data = add_total_row(data)
    return columns, data, None, None, summary

def get_column():
    return [
        {
            "label": "Part Name",
            "fieldname": "part_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Part Code",
            "fieldname": "part_name",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Device Type",
            "fieldname": "compatible_device_type",
            "fieldtype": "Link",
            "options": "Device Type",
            "width": 120
        },
        {
            "label": "Stock Qty",
            "fieldname": "stock_qty",
            "fieldtype": "Float",
            "width": 100
        }, {
            "label": "Reorder Level",
            "fieldname": "reorder_level",
            "fieldtype": "Float",
            "width": 110
        },
        {
            "label": "Unit Cost",
            "fieldname": "unit_cost",
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "label": "Selling Price",
            "fieldname": "selling_price",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Margin %",
            "fieldname": "margin",
            "fieldtype": "Percent",
            "width": 100
        },
    ]
def get_data():
    parts = frappe.get_all(
        "Spare Part",
        filters={"is_active": 1},
        fields=[
            "part_name", "part_code", "compatible_device_type",
            "stock_qty", "reorder_level", "unit_cost", "selling_price"
        ]
    )
    data = []
    for p in parts:
        margin = 0
        if p.selling_price:
            margin = ((flt(p.selling_price) - flt(p.unit_cost)) / flt(p.selling_price)) * 100
        data.append({
            "part_name": p.part_name,
            "part_code": p.part_code,
            "compatible_device_type": p.compatible_device_type,
            "stock_qty": p.stock_qty,
            "reorder_level": p.reorder_level,
            "unit_cost": p.unit_cost,
            "selling_price": p.selling_price,
            "margin": round(margin, 2)
        })
    return data

def get_summary(data):
    total_parts = len(data)
    below_reorder = len([p for p in data if flt(p["stock_qty"]) <= flt(p["reorder_level"])])
    total_inventory_value = sum(flt(p["stock_qty"]) * flt(p["unit_cost"]) for p in data)
    return [
        {
            "label": "Total Parts",
            "value": total_parts,
            "datatype": "Int"
        },
        {
            "label": "Below Reorder",
            "value": below_reorder,
            "datatype": "Int",
            "indicator": "red" if below_reorder > 0 else "green"
        },
        {
            "label": "Total Inventory Value",
            "value": total_inventory_value,
            "datatype": "Currency"
        }
    ]

def add_total_row(data):
    total_stock = sum(flt(p["stock_qty"]) for p in data)
    total_value = sum(flt(p["stock_qty"]) * flt(p["unit_cost"]) for p in data)
    data.append({
        "part_name": "<b>Total</b>",
        "part_code": "",
        "compatible_device_type": "",
        "stock_qty": total_stock,
        "reorder_level": "",
        "unit_cost": total_value,
        "selling_price": "",
        "margin": ""
    })
    return data
