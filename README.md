### Quickfix

Assesment purpose

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app quickfix
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/quickfix
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
# QuickFix-Frappe-app

<!-- Question: -->
1.In README.md explain in 4 sentences: what each config file is for, and what breaks
if you accidentally put a secret in common_site_config.json
<!-- Answer: -->
site_config.json stores settings specific to one site, like database credentials and site-level secrets.

common_site_config.json contains global settings shared across all sites in the bench, such as Redis or developer mode configuration.

App config files like hooks.py define how the app behaves, loads features, and connects with Frappe events.

If a secret is accidentally placed in common_site_config.json, it becomes shared across every site, which can expose sensitive data and create security risks or unintended access.


<!-- Question: -->
2.In README.md: list the 4 processes bench start launches (web, worker, scheduler,
socketio) and explain what happens to background jobs if the worker process
crashes.
<!-- Answer: -->
bench start runs four processes web (handles HTTP requests), worker (executes background jobs),scheduler(triggers scheduled tasks), and socketio(real-time updates),and if the worker crashes,queued background jobs stop processing until the worker restarts,causing delays but not data loss since jobs remain in the queue.


<!-- Question: -->
3.When a browser hits /api/method/quickfix.api.get_job_summary - what Python
function handles this request and how does Frappe find it?
<!-- Answer: -->
The Python function get_job_summary inside the file quickfix/api.py handles this request.
Frappe reads the dotted path (quickfix.api.get_job_summary), imports the quickfix app, then loads the api.py module and calls the function.
The function must be decorated with @frappe.whitelist() so it can be accessed via HTTP API.


<!-- Question: -->
When a browser hits /api/resource/Job Card/JC-2024-0001 - what happens
differently compared to /api/method/?
<!-- Answers -->
/api/resource/ uses Frappe’s built-in REST API to directly access DocTypes and database records.
Instead of calling a custom Python function, Frappe automatically loads the Job Card document using its ORM and returns the record data.
/api/method/ executes a specific Python function, while /api/resource/ performs CRUD operations on documents.

<!-- Question: -->
When a browser hits /track-job - which file/function handles it and why?
<!-- Answer: -->
This is handled by a file inside the app’s www/ folder, for example quickfix/www/track-job.py or track-job.html.
Frappe automatically maps URL routes to files inside the www directory.
The function prepares data and renders the web page because www is used for website routes.

<!-- Question: -->
With developer_mode: 1 - trigger a Python exception in one of your whitelisted
methods. What does the browser receive?
Set developer_mode: 0 - repeat. What does the browser receive now? Why is this
important for production?
Where do production errors go if they are hidden from the browser?
<!-- Answers: -->
* With developer_mode: 1, when a Python exception happens, the browser receives the full traceback and detailed error message, which helps debugging.
* With developer_mode: 0, the browser only receives a generic error message (no traceback) to avoid exposing internal code or sensitive details, which is important for production security.
* Hidden production errors are logged in server log files (like `frappe.log` / `error.log`) and can be viewed in logs or Error Log DocType.

<!-- Questions: -->
In a whitelisted method, call frappe.get_doc("Job Card", name) WITHOUT
ignore_permissions. Then log in as a QF Technician user who is NOT assigned to
that job. What error is raised and at what layer does Frappe stop the request?
<!-- Answers: -->
* The error raised will be a PermissionError (Not Permitted) because the user does not have permission to access that Job Card.
* Frappe stops the request at the permission validation layer (DocType permission check / ORM level) before returning the document data, preventing unauthorized access.
