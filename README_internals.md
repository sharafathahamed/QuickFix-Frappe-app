**1. In README.md explain in 4 sentences: what each config file is for, and what breaks if you accidentally put a secret in common_site_config.json**

site_config.json stores configuration that is specific to a single site,such as database details and site-level settings.  

common_site_config.json stores configuration shared across all sites in the same bench environment.  

hooks.py is an app configuration file that defines events, hooks, and loading behaviour.  

If a secret is placed in common_site_config.json, it becomes shared across every site, which can expose sensitive data and create security risks because all sites will be able to access that secret.

---

**2. In README.md: list the 4 processes bench start launches (web, worker, scheduler, socketio) and explain what happens to background jobs if the worker process crashes**

bench start runs four processes: 
  workers- processes background jobs, 
  scheduler- runs scheduled tasks, and 
  socketio- handles realtime updates. 

  If the worker process crashes, background jobs stop executing temporarily but remain in the queue, and they will continue once the worker restarts.

---

**3. When a browser hits /api/method/quickfix.api.get_job_summary - what Python function handles this request and how does Frappe find it?**

The Python function get_job_summary inside quickfix/api.py will be called. 

Frappe reads the dotted path quickfix.api.get_job_summary, imports the quickfix app, loads the api.py file, and calls the function. The function must be decorated with @frappe.whitelist() to allow API access.

---

**4. When a browser hits /api/resource/Job Card/JC-2024-0001 - what happens differently compared to /api/method/?**

/api/resource/ uses Frappe’s built-in REST API to directly access DocType records through the ORM and performs standard CRUD operations without calling a custom method.

---

**5. When a browser hits /track-job - which file/function handles it and why?**

This is handled by a file inside the app’s www/ folder, for example quickfix/www/track-job.py or track-job.html.

---

**6. With developer_mode: 1 - trigger a Python exception in one of your whitelisted methods. What does the browser receive? Set developer_mode: 0 - repeat. What does the browser receive now? Why is this important for production? Where do production errors go if they are hidden from the browser?**

With developer_mode: 1, when a Python exception occurs, the browser receives a detailed error message.  

With developer_mode: 0, the browser only receives a generic error message.

---

**7. In a whitelisted method, call frappe.get_doc("Job Card", name) WITHOUT ignore_permissions. Then log in as a QF Technician user who is NOT assigned to that job. What error is raised and at what layer does Frappe stop the request?**

The error raised will be a PermissionError or Not Permitted error because the user does not have access to that Job Card. Frappe stops the request at the permission checking layer inside the ORM before returning any document data, preventing unauthorized access.

---

**8. Run: frappe.db.sql("SHOW TABLES LIKE '%Job%'") and list what you see. Explain the tab prefix convention**

When I ran the query, I saw tables like tabScheduled Job Log and tabScheduled Job Type, which are database tables related to jobs. Frappe uses the tab prefix for all DocType tables so that the framework can easily identify and manage tables created from DocTypes.

---

**9. Run: frappe.db.sql("DESCRIBE `tabJob Card`", as_dict=True) and list 5 column names you recognise from your DocType fields**

When running the DESCRIBE command, I expect to see columns like name, customer_name, device_type, assigned_technician, and status because these are fields defined in the Job Card DocType.

---

**10. What are the three numeric values of docstatus and what state does each represent?**

In Frappe, docstatus has three numeric values: 0 = Draft, 1 = Submitted, and 2 = Cancelled.

---

**11. Can you call doc.save() on a submitted document? What about doc.submit() on a cancelled one? Test in bench console and explain why.**

Normally you cannot modify and save a submitted document because it is final, unless specific fields allow editing. You also cannot call doc.submit() on a cancelled document.

---

**12. Why would you see a "Document has been modified after you have opened it" error and how does Frappe prevent concurrent overwrites?**

This error happens when another user or process changes the document after you opened it but before you saved your changes. Frappe compares the last modified timestamp to prevent overwriting.

---

**13. The following snippet has TWO bugs related to document lifecycle. Identify both and write the corrected version**

The first bug is calling self.save() inside validate(), which causes recursion because validate() already runs during the save process.  
The second bug is modifying another document inside validate(), which creates side effects; updates like stock changes should be done in lifecycle methods such as on_submit() instead.

---

**14. When you append a row to Job Card.parts_used and save, what 4 columns does Frappe automatically set on the child table row?**

When a row is added to Job Card.parts_used and the document is saved, Frappe automatically sets the fields parent, parenttype, parentfield, and idx on the child row.

---

**15. What is the DB table name for the Part Usage Entry DocType?**

tabPart Usage Entry

---

**16. If you delete row at idx=2 and re-save, what happens to idx values of remaining rows?**

If the row with idx = 2 is deleted and the document is saved again, Frappe automatically reorders the remaining rows and updates the idx values sequentially so there are no gaps.

---

**17.Rename one of your test Technician records using Rename Document feature. Then check: does the assigned_technician field on linked Job Cards automatically update? Why or why not? What does "track changes" mean in this context?**

Yes, If I change in document it should affects its linked field aswell.
Because Frappe automatically update every link fields when ever the document is saved.
Only the document id is linked so it changes.

Track Changes is automatic logs which changed what and when, showing a "Version" history at the bottom of the document.

---

**18.Explain unique constraints: what is the difference between setting a field as "unique" in the DocType vs doing a frappe.db.exists() check in validate()?**

Setting a field as unique in the DocType creates a database to prevents duplicates.

In contrast, frappe.db.exists() in the validate() method is an application-level check that is more flexible for custom logic but can be bypassed by direct database writes.

---

**19.What is the issues in using frappe.get_all in a whitelisted method that is exposed to guests or low-privilege users. Explain it in the context of permission_query_conditions**

frappe.get_all()-- do not check for any permissions, it opens every door of every permissions and securities

**20.Call self.save() inside on_update and see to the issues of it and explain them in the same readme_internals. Correct the pattern and explain it.**

Calling self.save() inside on_update() creates a infinite save
Instead this we could just pass it or we can write frappe.db_set()

**21.why is doc_events safer than override_doctype_class for most use cases?**

doc_events is safer because it allows codee to write alongside instead replacing the whole code. It lets you work on different apps.

**22.**