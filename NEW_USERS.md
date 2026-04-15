# Black Ops for New Users

## What is BlackOps?

BlackOps is a modular framework for authorized security workflows, OSINT, recon, reporting, and plugin usage. It is designed for lab and approval-based scenarios, not for unauthorized actions.

## How do I start it?

```bash
python3 black_ops.py
```

Or as an interactive shell:

```bash
python3 black_ops_cli.py
```

## Which profile should I use?

- `lab`: when you want maximum flexibility in a local or controlled test environment
- `osint`: when you only want passive research
- `pentest`: when you have written authorization for testing
- `audit`: when you want conservative, evidence-oriented checks
- `training` / `demo`: when you want to practice or present safely

## Three simple rules

1. Only use authorized targets.
2. Check the scope and profile first.
3. Always document results and redact sensitive data.

## If you are unsure

- Start with `lab` or `training`
- Then read [USAGE.md](USAGE.md)
- Never use offensive functions outside a clear scope
