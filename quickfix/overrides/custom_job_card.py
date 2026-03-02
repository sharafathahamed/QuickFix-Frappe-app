import frappe
from quickfix.service_center.doctype.job_card.job_card import JobCard

class CustomJobCard(JobCard):
    def validate(self):
        super().validate()
        self._check_urgency_unassigned()
        
    def _check_urgency_unassigned(self):
        if self.priority=="Urgent" and not self.assigned_technician:
            settings=frappe.get_single("QuickFix Settings")
            frappe.enqueue(
                "quickfix.utils.send_urgent_alert",
                job_card=self.name,
                manager=settings.manager_email
            )

    #MRO - Method Resolution Order is a hierarchy of classes.

    #super() keyword is non negotiable because without that we can use the attributes of parent class.