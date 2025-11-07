import csv
import json
import subprocess
import sys
from pathlib import Path


def run_convert(expr: str, repo: str = "zabbix") -> dict:
    cmd = [
        sys.executable,
        "-m",
        "ketacli",
        "convert",
        "--src",
        "zabbix",
        "--dst",
        "spl_json",
        "--host-field",
        "",
        "--origin-field",
        "",
        "--repo",
        repo,
        "-t",
        expr,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"convert failed: {proc.stderr}")
    return json.loads(proc.stdout.strip())


def summarize(idx: int, title: str, expr: str, result: dict) -> dict:
    spl = result.get("SPL", "")
    crontab = result.get("crontab", [])
    return {
        # "index": idx,
        "title": title,
        "zabbix": expr,
        "result": {
            "spl": spl,
            "crontab": crontab
        }
        
        # "has_join": ("join type=" in spl),
        # "has_join_tmp": ("eval join_tmp=1" in spl),
        # "need_alert_is_cond0": ("eval need_alert=cond_0" in spl),
        # "crontab_len": len(crontab),
    }


def main():
    csv_path = Path(__file__).parent / "zabbix_roles.csv"
    rows = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            # Expect 2 columns: title, expression
            if len(row) < 2:
                # skip malformed line
                continue
            title = row[0]
            expr = row[1]
            rows.append((title, expr))

    results = []
    for i, (title, expr) in enumerate(rows, start=1):
        try:
            res = run_convert(expr)
            summary = summarize(i, title, expr, res)
        except Exception as e:
            summary = {
                "index": i,
                "title": title,
                "error": str(e),
            }
        results.append(summary)

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()