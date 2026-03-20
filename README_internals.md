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

frappe.get_all() bypasses permission checks and returns records directly from the database.  

If this is used inside a whitelisted API exposed to guests or low-privilege users, it can leak data because permission_query_conditions are not applied.  

This means users may receive records they are not authorized to see, so frappe.get_list() should be used instead because it respects permission rules and record-level filtering.


**E1**

**20.Call self.save() inside on_update and see to the issues of it and explain them in the same readme_internals. Correct the pattern and explain it.**

Calling self.save() inside on_update() causes infinite recursion because on_update() is triggered during the save process itself.  

When save() runs again inside on_update(), it triggers on_update() repeatedly, eventually causing a recursion error or server crash.

Correct pattern is to update fields using frappe.db.set_value() or modify fields directly without calling save() again.


**E3**

**21.why is doc_events safer than override_doctype_class for most use cases?**

doc_events is safer because it allows developers to attach logic to document lifecycle events without replacing the original controller class.  

This avoids breaking core functionality and reduces upgrade conflicts when the base DocType controller changes in future framework updates.


**F1**

**22.in what order do they run in job_card?**

First the DocType controller method (for example validate() inside job_card.py) runs.  

After that, handlers registered in hooks.py under doc_events are executed.


**23.What happens if both raise a frappe.ValidationError?**

If both handlers raise frappe.ValidationError, the first error raised stops execution and the request fails immediately.  

The document will not be saved because validation errors halt the lifecycle process.


**F3**

**24. what is the difference? When would you use each?**

app_include_js loads JavaScript files globally for the Desk interface used by logged-in users.

web_include_js loads JavaScript files only for website or portal pages accessible through the web interface.

app_include_js is used for Desk UI customizations while web_include_js is used for public web pages or portals.


**25. what DocType would use a tree view and why?**

doctype_js runs when a specific document form is opened.

doctype_list_js runs when the list view of that DocType is displayed.

doctype_tree_js is used when the DocType has a hierarchical parent-child structure such as Account, Item Group, or Department where records form a tree hierarchy.


**26.Explain what bench build --app quickfix does and why assets need cache-busting after JS changes**

bench build --app quickfix compiles and bundles the app’s JavaScript and CSS assets.

Browsers cache these files for performance, so after JS changes cache-busting ensures the browser loads the new version instead of using the old cached file.


**27.what is the difference between a Jinja context available in Print Formats vs one available in Web Pages? Are they the same?**
No, they are not the same.

Print Formats receive the document object (doc) and context related to printing such as format_value and printing utilities.

Web Pages receive context data prepared by the get_context() function inside the www Python file and may include website-specific variables.


**28.Explain the difference between override_whitelisted_methods (hook-based reversible, explicit) vs monkey patching(import-time, brittle, invisible). When would you use each?**
override_whitelisted_methods replaces an API method using hooks.py in a structured and reversible way.

Monkey patching directly replaces a function at runtime using Python imports which is fragile and harder to track.

override_whitelisted_methods should be used when replacing API behavior, while monkey patching should only be used as a last resort when no official hook exists.


**F4**

**What happens if TWO apps both register override_whitelisted_methods for the same method? Write the answer.**
If two apps override the same method, the method from the app loaded last will take precedence.

The load order depends on the order of apps defined in the site configuration.


**Explain about the Signature mismatch and not having exactly the same arguments as the original and in what case would you get a TypeError.**
Signature mismatch occurs when the custom override method does not accept the same arguments as the original function.

If Frappe calls the method with arguments the override does not expect, Python raises a TypeError because the parameters do not match.


**F5**
**Explain fieldname collision risk: what happens if your Custom Field has the same fieldname as a field added by a future Frappe update?**
If a Custom Field has the same fieldname as a new field added by a future Frappe update, database migration may fail with a duplicate column error.

This can also cause conflicts between custom logic and core framework logic.


**Explain patching order: if Patch 1 creates a Custom Field and Patch 2 reads it, why must they be separate entries in patches.txt and never merged?**
Patches run sequentially during bench migrate.

If both operations are merged into one patch, the read operation may execute before the field is created.

Keeping them separate ensures Patch 1 completes first and Patch 2 runs after the field exists.


