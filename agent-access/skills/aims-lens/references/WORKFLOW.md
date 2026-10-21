# Commands and harness contract

Run these from the installed skill directory. On Windows use `python` instead of `python3`. Every example is synthetic. IDs, revisions and hashes must come from actual responses.

```bash
python3 scripts/aims_client.py role-create --body examples/role.json --key example-role-001
python3 scripts/aims_client.py material-text --role role_demo --body examples/material.json --key example-material-001
python3 scripts/aims_client.py directive-create --role role_demo --body examples/directive.json --key example-directive-001
python3 scripts/aims_client.py interview-create --role role_demo --body examples/interview.json --key example-interview-001
python3 scripts/aims_client.py rubric-create --role role_demo --body examples/rubric.json --key example-rubric-001
python3 scripts/aims_client.py role-get --role role_demo
python3 scripts/aims_client.py submission-freeze --role role_demo --body examples/freeze.json --key example-freeze-001
python3 scripts/aims_client.py lens-build --submission sub_demo --body examples/build.json --key example-build-001
python3 scripts/aims_client.py lens-get --lens lens_demo --version 1
```

These default to dry-run and never need credentials. For execution, append `--execute`; first run capabilities and whoami. Persist idempotency keys in the harness state before sending requests. Do not print full input files to public logs.

File upload (use your own authorized PDF/DOCX/TXT):

```bash
python3 scripts/aims_client.py material-file --role role_demo --file /absolute/path/role.pdf --document-type JOB_DESCRIPTION --title "Role description" --key example-file-001
```

To inspect a file without uploading, omit `--execute`. The client hashes it and plans a multipart upload. An accepted upload still has `body_parsing_status=not_performed`.

## Local mock

Start `tests/mock_server.py` from the repository root. It prints the randomly allocated loopback port. Set `AIMS_API_KEY` to the public test value `mock-only-not-a-secret` in that terminal's environment (not in chat). Then execute:

```bash
python3 scripts/aims_client.py capabilities --base-url http://127.0.0.1:PORT --allow-local-mock --execute
```

Use the same options on later commands. Mock state is ephemeral; no real documents, real builder or database are used. Any Lens fixture is marked `mock_only=true`; never present it as a usable AIMS Lens.

## Harness adapter

Input: operation + resource IDs + JSON file path or local file + persisted idempotency key + credential reference resolved by the harness. `--base-url` is an origin, not a path. Production candidate origin is fixed; arbitrary hosts, credentials in URLs, redirects and remote HTTP are rejected.

stdout is one JSON object. Exit 0 means a dry-run plan or successful validated response; exit 2 means local input/config/contract validation failed; exit 3 means HTTP/API error; exit 4 means transport result unknown. Distinguish `mode=dry_run` from `mode=execute` before treating a response as a completed operation. Errors retain safe code, request ID and retryability; arbitrary server error text/details are withheld. Execution returns the authorized API data, which may include private hiring content: route it only to the requesting context.

No automatic retries, pagination, polling, cookie use or shell evaluation. A timeout after a write has unknown outcome; store key and request ID if available and reconcile before retrying. File body/JSON values are never interpolated into shell commands.
