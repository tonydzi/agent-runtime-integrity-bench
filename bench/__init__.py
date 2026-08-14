"""Benchmark package: scenarios, adapters and the report/verdict plumbing.

Layout:
    core                  Finding/Report types, verdicts, exit-code discipline
    adapters              one class per runtime store, behind a tiny async contract
    s2_replay             scenario S2 - replay / idempotency
    s3_concurrent_memory  scenario S3 - concurrent writes, close, write-after-close

Imported by: run_bench.py (the CLI) and selftest.py (the harness self-check).
Nothing here runs at import time - importing the package must stay free of side
effects, because selftest.py imports the same modules it is judging.
"""
