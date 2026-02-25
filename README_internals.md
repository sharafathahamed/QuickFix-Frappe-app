<!-- Question: -->
1.In README.md explain in 4 sentences: what each config file is for, and what breaks
if you accidentally put a secret in common_site_config.json
<!-- Answer: -->
  site_config.json stores configuration that is specific to a single site, such as database details and site-level settings.
  
common_site_config.json stores global configuration shared across all sites in the same bench environment.

hooks.py is an app configuration file that defines how the app integrates with Frappe, including events, hooks, and loading behaviour.

If a secret is placed in common_site_config.json, it becomes shared across every site, which can expose sensitive data and create security risks because all sites will be able to access that secret.

<!-- Question: -->
2.In README.md: list the 4 processes bench start launches (web, worker, scheduler,
socketio) and explain what happens to background jobs if the worker process
crashes.
<!-- Answer: -->
  bench start runs four processes: 
      web(handles HTTP requests),
      worker (processes background jobs),   
      scheduler(runs scheduled tasks), 
      and socketio (handles realtime updates).If the worker process crashes, background jobs stop executing temporarily but remain in the queue, and they will continue once the worker restarts.

<!-- Question: -->
3.When a browser hits /api/method/quickfix.api.get_job_summary - what Python
function handles this request and how does Frappe find it?
<!-- Answer: -->
  The Python function get_job_summary inside quickfix/api.py handles this request. Frappe reads the dotted path quickfix.api.get_job_summary, imports the quickfix app, loads the api.py file, and calls the function. The function must be decorated with @frappe.whitelist() to allow API access.

<!-- Question: -->
4.When a browser hits /api/resource/Job Card/JC-2024-0001 - what happens
differently compared to /api/method/?
<!-- Answers -->
  /api/resource/ uses Frappe’s built-in REST API to directly access DocType records through the ORM. while /api/resource/ performs standard CRUD operations by calling a function on documents.

<!-- Question: -->
5.When a browser hits /track-job - which file/function handles it and why?
<!-- Answer: -->
  This is handled by a file inside the app’s www/ folder, for example quickfix/www/track-job.py or track-job.html. 

<!-- Question: -->
6.With developer_mode: 1 - trigger a Python exception in one of your whitelisted
methods. What does the browser receive?
Set developer_mode: 0 - repeat. What does the browser receive now? Why is this
important for production?
Where do production errors go if they are hidden from the browser?
<!-- Answers: -->
  With 
  developer_mode: 1, when a Python exception occurs, the browser receives detailed error message helps during development and debugging.
  
With developer_mode: 0, the browser only receives a generic error message.
Hidden production errors are stored in server log files and the Error Log DocType for later debugging.

<!-- Questions: -->
7.In a whitelisted method, call frappe.get_doc("Job Card", name) WITHOUT
ignore_permissions. Then log in as a QF Technician user who is NOT assigned to
that job. What error is raised and at what layer does Frappe stop the request?
<!-- Answers: -->
  The error raised will be a PermissionError or Not Permitted error because the user does not have access to that Job Card.
  
Frappe stops the request at the permission checking layer inside the ORM before returning any document data, preventing unauthorized access.

<!-- Question: -->
8.Run: frappe.db.sql("SHOW TABLES LIKE '%Job%'") and list what you see. Explain
the tab prefix convention.
<!-- Answer: -->
  When I ran the query, I saw tables like tabScheduled Job Log and tabScheduled Job Type, which are database tables related to jobs. Frappe uses the tab prefix for all DocType tables so that the framework can easily identify and manage tables created from DocTypes.

<!-- Question: -->
9.Run: frappe.db.sql("DESCRIBE `tabJob Card`", as_dict=True) and list 5 column
names you recognise from your DocType fields.
<!-- Answer -->
  When running the DESCRIBE command, I expect to see columns like name, customer_name, device_type, assigned_technician, and status because these are fields defined in the Job Card DocType.

<!-- Question: -->
10.What are the three numeric values of docstatus and what state does each represent?
<!-- Answer: -->
  In Frappe, docstatus has three numeric values: 0 = Draft, 1 = Submitted, and 2 = Cancelled.
<!-- Question: -->
11.Can you call doc.save() on a submitted document? What about doc.submit() on a cancelled one? Test in bench console and explain why.
<!-- Answer: -->
  Normally you cannot modify and save a submitted document because it is final, unless specific fields allow editing.
  
You also cannot call doc.submit() on a cancelled document

<!-- Question: -->
12.Why would you see a "Document has been modified after you have opened it" error and how does Frappe prevent concurrent overwrites?
<!-- Answer: -->
  This error happens when another user or process changes the document after you opened it but before you saved your changes.Frappe compares the last modified timestamp
<!-- Part E -->
13.The following snippet has TWO bugs related to document lifecycle. Identify both and write
the corrected version:
def validate(self):
self.total = sum(r.amount for r in self.items)
self.save()
other = frappe.get_doc("Spare Part", self.part)
other.stock_qty -= self.qty
other.save()
<!-- Answer -->
  -The first bug is calling self.save() inside validate(), which causes recursion because validate() already runs during the save process.

  -The second bug is modifying another document inside validate(), which creates side effects; updates like stock changes should be done in lifecycle methods such as on_submit() instead.

<!-- Question: -->
14.When you append a row to Job Card.parts_used and save, what 4 columns does
Frappe automatically set on the child table row?
<!-- Answers: -->
    When a row is added to Job Card.parts_used and the document is saved, Frappe automatically sets the fields parent, parenttype, parentfield, and idx on the child row. These fields link the child record to its parent document and maintain the correct order of rows.

<!-- Question: -->
What is the DB table name for the Part Usage Entry DocType?
<!-- Answer: -->
Ans: `tabPart Usage Entry`

<!-- Question: -->
If you delete row at idx=2 and re-save, what happens to idx values of remaining rows?
<!-- Answer: -->
If the row with idx = 2 is deleted and the document is saved again, Frappe automatically reorders the remaining rows and updates the idx values sequentially, so there are no gaps in the row numbering.
