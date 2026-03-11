import frappe
from frappe import _
from frappe.utils import flt, date_diff

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary

def get_columns(filters):
    columns = [
        {
            "label":"Technician",
            "fieldname":"technician",
            "fieldtype":"Link",
            "options":"Technician",
            "width":150
        },
        {
            "label":"Total Jobs",
            "fieldname":"total_jobs",
            "fieldtype":"Int",
            "width":100
        },
        {
            "label":"Completed",
            "fieldname":"completed",
            "fieldtype":"Int",
            "width":100
        },
        {
            "label":"Avg Turnaround Days",
            "fieldname":"avg_turnaround",
            "fieldtype":"Float",
            "width":150
        },
        {
            "label":"Revenue",
            "fieldname":"revenue",
            "fieldtype":"Currency",
            "width":120
        },
        {
            "label":"Completion Rate %",
            "fieldname":"completion_rate",
            "fieldtype":"Percentage",
            "width":130
        },
    ]
    for dt in frappe.get_all("Device Type",fields=["name"]):
        columns.append({
            "label":dt.name,
            "fieldname":dt.name.lower().replace(" ","_"),
            "fieldtype":"Int",
            "width":100
        })
    return columns

def get_data(filters):
    f = {}
    if filters.get("from_date"):
        f["creation"] = [">=",filters.get("from_date")]
    if filters.get("to_date"):
        f["creation"] = ["<=",filters.get("to_date")]
    if filters.get("technician"):
        f["assigned_technician"] = filters.get("technician")

    job_cards = frappe.get_list(
        "Job Card",
        filters=f,
        fields=[
            "name","assigned_technician","status",
            "final_amount","creation","delivery_date",
            "device_type"
        ]
    )

    tech_data = {}
    for jc in job_cards:
        tech = jc.assigned_technician or "Unassigned"
        if tech not in tech_data:
            tech_data[tech] = {
                "technician":tech,
                "total_jobs":0,
                "completed":0,
                "revenue":0,
                "turnaround_days":[],
                "device_types":{}
            }
        tech_data[tech]["total_jobs"] += 1
        if jc.status == "Delivered":
            tech_data[tech]["completed"] += 1
            tech_data[tech]["revenue"] += flt(jc.final_amount)
            if jc.delivery_date and jc.creation:
                days = date_diff(jc.delivery_date,jc.creation)
                tech_data[tech]["turnaround_days"].append(days)
        dt = jc.device_type or "Unknown"
        tech_data[tech]["device_types"][dt] = tech_data[tech]["device_types"].get(dt,0) + 1

    data = []
    device_types = [dt.name for dt in frappe.get_all("Device Type",fields=["name"])]

    for tech,d in tech_data.items():
        total = d["total_jobs"]
        completed = d["completed"]
        completion_rate = (completed/total*100) if total else 0
        avg_turnaround = (
            sum(d["turnaround_days"])/len(d["turnaround_days"])
            if d["turnaround_days"] else 0
        )
        row = {
            "technician":tech,
            "total_jobs":total,
            "completed":completed,
            "avg_turnaround":round(avg_turnaround,1),
            "revenue":d["revenue"],
            "completion_rate":round(completion_rate,1)
        }
        for dt in device_types:
            row[dt.lower().replace(" ","_")] = d["device_types"].get(dt,0)
        data.append(row)

    return data

def get_chart(data):
    if not data:
        return None
    return {
        "data":{
            "labels":[d["technician"] for d in data],
            "datasets":[
                {
                    "name":"Total Jobs",
                    "values":[d["total_jobs"] for d in data]
                },
                {
                    "name":"Completed",
                    "values":[d["completed"] for d in data]
                }
            ]
        },
        "type":"bar",
        "title":"Technician Performance"
    }

def get_summary(data):
    if not data:
        return []
    total_jobs = sum(d["total_jobs"] for d in data)
    total_revenue = sum(d["revenue"] for d in data)
    best_tech = max(data,key=lambda x:x["completion_rate"])
    return [{
            "label":"Total Jobs",
            "value":total_jobs,
            "datatype":"Int"
        },{
            "label":"Total Revenue",
            "value":total_revenue,
            "datatype":"Currency"
        },{
            "label":"Best Technician",
            "value":best_tech["technician"],
            "datatype":"Data"
        }
    ]