**G1**
**What is the _qf_patched guard for? What breaks without it?**
The _qf_patched guard ensures the monkey patch is applied only once.

Without this guard the function could be patched multiple times which may cause duplicated logic or incorrect behaviour.


**2. Why isolate in monkey_patches.py instead of __init__.py?**
__init__.py runs every time the app is imported.

Isolating patches in monkey_patches.py ensures patches are applied only when explicitly called and not during every import.


**What is the correct escalation path: try doc_events first - then override_doctype_class - then override_whitelisted_methods - then monkey patch. Why is this the order?**
doc_events is safest because it adds behaviour without replacing core logic.

override_doctype_class is used when deeper controller customization is needed.

override_whitelisted_methods replaces API methods in a controlled way.

monkey patching is the last resort because it modifies framework behaviour directly.


**Why frappe.call inside validate (before_save) doesn't work**
frappe.call is asynchronous and sends a request to the server.

validate and before_save events execute synchronously during the save process.

Because of this the async call does not complete before validation finishes, making the result unusable during validation.


**Use onload or refresh for async data fetches**
onload is used for initial setup tasks such as loading data when the form opens.

refresh is used for updating UI behaviour whenever the form is refreshed.

Async calls such as frappe.call work safely in these events because they occur after the document is loaded.


**H3**

**What is a Tree DocType?**

A Tree DocType represents hierarchical data where records have parent-child relationships.
Examples include Account or Item Group where records form a nested structure.


**What is doctype_tree_js used for?**
doctype_tree_js is used to customize behaviour of the tree view interface such as adding buttons or custom actions.


**When would you use tree view?**
Tree view is used when records naturally form hierarchical structures such as departments, account heads, or category groups.

**Client Script DocType vs Shipped JS:**
Client Script DocType is stored in the database, so a consultant can change it directly from the browser without any deployment — useful for quick site-specific tweaks like hiding a field for a specific customer. 

Shipped JS lives in your app code, is version controlled in git, and needs bench build — better for permanent features since changes are tracked and reviewed. Risk of Client Script: anyone with System Manager role can accidentally modify it, and it's not in git so changes can't be rolled back.

**JS Field Hiding is NOT Security:**
frm.set_df_property("customer_phone", "hidden", 1) only hides the field visually in the browser — the data is still sent from server to browser. Anyone can open console and run frappe.call({method: "frappe.client.get", args: {doctype: "Job Card", name: cur_frm.doc.name}}) and see customer_phone in the response. Real security must be enforced server-side using has_permission hook or stripping sensitive fields in whitelisted methods — never trust the client!

**Demonstrate and explain the issues and solutions with respect to f-string SQL and the parameterized pattern.**

f-string SQL is dangerous because user input goes directly into the query string — an attacker can inject malicious SQL and access or destroy your entire database. For example, f"WHERE name = '{user_input}'" — if user types ' OR '1'='1, the query returns all records. 

Parameterized queries like WHERE name = %(name)s pass values separately so MariaDB treats them as data, never as SQL code — always use this pattern.

**I4**

**Prepared Report vs Real-time Report:**
- Use Prepared Report when data is large and 
  report takes > 10 seconds to run
- Use Real-time when data must be up to date

**Staleness tradeoff:**
- Prepared Report shows data from LAST RUN
- If new Job Cards added after last run,
  they won't appear until next preparation
- User may see outdated data without knowing it

**Caching risk:**
- If underlying data changes between preparations, user sees OLD data
- Example: Job Card delivered at 10am, report prepared at 9am → revenue wrong until next run

**When is Report Builder appropriate?**

Use Report Builder when you need a simple list-style report with basic filters and no calculations — a consultant or non-developer can build it in minutes without writing any code, like "Customer History" showing all Job Cards per customer.

**When must you use Script Report?**

Use Script Report when you need dynamic columns, complex calculations like margin% or avg turnaround, custom charts, permission-based row filtering, or report_summary cards — anything beyond a simple list requires Python code.

**Report Builder in production = mistake scenario:**

A manager builds "Revenue by Technician" using Report Builder — it works fine for 100 records but when Job Cards grow to 50,000, it fetches all records with no SQL grouping or indexing, crashes the server under load, and should have been a Script Report from the start.

## J1 - Jinja Template Patterns

