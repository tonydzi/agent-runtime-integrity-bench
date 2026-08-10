#!/usr/bin/env python3
"""Regenerate the animated terminal demo used at the top of README.md.

Every line it draws is copied verbatim from a real run — this script does not
invent output. Regenerate after a run whose summary changed:

    python3 run_bench.py --json /tmp/r.json 2>/tmp/summary.txt
    python3 .github/assets/make_demo.py /tmp/summary.txt 1 > .github/assets/demo.svg

Args: <summary-file> <exit-code>. With no args it replays the checked-in
2026-08-10 run against openai-agents 0.19.4 (the constant below), so the demo
stays regenerable on a machine that cannot install the SDK.

Output: a self-contained SMIL-animated SVG (no fonts, no scripts, no network),
because GitHub renders README images through a proxy that drops both.
"""
import html
import sys

# Verbatim stderr summary of: .venv/bin/python run_bench.py
# openai-agents 0.19.4, aiosqlite 0.22.1, sqlalchemy 2.0.51, Python 3.12.13,
# macOS-26.3.1-x86_64. Full report: results/2026-08-10-openai-agents-0.19.4.json
FALLBACK = """== summary ==
VIOL ARIB-REPLAY-001    [sqlite] redelivered batch (same logical message) is visible exactly once
VIOL ARIB-REPLAY-001    [async-sqlite] redelivered batch (same logical message) is visible exactly once
VIOL ARIB-REPLAY-001    [advanced-sqlite] redelivered batch (same logical message) is visible exactly once
VIOL ARIB-REPLAY-001    [sqlalchemy] redelivered batch (same logical message) is visible exactly once
OK   ARIB-CONC-001      [sqlite] 200 concurrent appends -> 200 visible items, 0 lost, 0 duplicated
OK   ARIB-CONC-002      [sqlite] close() is idempotent under concurrency: two concurrent close() never raise
OK   ARIB-CONC-003      [sqlite] a write after close() is refused loudly (exception), never silently committed or dropped
OK   ARIB-CONC-001      [async-sqlite] 200 concurrent appends -> 200 visible items, 0 lost, 0 duplicated
OK   ARIB-CONC-002      [async-sqlite] close() is idempotent under concurrency: two concurrent close() never raise
OK   ARIB-CONC-003      [async-sqlite] a write after close() is refused loudly (exception), never silently committed or dropped
OK   ARIB-CONC-001      [advanced-sqlite] 200 concurrent appends -> 200 visible items, 0 lost, 0 duplicated
OK   ARIB-CONC-002      [advanced-sqlite] close() is idempotent under concurrency: two concurrent close() never raise
OK   ARIB-CONC-003      [advanced-sqlite] a write after close() is refused loudly (exception), never silently committed or dropped
OK   ARIB-CONC-001      [sqlalchemy] 200 concurrent appends -> 200 visible items, 0 lost, 0 duplicated
N/A  ARIB-CONC-002      [sqlalchemy] close() is idempotent under concurrency: two concurrent close() never raise
N/A  ARIB-CONC-003      [sqlalchemy] a write after close() is refused loudly (exception), never silently committed or dropped"""

BG, FG, DIM = "#0d1117", "#c9d1d9", "#8b949e"
RED, GREEN, BLUE, YELLOW = "#f85149", "#3fb950", "#79c0ff", "#d29922"
CH = 7.22          # advance width of 12px DejaVu Sans Mono
LH = 19            # line height
PAD_X, PAD_Y = 18, 16
CHROME = 30        # title-bar height

# The summary is wide; trim the invariant prose to keep the image readable at
# README width. The IDs, adapters and verdicts — the part being claimed — are
# never trimmed.
MAX_COLS = 104


def colour(line):
    if line.startswith("VIOL"):
        return RED
    if line.startswith("OK"):
        return GREEN
    if line.startswith("N/A"):
        return DIM
    if line.startswith("=="):
        return YELLOW
    return FG


