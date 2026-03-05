**A**

**1. In README.md explain in 4 sentences: what each config file is for, and what breaks if you accidentally put a secret in common_site_config.json**

site_config.json stores configuration that is specific to a single site,such as database details and site-level settings.

common_site_config.json stores configuration shared across all sites in the same bench environment.

hooks.py is an app configuration file that defines events, hooks, and loading behaviour.

If a secret is placed in common_site_config.json, it becomes shared across every site, which can expose sensitive data and create security risks because all sites will be able to access that secret.


**2. In README.md: list the 4 processes bench start launches (web, worker, scheduler, socketio) and explain what happens to background jobs if the worker process crashes**

bench start runs four processes:
workers- processes background jobs,
scheduler- runs scheduled tasks, and
socketio- handles realtime updates.

If the worker process crashes, background jobs stop executing temporarily but remain in the queue, and they will continue once the worker restarts.


**B1**

**3. When a browser hits /api/method/quickfix.api.get_job_summary - what Python function handles this request and how does Frappe find it?**

The Python function get_job_summary inside quickfix/api.py will be called.

Frappe reads the dotted path quickfix.api.get_job_summary, imports the quickfix app, loads the api.py file, and calls the function. The function must be decorated with @frappe.whitelist() to allow API access.


**4. When a browser hits /api/resource/Job Card/JC-2024-0001 - what happens differently compared to /api/method/?**

/api/resource/ uses Frappe’s built-in REST API to directly access DocType records through the ORM and performs standard CRUD operations without calling a custom method.


**5. When a browser hits /track-job - which file/function handles it and why?**

This is handled by a file inside the app’s www/ folder, for example quickfix/www/track-job.py or track-job.html.


**6. With developer_mode: 1 - trigger a Python exception in one of your whitelisted methods. What does the browser receive? Set developer_mode: 0 - repeat. What does the browser receive now? Why is this important for production? Where do production errors go if they are hidden from the browser?**

With developer_mode: 1, when a Python exception occurs, the browser receives a detailed error message.

With developer_mode: 0, the browser only receives a generic error message.


**7. In a whitelisted method, call frappe.get_doc("Job Card", name) WITHOUT ignore_permissions. Then log in as a QF Technician user who is NOT assigned to that job. What error is raised and at what layer does Frappe stop the request?**

The error raised will be a PermissionError or Not Permitted error because the user does not have access to that Job Card. Frappe stops the request at the permission checking layer inside the ORM before returning any document data, preventing unauthorized access.


**B2**

**8. Run: frappe.db.sql("SHOW TABLES LIKE '%Job%'") and list what you see. Explain the tab prefix convention**

When I ran the query, I saw tables like tabScheduled Job Log and tabScheduled Job Type, which are database tables related to jobs. Frappe uses the tab prefix for all DocType tables so that the framework can easily identify and manage tables created from DocTypes.


**9. Run: frappe.db.sql("DESCRIBE `tabJob Card`", as_dict=True) and list 5 column names you recognise from your DocType fields**

When running the DESCRIBE command, I expect to see columns like name, customer_name, device_type, assigned_technician, and status because these are fields defined in the Job Card DocType.


**10. What are the three numeric values of docstatus and what state does each represent?**

In Frappe, docstatus has three numeric values: 0 = Draft, 1 = Submitted, and 2 = Cancelled.


**11. Can you call doc.save() on a submitted document? What about doc.submit() on a cancelled one? Test in bench console and explain why.**

Normally you cannot modify and save a submitted document because it is final, unless specific fields allow editing. You also cannot call doc.submit() on a cancelled document.


**12. Why would you see a "Document has been modified after you have opened it" error and how does Frappe prevent concurrent overwrites?**

This error happens when another user or process changes the document after you opened it but before you saved your changes. Frappe compares the last modified timestamp to prevent overwriting.


**13. The following snippet has TWO bugs related to document lifecycle. Identify both and write the corrected version**

The first bug is calling self.save() inside validate(), which causes recursion because validate() already runs during the save process.
The second bug is modifying another document inside validate(), which creates side effects; updates like stock changes should be done in lifecycle methods such as on_submit() instead.


**C1**