### Putting frappe.get_all() directly in Jinja template
This is a bad pattern because the template layer should only handle presentation, not data fetching.
Calling frappe.get_all() inside a Jinja template makes the template slow, hard to debug, and mixes
business logic with presentation — if the query fails, the entire print render crashes with an
unhelpful template error.

### Pre-compute in before_print() and attach to self
This is the correct pattern — compute heavy data in before_print(), attach it to the doc object
(e.g. self.precomputed_field = some_value), then reference it in the template as doc.precomputed_field.
This keeps templates clean, makes logic testable in Python, and errors surface with proper tracebacks
rather than cryptic Jinja errors.

## J2 - Raw Print vs HTML to PDF

### Difference between Raw Printing and HTML-PDF rendering
Raw printing sends ESC/POS binary commands directly to a thermal printer without involving a browser or PDF renderer, while Frappe's HTML-PDF rendering uses wkhtmltopdf or WeasyPrint to convert a Jinja HTML template into a downloadable PDF file.

### 3 CSS properties that work in browser but fail in WeasyPrint
Three CSS properties that work in a browser but fail in WeasyPrint are display:flex (flexbox layout is unsupported), position:fixed (fixed positioning is ignored), and box-shadow (shadow effects are not rendered).

### format_value() usage
The format_value() function is essential in print templates because without it a Currency field like 1700.0 renders as a raw float "1700.0", but with format_value() it correctly renders as "₹ 1,700.00" with the currency symbol, thousand separators, and two decimal places as expected in a customer-facing document.

## K1 - Background Jobs

### Task A - Queue Names
Frappe has three RQ queue names: 
"short" is for quick jobs like sending a single email that must 
not wait behind heavy tasks, 
"default" is for normal jobs like processing a form submission, and 
"long" is for heavy jobs like generating reports that need extended time with timeout=600

### Find the failure in Setup - Error Log: 
Go to Awesome Bar → Error Log, and you will see the failed job entry with the full traceback, method name, and timestamp of when it failed.

### In RQ Failed Jobs: 
Access /rq-dashboard on your site URL, click "Failed" tab, and you will see  the failed job listed there with its exception details and the exact moment it was moved to the failed queue.

### Retry behavior: 
Frappe does not retry failed background jobs by default — a job that raises an unhandled exception fails immediately with 0 automatic retries and stays in the RQ failed queue until manually requeued by an administrator.

### How to disable the scheduler for a specific site:
Run `bench --site quickfix-dev.localhost scheduler disable`
to disable the scheduler for that site.
We'd do this in dev sie because to prevent background jobs from firing during active development.

### What happens to scheduled jobs that were queued while the worker was down:

Scheduled jobs that were queued while the worker was down will still run when the worker comes back up — because the jobs were already pushed into the Redis queue before the worker crashed, and Redis persists the queue, so when the worker restarts it picks up and processes all the pending jobs that were waiting in the queue.

### N+1 Query

job_cards = frappe.get_all(
    "Job Card",
    fields=["name", "assigned_technician"]
)
tech_ids = [jc.assigned_technician for jc in job_cards]
technicians = frappe.get_all(
    "Technician",
    filters={"name": ["in", tech_ids]},
    fields=["name", "technician_name", "phone"]
)
tech_map = {t.name: t for t in technicians}
for jc in job_cards:
    tech = tech_map.get(jc.assigned_technician)

    if tech:
        print(tech.technician_name, tech.phone)

## K3 - Performance Engineering

### Task A - N+1 Query
The N+1 problem occurs when you call frappe.get_doc() inside a loop — for 100 Job Cards that means 101 database queries (1 to get the list + 1 per row to fetch the technician). The fix is to fetch all technician IDs first, then use a single frappe.get_all() with an IN filter to get all technicians in one query, then map them in Python using a dict.

### Task B - Bulk Operations
frappe.db.sql() with a single UPDATE statement is dramatically faster than a Python loop with individual doc.save() calls because it executes one database operation instead of N operations with N round trips. frappe.db.bulk_insert() is similarly faster than individual .insert() calls because it batches all rows into a single INSERT statement.

