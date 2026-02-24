import frappe
from frappe.query_builder import DocType
from frappe.utils import now,add_days

@frappe.whitelist()
def get_overdue_jobs():
    JobC=DocType("Job Card")
    result=(
        frappe.qb.from_(JobC).select(
            JobC.name,
            JobC.customer_name,
            JobC.assigned_technician,
            JobC.creation
        ).where((JobC.status.isin(["Pending Diagnosis","In Repair"]))&
                (JobC.creation<add_days(now(),-7))
        ).orderby(JobC.creation).run(as_dict=True)
    )
    return result
@frappe.whitelist()
def transfer_job(from_tech, to_tech):
    try:
        frappe.db.sql("""
                      UPDATE `tabJob =%s
                      WHERE asiigned_technician = %s
                      AND status NOT IN ('Delivered','Cancelled')
                      """,(to_tech,from_tech))
        frappe.db.commit()
        return "Transfered succesful"

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(),"Transfer Job Error")
        raise