**14. When you append a row to Job Card.parts_used and save, what 4 columns does Frappe automatically set on the child table row?**

When a row is added to Job Card.parts_used and the document is saved, Frappe automatically sets the fields parent, parenttype, parentfield, and idx on the child row.


**15. What is the DB table name for the Part Usage Entry DocType?**

tabPart Usage Entry


**16. If you delete row at idx=2 and re-save, what happens to idx values of remaining rows?**

If the row with idx = 2 is deleted and the document is saved again, Frappe automatically reorders the remaining rows and updates the idx values sequentially so there are no gaps.


**C3**

**17.Rename one of your test Technician records using Rename Document feature. Then check: does the assigned_technician field on linked Job Cards automatically update? Why or why not? What does "track changes" mean in this context?**

Yes, If I change in document it should affects its linked field aswell.
Because Frappe automatically update every link fields when ever the document is saved.
Only the document id is linked so it changes.

Track Changes is automatic logs which changed what and when, showing a "Version" history at the bottom of the document.


**18.Explain unique constraints: what is the difference between setting a field as "unique" in the DocType vs doing a frappe.db.exists() check in validate()?**

Setting a field as unique in the DocType creates a database to prevents duplicates.

In contrast, frappe.db.exists() in the validate() method is an application-level check that is more flexible for custom logic but can be bypassed by direct database writes.


**D2**

**19.What is the issues in using frappe.get_all in a whitelisted method that is exposed to guests or low-privilege users. Explain it in the context of permission_query_conditions**

frappe.get_all()-- do not check for any permissions, it opens every door of every permissions and securities


**E1**

**20.Call self.save() inside on_update and see to the issues of it and explain them in the same readme_internals. Correct the pattern and explain it.**

Calling self.save() inside on_update() creates a infinite save
Instead this we could just pass it or we can write frappe.db_set()


**E3**

**21.why is doc_events safer than override_doctype_class for most use cases?**

doc_events is safer because it allows codee to write alongside instead replacing the whole code. It lets you work on different apps.


**F1**

**22.in what order do they run in job_card?**

First: It runs Main controller which is from validate method in Job_card.py
Second: It runs the doc_events in hooks.py


**23.What happens if both raise a frappe.ValidationError?**

When Main controller raises frappe.ValidationError error it immediately stops.


**F3**

**24. what is the difference? When would you use each?**

app_include_js: This is used as a global desk feature used for --help like feature
web_include_js:It is used as a styling website/portal feature like adding features to your homepage

**25. what DocType would use a tree view and why?**

doctype_js: This runs when user opens a specific 'jobcard' document. it calculates in realtime.
doctype_list_js: This script runs on the Job Card List View.
doctype_tree_js: Like for Accounts but not used in job cards i think.

**26.Explain what bench build --app quickfix does and why assets need cache-busting after JS changes**

Browsers cache-save JS files to speed up loading. It collects all your JS and CSS files and combines them into single files for faster loading.

**27.what is the difference between a Jinja context available in Print Formats vs one available in Web Pages? Are they the same?**

No, They aren't same,
  Print Format: Used for PDF Format.
  Web Pages: Used for Web pages(Public).

**28.Explain the difference between override_whitelisted_methods (hook-based reversible, explicit) vs monkey patching(import-time, brittle, invisible). When would you use each?**

override_whitelisted_methods is the way to change API functions using a clear list in hooks.py, making it safe and easy to undo. Monkey patching is a "secret" code hack that overwrites functions everywhere at once, which can easily break other parts of the system. 

Use the hook for standard API updates to keep your code clean, and only use monkey patching as a last resort for core internal logic.

**F4**

**What happens if TWO apps both register override_whitelisted_methods for the same method? Write the answer.**

If two separate apps register an override_whitelisted_methods for the exact same function, the app that is loaded last by the Frappe framework will win and its method will be the one executed.

The load order is determined by the sequence of apps listed in your site's apps.txt or site_config.json.

**Explain about the Signature mismatch and not having exactly the same arguments as the original and in what case would you get a TypeError.**

Signature mismatch happens when your custom function’s arguments don't exactly match the original’s, leading to a TypeError if the system sends a parameter your code doesn't recognize. To prevent this, always include **kwargs to safely catch any extra arguments and ensure long-term compatibility.