### Task C - Indexing
The existing indexes on tabJob Card before adding search_index were: PRIMARY on name, amended_from, modified, and status_index on status. After adding search_index:1 to assigned_technician in the DocType JSON and running bench migrate, assigned_technician_index was added. You would NOT add a search index to every field because each index adds overhead to INSERT, UPDATE, and DELETE operations — over-indexing a write-heavy table like Job Card would slow down job creation and status updates significantly.

### Task D - Report Performance
To enable SQL logging add "logging": 1 to site_config.json and check ~/frappe-bench/logs/web.log for query output. The slowest query in the Technician Performance Report is typically the GROUP BY aggregation across Job Cards — adding a composite index on assigned_technician, status, and delivery_date reduces query time by allowing MySQL to avoid a full table scan.

## L1 - Task A - Resource API

### GET /api/resource/Job Card
Request: GET http://quickfix-dev.localhost:8000/api/resource/Job Card with session cookie auth.
Response: 200 OK — returns a list of Job Card names like JC-2026-00037, JC-2026-00038, JC-2026-00039.

### GET /api/resource/Job Card/JC-2026-00038
Request: GET http://quickfix-dev.localhost:8000/api/resource/Job Card/JC-2026-00038 with session cookie auth.
Response: 200 OK — returns full Job Card document including customer_name, device_type, parts_used child table, final_amount, and status.

### POST /api/resource/Spare Part
Request: POST http://quickfix-dev.localhost:8000/api/resource/Spare Part with body {"part_name":"Test Part","part_code":"TESTAPI002","unit_cost":100,"selling_price":150}.
Response: 200 OK — returns the created Spare Part document with auto-generated name TESTAPI002-0001 and all fields populated.

### PUT /api/resource/Spare Part/TESTAPI002-0001
Request: PUT http://quickfix-dev.localhost:8000/api/resource/Spare Part/TESTAPI002-0001 with body {"selling_price":200}.
Response: 200 OK — returns the updated document with selling_price changed from 150 to 200 and modified timestamp updated.

### DELETE /api/resource/Spare Part/TESTAPI002-0001
Request: DELETE http://quickfix-dev.localhost:8000/api/resource/Spare Part/TESTAPI002-0001 with session cookie auth.
Response: 200 OK — returns {"data":"ok"} confirming the record was permanently deleted from the database.

### Session Cookie Auth vs Token Auth

Session cookie auth works by logging in once via /api/method/login, after which the server creates a session and the browser automatically attaches the cookie to every subsequent request without the user sending credentials again — this is appropriate for browser-based usage where a human is interactively logged in to the Frappe desk.

Token auth sends Authorization: token api_key:api_secret in every single request header with no session or cookie involved — this is appropriate for server-to-server integrations, CI pipelines, and external apps where there is no browser and the client must authenticate programmatically on every call.

### Task - D

Risks of allow_guest=True:
1.API Abuse - Attackers can again and again call the API and overload the server.
2.Data Scraping - Public APIs may expose data that attackers can scrape.
3.Denial of Service (DoS) - High volumes of requests can slow down or crash the system.

### M1 - Server Script Doctype

**1. Python functions/modules blocked in the Server Script sandbox**

Server Scripts run in a restricted sandbox environment for security purposes. Certain Python modules such as `os`, `sys`, `subprocess`, `socket`, `shutil`, and `requests` are not permitted. Potentially unsafe built-in functions like `open()`, `eval()`, `exec()`, `compile()`, and `__import__()` are also restricted to prevent unauthorized system access or unsafe execution.

**2. Three things you cannot do in a Server Script**

1. Access the server file system (for example reading or writing files).  
2. Execute operating system level commands.  
3. Import external Python libraries or restricted modules.

**3. When Server Scripts are acceptable vs when to use App Code**

**Acceptable:**
- Simple automation tasks such as automatically updating a field before saving a document.
- Small internal APIs or lightweight reporting logic.

**Use App Code when:**
- Implementing complex business logic involving multiple DocTypes.
- Integrating with external services such as APIs, payment gateways, or messaging systems.

**4. Governance / Maintainability risks**

Server Scripts are stored directly in the database instead of being tracked in version control systems like Git. Because of this, changes are harder to audit, review, and maintain. Since they can also be modified directly through the UI, there is a risk of untracked changes affecting production environments.

---

### M2 - Caching, Redis & Cache Invalidation