def main():
    if len(sys.argv) > 1:
        summary = open(sys.argv[1], encoding="utf-8").read().strip("\n")
    else:
        summary = FALLBACK
    exit_code = sys.argv[2] if len(sys.argv) > 2 else "1"

    cmd = "python run_bench.py"
    body = [ln for ln in summary.split("\n") if ln.strip()]
    trimmed = [(ln[: MAX_COLS - 1] + "…") if len(ln) > MAX_COLS else ln for ln in body]

    tail = [
        "",
        f"$ echo $?              # 0 all held · 1 violations found · 4 harness itself failed",
        exit_code,
    ]

    rows = ["$ " + cmd] + trimmed + tail
    width = int(PAD_X * 2 + CH * (MAX_COLS + 2))
    height = int(CHROME + PAD_Y * 2 + LH * (len(rows) + 0.5))

    # Timing: type the command, stream the verdicts, hold the frame, loop.
    type_time = 1.2
    per_line = 0.16
    stream_end = type_time + per_line * len(trimmed) + 0.9
    total = stream_end + 4.2

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,'
        f'Menlo,Consolas,DejaVu Sans Mono,monospace" font-size="12">',
        f'<rect width="{width}" height="{height}" rx="8" fill="{BG}"/>',
        f'<rect width="{width}" height="{CHROME}" rx="8" fill="#161b22"/>',
        f'<rect y="{CHROME-8}" width="{width}" height="8" fill="#161b22"/>',
    ]
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(f'<circle cx="{20 + i*18}" cy="{CHROME/2}" r="5.5" fill="{c}"/>')
    out.append(
        f'<text x="{width/2}" y="{CHROME/2 + 4}" fill="{DIM}" text-anchor="middle" '
        f'font-size="11">agent-runtime-integrity-bench — openai-agents 0.19.4, no API key, no network</text>'
    )

    def reveal(at):
        """One indefinitely repeating animate: hidden until `at`, then visible
        for the rest of the cycle. Looping this way (rather than begin= +
        fill=freeze) is what makes the whole frame replay without a script."""
        k = max(0.0001, min(at / total, 0.98))
        return (
            f'<animate attributeName="opacity" values="0;0;1;1;0" '
            f'keyTimes="0;{k:.4f};{min(k+0.004, 0.985):.4f};0.985;1" '
            f'dur="{total:.2f}s" repeatCount="indefinite"/>'
        )

    y = CHROME + PAD_Y + 12

    # Prompt line, typed character by character.
    out.append(f'<text x="{PAD_X}" y="{y}" fill="{BLUE}">$</text>')
    tx = PAD_X + CH * 2
    for i, ch in enumerate(cmd):
        out.append(
            f'<text x="{tx + CH*i:.1f}" y="{y}" fill="{FG}" opacity="1">'
            f'{html.escape(ch)}{reveal(i * (type_time / len(cmd)))}</text>'
        )

    for n, line in enumerate(trimmed):
        y += LH
        out.append(
            f'<text x="{PAD_X}" y="{y}" fill="{colour(line)}" opacity="1" '
            f'xml:space="preserve">{html.escape(line)}'
            f'{reveal(type_time + 0.35 + n * per_line)}</text>'
        )

    for line in tail:
        y += LH
        if not line.strip():
            continue
        fill = BLUE if line.startswith("$") else RED
        out.append(
            f'<text x="{PAD_X}" y="{y}" fill="{fill}" opacity="1" xml:space="preserve">'
            f'{html.escape(line)}{reveal(stream_end)}</text>'
        )

    # Cursor: blinks while typing, parks at the end.
    out.append(
        f'<rect x="{PAD_X + CH*2 + CH*len(cmd):.1f}" y="{CHROME + PAD_Y + 2}" '
        f'width="{CH:.1f}" height="14" fill="{FG}" opacity="0.8">'
        f'<animate attributeName="opacity" values="0.8;0;0.8" dur="1s" repeatCount="indefinite"/>'
        f'</rect>'
    )
    # One driver animation sets the loop period for the whole frame.
    out.append(
        f'<rect width="1" height="1" fill="{BG}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0" dur="{total:.2f}s" repeatCount="indefinite"/>'
        f'</rect>'
    )
    out.append("</svg>")
    print("\n".join(out))


if __name__ == "__main__":
    main()
