import os
import sys
import csv
import subprocess
import re

IN_PATH = "/Users/mac/01work/git-project/ketacli/ketacli/sdk/test/zabbix_sigle.csv"
OUT_PATH = os.path.join(os.path.dirname(IN_PATH), "zabbix_sigle.converted.csv")

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)

def convert_line(line: str) -> str:
    cmd = [sys.executable, "-m", "ketacli", "convert", "--src", "zabbix", "--dst", "spl", "--text", line]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = strip_ansi(proc.stdout or "").strip()
    err = strip_ansi(proc.stderr or "").strip()
    if proc.returncode != 0:
        return f"[ERROR] {err}" if err else "[ERROR] conversion failed"
    return out

def main():
    lines = []
    with open(IN_PATH, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            lines.append(ln)
    rows = []
    for i, ln in enumerate(lines, start=1):
        spl = convert_line(ln)
        rows.append([ln, spl])
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["original", "spl"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_PATH}")

if __name__ == "__main__":
    main()