### Task - A

Frappe uses Redis as a caching layer to improve system performance by storing frequently accessed data.

Examples of data cached in Redis include:

1. **Bootinfo** – Stores user session details such as roles, permissions, modules, and system defaults required during UI loading.  
2. **DocType Metadata** – Contains the structure of DocTypes including fields, properties, and permission settings.  
3. **Website Context** – Cached context used when rendering website pages.  
4. **Translations** – Language translation data used in the frontend interface.  
5. **User Permissions** – Cached permission rules that reduce repeated database queries.

Running `frappe.clear_cache()` removes these cached values so that Frappe rebuilds them from the database.

---

### Task - C

If the browser continues to display outdated JavaScript after making changes, the issue is usually caused by cached frontend assets.

To refresh the assets, run:

```
bench build --app quickfix
```

This command rebuilds the JavaScript and frontend assets for the **quickfix** app so the browser loads the latest version.

If the problem persists, restart the services using:

```
bench restart
```

Restarting ensures that runtime caches are cleared and the updated assets are loaded correctly.

When a **DocType structure changes**, stale UI issues may occur due to cached metadata. Clearing the cache or restarting services forces the system to regenerate the form layout so the UI reflects the latest DocType configuration.

## M3 - Logging, Error Handling & Observability

### Task C — Debugging stale UI

**Stale JS after a JS file change:**
Run `bench build --app quickfix` to recompile and bundle assets.
Frappe appends a content hash to asset filenames, forcing the browser
to download the new file instead of using its cached copy.

**Stale field labels after a DocType change:**
Run `bench --site quickfix-dev.localhost clear-cache` or call
`frappe.clear_cache()` in bench console. This clears the DocType
metadata cache in Redis.

### Task C — Production debugging without developer_mode

1. Check **Setup → Error Log** — all unhandled exceptions logged here
   with full tracebacks even when developer_mode is off
2. Check **Audit Log** — trace exact sequence of events
3. Check `frappe-bench/logs/quickfix.log` — named logger output
   with timestamps to reconstruct sequence of events

## N1 Task C — ignore_permissions analysis

### Every place ignore_permissions=True is used:

1. `job_card.py on_submit → frappe.db.set_value (stock deduction)`
   System-initiated stock deduction triggered by job submission,
   not a direct user request to edit Spare Part records.

2. `job_card.py on_submit → invoice.insert(ignore_permissions=True)`
   Service Invoice is auto-created as a system consequence of submission,
   not a user manually creating an invoice.

3. `job_card.py on_cancel → invoice.cancel()`
   Invoice cancellation is a system consequence of job cancellation,
   not a user directly cancelling the invoice.

### What if a malicious intern did this:

@frappe.whitelist(allow_guest=True)
def evil_endpoint():
    frappe.get_doc("User", "Administrator").ignore_permissions = True
    # Now ANY anonymous internet user can read, write, delete
    # ANY record in the entire database with zero authentication.

## Q1. What Linux service containers does Frappe CI need and why? What breaks if MariaDB is missing?

Frappe CI needs MariaDB and Redis as service containers. MariaDB is where
Frappe stores everything — when bench new-site runs in CI, it creates the
database there. If MariaDB is missing, bench new-site just fails and the
entire pipeline stops before a single test runs. Redis is needed for cache
and queue — Frappe expects it on startup even in test mode, so without it
the import itself crashes.

## Q2. Why does ERPNext CI use --skip-assets when installing apps?

Building JS and CSS bundles takes around 3 to 5 minutes and needs Node.js.
Tests run purely in Python and never open a browser, so the built assets are
completely useless in CI. --skip-assets just skips that step and makes the
pipeline faster without affecting anything the tests actually care about.

## Q3. What is the purpose of bench start in CI versus bench serve? Does CI need either?

bench start launches everything — web, worker, scheduler, socketio. bench
serve launches only the web server. CI needs neither of them. bench run-tests
connects to the database directly through Frappe's Python layer and does not
go through HTTP at all, so no server needs to be running.

## Q4. What happens to the test site after the CI run completes? Is cleanup needed?

GitHub spins up a temporary Linux machine for the workflow and destroys it
the moment the run finishes. The site, the database, every file — all gone
automatically. No cleanup step is needed.