**F5**

**Explain fieldname collision risk: what happens if your Custom Field has the same fieldname as a field added by a future Frappe update?**

If you create a Custom Field on Job Card with fieldname priority, and Frappe later adds its own priority field in a core update, bench migrate will crash with a duplicate column error in MariaDB.
Your existing data in priority may get overwritten by Frappe's version, and any core logic Frappe built around its priority field will conflict with your custom behavior.
Always prefix your custom fields with your app name — use qf_priority instead of priority — so there's zero chance of collision with future Frappe updates.

**Explain patching order: if Patch 1 creates a Custom Field and Patch 2 reads it, why must they be separate entries in patches.txt and never merged?**

bench migrate runs patches one by one in order, and commits each one before moving to the next.
If you merge Patch 1 (create field) and Patch 2 (read field) into one function, the column doesn't exist yet when the read runs — crash.
Keep them separate so Patch 1 fully finishes and commits first, then Patch 2 runs safely knowing the column is already there.

**G1**

**What is the _qf_patched guard for? What breaks without it?**

The guard prevents the patch from being applied more than once. Without it, every time apply_all() is called, it wraps get_url inside another wrapper — so after 3 calls your URL becomes "cdn.cdn.cdn.http://localhost" instead of "cdn.http://localhost".

**2. Why isolate in monkey_patches.py instead of __init__.py?**

__init__.py runs every single time Python imports your app - during bench migrate, tests, CLI commands, worker startup — even when you don't want patches applied. monkey_patches.py only runs when you explicitly call apply_all(), giving you full control over when patches are applied.

**What is the correct escalation path: try doc_events first - then override_doctype_class - then override_whitelisted_methods - then monkey patch. Why is this the order?**

doc_events → safest, always try this first
override_doctype_class → when you need more control
override_whitelisted_methods → when you need to replace an API function
monkey patch → last resort, dangerous, avoid if possible

**Why frappe.call inside validate (before_save) doesn't work**

frappe.call is ASYNC — it sends HTTP request and waits for response.
But validate/before_save is SYNC — Frappe doesn't wait for async calls.

So by the time frappe.call gets response from server,
form is already saved and validate has finished.
Your async result arrives too late — it's ignored.

Rule: Never use frappe.call inside before_save/validate client event.
Use frappe.db.get_value or frm.set_query instead — they work synchronously.

**Use onload or refresh for async data fetches**

onload  → use for one-time async setup (realtime listeners, initial data fetch)
refresh → use for UI updates that depend on current doc state

Both fire AFTER form is ready — so async calls work safely here.
frappe.call inside refresh is fine because user is just viewing,
not in the middle of a save operation.

**H3**

**What is a Tree DocType?**

A Tree DocType is a DocType that has parent-child hierarchy — records can contain other records like a folder structure. Example: Account in ERPNext has parent accounts, Employee has reporting manager hierarchy.

**What is doctype_tree_js used for?**

It's a JS file that customizes the tree view of a DocType — adding buttons, actions, or custom behavior when navigating the tree.
Example where it applies:
Chart of Accounts → Account DocType uses tree view
because accounts have parent-child relationships
(Assets → Current Assets → Cash)

**When would you use tree view?**

Use tree view when:
- Records have parent-child relationships
- Users need to navigate hierarchy visually
- Example: Departments, Account heads, Item Groups

**Client Script DocType vs Shipped JS:**

Client Script DocType is stored in the database, so a consultant can change it directly from the browser without any deployment — useful for quick site-specific tweaks like hiding a field for a specific customer. 

Shipped JS lives in your app code, is version controlled in git, and needs bench build — better for permanent features since changes are tracked and reviewed. Risk of Client Script: anyone with System Manager role can accidentally modify it, and it's not in git so changes can't be rolled back.

**JS Field Hiding is NOT Security:**

frm.set_df_property("customer_phone", "hidden", 1) only hides the field visually in the browser — the data is still sent from server to browser. Anyone can open console and run frappe.call({method: "frappe.client.get", args: {doctype: "Job Card", name: cur_frm.doc.name}}) and see customer_phone in the response. Real security must be enforced server-side using has_permission hook or stripping sensitive fields in whitelisted methods — never trust the client!