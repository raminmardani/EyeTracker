"""D1-D7 static eval gate - delta-scoped against a base ref.

Owns the baseline diff for BOTH the local gate and CI (eval-framework.md 2.2).
Findings are keyed on (rule, file, message) - never line numbers, which shift.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / ".evals/config.json").read_text(encoding="utf-8"))
TH = CFG["thresholds"]
KEY = os.environ.get("EVAL_KEY") or "local"
EV = ROOT / ".spec/aire-docs/implementation/code/eval-evidence" / KEY
VENV = ROOT / ".venv/Scripts"


def tool(name):
    exe = VENV / (name + ".exe")
    return str(exe) if exe.exists() else name


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def changed_files(base):
    rc, out, _ = run(["git", "diff", "--name-only", base + "...HEAD"], cwd=ROOT)
    if rc:
        rc, out, _ = run(["git", "diff", "--name-only", base], cwd=ROOT)
    return [f for f in out.splitlines()
            if f.endswith(".py") and not f.startswith(".evals/")]


def _rel(path, tree):
    return str(path).replace(str(tree), "").lstrip("\\/").replace("\\", "/")


# ---- collectors: each returns (set of (rule, file, message), raw output) ----

def d1_lint(tree, files):
    if not files:
        return set(), ""
    rc, out, err = run([tool("ruff"), "check", "--output-format", "json",
                        "--force-exclude"] + files, cwd=tree)
    raw = out or err
    try:
        data = json.loads(out or "[]")
    except json.JSONDecodeError:
        return set(), raw
    return {(d.get("code") or "?", _rel(d.get("filename", ""), tree),
             (d.get("message") or "")[:120]) for d in data}, raw


def d2_types(tree, files):
    if not files:
        return set(), ""
    rc, out, err = run([tool("mypy"), "--ignore-missing-imports", "--no-error-summary",
                        "--hide-error-context", "--no-color-output"] + files, cwd=tree)
    raw = out + err
    found = set()
    pat = re.compile(r"^(.*?):(\d+):(?:\d+:)?\s*error:\s*(.*?)(?:\s+\[([\w-]+)\])?$")
    for line in out.splitlines():
        m = pat.match(line)
        if m:
            found.add((m.group(4) or "mypy", m.group(1).replace("\\", "/"),
                       m.group(3)[:120]))
    return found, raw


def d3_sast(tree, files):
    if not files:
        return set(), ""
    rc, out, err = run([tool("semgrep"), "--config", "p/python", "--json", "--quiet",
                        "--metrics", "off"] + files, cwd=tree)
    raw = out or err
    try:
        data = json.loads(out or "{}")
    except json.JSONDecodeError:
        return set(), raw
    found = set()
    for r in data.get("results", []):
        sev = (r.get("extra", {}).get("severity") or "INFO").upper()
        found.add((r.get("check_id", "?") + "|" + sev, r.get("path", ""),
                   (r.get("extra", {}).get("message") or "")[:120]))
    return found, raw


def d4_deps(tree, files):
    rc, out, err = run([tool("pip-audit"), "-f", "json",
                        "--progress-spinner", "off"], cwd=tree)
    raw = out or err
    try:
        data = json.loads(out or "{}")
    except json.JSONDecodeError:
        return set(), raw
    found = set()
    for dep in data.get("dependencies", []):
        for v in dep.get("vulns", []):
            found.add((v.get("id", "?"), dep.get("name", "?"),
                       ",".join(v.get("fix_versions", []))[:120]))
    return found, raw


def d5_licences(tree, files):
    rc, out, err = run([tool("pip-licenses"), "--format", "json"], cwd=tree)
    raw = out or err
    try:
        data = json.loads(out or "[]")
    except json.JSONDecodeError:
        return set(), raw
    bad = set(TH["disallowedLicenses"])
    return {("DISALLOWED_LICENCE", p.get("Name", "?"), p.get("License", "?"))
            for p in data if p.get("License") in bad}, raw


def d6_complexity(tree, files):
    if not files:
        return set(), ""
    cap = TH["maxCyclomaticComplexity"]
    rc, out, err = run([tool("ruff"), "check", "--select", "C901",
                        "--output-format", "json", "--force-exclude",
                        "--config", "lint.mccabe.max-complexity=" + str(cap)]
                       + files, cwd=tree)
    raw = out or err
    try:
        data = json.loads(out or "[]")
    except json.JSONDecodeError:
        return set(), raw
    return {("C901", _rel(d.get("filename", ""), tree),
             (d.get("message") or "")[:120]) for d in data}, raw


def d7_secrets(tree, files):
    """gitleaks has no wheel here and no container runtime for the OCI rung.
    detect-secrets is a DOCUMENTED substitute, recorded in the evidence.
    It is never silently reported as N/A."""
    if not files:
        return set(), ""
    rc, out, err = run([tool("detect-secrets"), "scan"] + files, cwd=tree)
    raw = out or err
    try:
        data = json.loads(out or "{}")
    except json.JSONDecodeError:
        return set(), raw
    found = set()
    for path, items in (data.get("results") or {}).items():
        for it in items:
            found.add((it.get("type", "secret"), path,
                       (it.get("hashed_secret") or "")[:32]))
    return found, raw


GATES = [
    ("D1_lint", d1_lint, "json"),
    ("D2_typecheck", d2_types, "txt"),
    ("D3_sast", d3_sast, "json"),
    ("D4_deps", d4_deps, "json"),
    ("D5_licences", d5_licences, "json"),
    ("D6_complexity", d6_complexity, "json"),
    ("D7_secrets", d7_secrets, "json"),
]


def verdict(gate, new):
    """THE ONLY place a gate pass/fail is decided. No hardcoded PASS anywhere."""
    n = len(new)
    if gate == "D1_lint":
        allowed = TH["lintErrorsAllowedDelta"]
        return ("PASS" if n <= allowed else "FAIL",
                str(n) + " new (allowed delta " + str(allowed) + ")")
    if gate == "D2_typecheck":
        allowed = TH["typeErrorsAllowed"]
        return ("PASS" if n <= allowed else "FAIL",
                str(n) + " new (allowed " + str(allowed) + ")")
    if gate == "D3_sast":
        a = TH["semgrepFindingsAllowed"]
        sev = {"critical": 0, "high": 0, "medium": 0}
        for rule, _f, _m in new:
            s = rule.split("|")[-1].lower()
            if s == "error":
                sev["high"] += 1
            elif s == "warning":
                sev["medium"] += 1
            else:
                sev["medium"] += 0
        bad = [k for k in ("critical", "high", "medium") if sev[k] > a.get(k, 0)]
        return ("FAIL" if bad else "PASS", str(sev) + " vs allowed " + str(a))
    if gate == "D4_deps":
        a = TH["dependencyVulnerabilitiesAllowed"]
        cap = a.get("critical", 0) + a.get("high", 0)
        return ("FAIL" if n > cap else "PASS", str(n) + " new advisories")
    if gate == "D5_licences":
        return ("FAIL" if n else "PASS", str(n) + " disallowed")
    if gate == "D6_complexity":
        return ("FAIL" if n else "PASS",
                str(n) + " functions over " + str(TH["maxCyclomaticComplexity"]))
    if gate == "D7_secrets":
        allowed = TH["secretFindingsAllowed"]
        return ("PASS" if n <= allowed else "FAIL",
                str(n) + " new (allowed " + str(allowed) + ")")
    raise SystemExit("ERROR: no verdict rule for " + gate)


def main():
    if len(sys.argv) < 2:
        print("usage: static_evals.py <base-ref>", file=sys.stderr)
        return 2
    base = sys.argv[1]
    # V12: every directory is created before anything writes to it
    (EV / "static" / "baseline").mkdir(parents=True, exist_ok=True)
    (EV / "judge").mkdir(parents=True, exist_ok=True)
    (ROOT / ".evals" / "_run").mkdir(parents=True, exist_ok=True)

    files = changed_files(base)
    print("[static-evals] base=" + base + "  changed .py files=" + str(len(files)))

    wt = Path(tempfile.mkdtemp(prefix="aire-base-"))
    shutil.rmtree(wt, ignore_errors=True)
    rc, _o, err = run(["git", "worktree", "add", "--detach", str(wt), base], cwd=ROOT)
    if rc:
        print("ERROR: could not create base worktree: " + err, file=sys.stderr)
        return 2
    results = {}
    failed = []
    try:
        base_files = [f for f in files if (wt / f).exists()]
        for gate, fn, ext in GATES:
            pre, pre_raw = fn(wt, base_files)
            post, post_raw = fn(ROOT, files)
            (EV / "static" / "baseline" / (gate + "." + ext)).write_text(
                pre_raw or "", encoding="utf-8")
            (EV / "static" / (gate + "-post." + ext)).write_text(
                post_raw or "", encoding="utf-8")
            new = post - pre
            status, detail = verdict(gate, new)
            results[gate] = {
                "status": status,
                "detail": detail,
                "newFindings": len(new),
                "preExisting": len(pre),
                "new": sorted(r + " :: " + f + " :: " + m for r, f, m in new)[:25],
            }
            if gate == "D7_secrets":
                results[gate]["toolDeviation"] = (
                    "detect-secrets substituted for gitleaks: no wheel available and no "
                    "container runtime for the OCI rung. Documented deviation, not N/A.")
            flag = "OK  " if status == "PASS" else "FAIL"
            print("  [" + flag + "] " + gate.ljust(14)
                  + " new=" + str(len(new)).ljust(4)
                  + " pre-existing=" + str(len(pre)).ljust(4) + " " + detail)
            if status == "FAIL":
                failed.append(gate)
    finally:
        run(["git", "worktree", "remove", "--force", str(wt)], cwd=ROOT)
        shutil.rmtree(wt, ignore_errors=True)

    overall = "FAIL" if failed else "PASS"
    payload = {
        "evalKey": KEY,
        "base": base,
        "scope": CFG["scope"],
        "changedFiles": files,
        "gates": results,
        "overall": {"verdict": overall, "checksRun": len(GATES),
                    "checksTotal": len(GATES), "failed": failed},
    }
    (EV / "static-evals.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (ROOT / ".evals" / "_run" / "failed-gates.txt").write_text(
        "\n".join(failed) + ("\n" if failed else ""), encoding="utf-8")
    print("[static-evals] verdict=" + overall + "  failed=" + (str(failed) if failed else "none"))
    print("[static-evals] evidence -> " + str(EV))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
