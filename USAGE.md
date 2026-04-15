# Black Ops Usage Guide

## 1. Quickstart in 5 Minutes

1. Make sure you are in the project directory.
2. Start the main application:
   ```bash
   python3 black_ops.py
   ```
3. Or start the interactive shell:
   ```bash
   python3 black_ops_cli.py
   ```
4. Choose a profile that matches your use case:
   - `lab` for local testing and full flexibility in a controlled environment
   - `osint` for passive research
   - `pentest` for authorized testing
   - `audit` for evidence-oriented checks
   - `training` or `demo` for safe exercises and demonstrations
5. Run the system check first, then choose the appropriate tool or workflow.
6. Save results through the reporting or logging features if you want to document or share them.

## 2. OSINT Workflow

1. Set the profile to `osint`.
2. Define the scope as narrowly as possible:
   - Domain
   - Username
   - Email
   - IP
   - Person or organization
3. Prefer passive recon and intelligence workflows.
4. Avoid active or disruptive actions unless they are explicitly in scope.
5. Consolidate the results:
   - merge duplicate hits
   - mark false positives
   - look for relationships between identities, domains, and infrastructure
6. Generate a report at the end and redact sensitive contents before sharing.

## 3. Authorized Pentest Workflow

1. Confirm written authorization first.
2. Define scope, target systems, time window, and allowed test depth.
3. Set the profile to `pentest` or `lab`.
4. Start with recon to understand the targets and attack surface.
5. Use only the workflows that are explicitly approved.
6. Keep documentation for every step:
   - what was checked
   - when it was checked
   - what the result was
   - what evidence exists
7. Finish with a report that separates findings, risk, impact, and evidence.

## Practical Commands

```bash
python3 black_ops.py
python3 black_ops_cli.py
python3 -m pytest -q
```

## Recommended Working Style

- Check scope and profile before every action
- Start passive, then move to targeted steps
- Always save results
- Redact reports before sharing them
- Only work against authorized targets

## When to Use Which Profile

- `lab`: full functionality in a controlled environment
- `osint`: passive collection and analysis
- `pentest`: authorized technical testing
- `audit`: evidence-oriented, conservative checks
- `training`: workshops and exercises
- `demo`: safe demonstrations
