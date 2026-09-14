"""CI self-repair agent.

Contract (ci-pipeline-generation.md 6.0.1 / 6.4 / 6.5):
  - It is GIVEN the failure. It does not hunt for one.
    PRIMARY input  : .evals/_run/failed-gates.txt
    SUPPLEMENTARY  : eval.json (never a precondition)
  - Triage BEFORE repairing: not every red job is a code defect.
  - Re-run run-static-evals AND run-evals after the fix, BEFORE committing.
  - V19: if its inputs are missing it exits NON-ZERO naming what was missing.
    It never exits 0 without repairing, and never reclassifies a missing input
    as an "infrastructure failure" of the build.
  - Enforces retryLimitForSelfRepair.
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
RETRY_LIMIT = CFG.get("retryLimitForSelfRepair", 3)


def _safe_key(raw):
    key = (raw or "local").strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", key) or key in (".", ".."):
        raise SystemExit(
            "ERROR: EVAL_KEY must be a single path segment matching "
            "[A-Za-z0-9][A-Za-z0-9._-]{0,63} (got " + repr(raw) + "). "
            "A branch ref contains '/' and is not a valid key.")
    return key


KEY = _safe_key(os.environ.get("EVAL_KEY"))
EV = ROOT / ".spec/aire-docs/implementation/code/eval-evidence" / KEY
FAILED = ROOT / ".evals/_run/failed-gates.txt"

# Section 6.4 - triage. Not every red gate is a code defect the agent may fix.
INFRA_MARKERS = (
    "command not found", "No such file or directory", "connection refused",
    "could not resolve host", "rate limit", "unauthorized", "401", "403",
    "Permission denied", "timed out",
)
NOT_CODE_DEFECT = {
    # gates whose failure is usually environmental, requiring a human decision
    "D4_deps": "a new upstream advisory is not necessarily this diff's defect",
    "D5_licences": "a licence change is a policy decision, not a code fix",
}


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def die(msg, code=2):
    """V19: name what was missing and exit NON-ZERO. Never exit 0."""
    print("ERROR: " + msg, file=sys.stderr)
    return code


def read_failed_gates():
    if not FAILED.exists():
        return None, str(FAILED) + " does not exist"
    gates = [g.strip() for g in FAILED.read_text(encoding="utf-8").splitlines() if g.strip()]
    if not gates:
        return None, str(FAILED) + " is empty - self-repair was invoked with no failing gate"
    return gates, None


def load_eval_json():
    """SUPPLEMENTARY only. Its absence is never a precondition failure."""
    p = EV / "eval.json"
    if not p.exists():
        print("[auto-fix] note: " + str(p) + " absent - continuing on failed-gates.txt alone")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        print("[auto-fix] note: eval.json unreadable (" + str(exc) + ") - continuing")
        return {}


def gather_logs(gates):
    out = []
    for g in gates:
        for cand in ((EV / "static" / (g + "-post.json")),
                     (EV / "static" / (g + "-post.txt")),
                     (EV / "judge" / "architecture-score.json"),
                     (EV / "judge" / "security-score.json")):
            if cand.exists():
                txt = cand.read_text(encoding="utf-8", errors="replace")[:6000]
                if txt.strip():
                    out.append("--- " + cand.name + " ---\n" + txt)
                break
    return "\n\n".join(out)


def triage(gates, evaljson):
    """Return (repairable, deferred). Deferred gates are reported, not fixed."""
    repairable, deferred = [], []
    blob = gather_logs(gates)
    for g in gates:
        if g in NOT_CODE_DEFECT:
            deferred.append((g, NOT_CODE_DEFECT[g]))
        elif any(m.lower() in blob.lower() for m in INFRA_MARKERS) and g.startswith("D"):
            deferred.append((g, "log shows an environment/infrastructure marker"))
        else:
            repairable.append(g)
    return repairable, deferred


def build_brief(gates, evaljson):
    parts = [
        "You are repairing a FAILING CI eval gate in this repository.",
        "",
        "FAILING GATES (authoritative, from .evals/_run/failed-gates.txt):",
        "  " + ", ".join(gates),
        "",
        "Rules:",
        "  - Fix the CODE that caused the finding. Never weaken a threshold in",
        "    .evals/config.json, never edit a rubric, never mark a gate N/A.",
        "  - Make the smallest change that removes the finding.",
        "  - Do not modify .evals/rubrics/** or .spec/architecture.md Section 10.",
        "",
    ]
    for g, v in (evaljson.get("gates") or {}).items():
        if g in gates:
            parts.append("GATE " + g + ": " + str(v.get("detail", "")))
    logs = gather_logs(gates)
    if logs:
        parts += ["", "EVIDENCE:", logs[:12000]]
    return "\n".join(parts)


def invoke_claude(brief):
    exe = shutil.which("claude")
    if not exe:
        return None, "claude CLI not found on PATH"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(brief)
        pf = fh.name
    try:
        with open(pf, "r", encoding="utf-8") as stdin_fh:
            p = subprocess.run(
                [exe, "-p", "--output-format", "text",
                 "--permission-mode", "acceptEdits"],
                cwd=ROOT, capture_output=True, text=True,
                encoding="utf-8", errors="replace", stdin=stdin_fh, timeout=1800)
        return (p.stdout or "").strip(), None
    finally:
        os.unlink(pf)


def reverify(base):
    """Rule 4: re-run BOTH gates before committing. Non-zero means still failing."""
    a = run(["bash", ".evals/scripts/run-static-evals.sh", base])
    print(a.stdout[-1500:])
    b = run(["bash", ".evals/scripts/run-evals.sh", base])
    print(b.stdout[-1500:])
    return a.returncode == 0 and b.returncode == 0


def main():
    base = os.environ.get("BASE_REF") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not base:
        return die("no base ref given (argv[1] or BASE_REF)")

    gates, why = read_failed_gates()
    if gates is None:
        # V19: missing PRIMARY input is an ERROR naming what was missing.
        return die("self-repair has no failing-gate input: " + why
                   + ". This is NOT an infrastructure failure of the build and is "
                     "NOT a reason to exit 0.")

    evaljson = load_eval_json()
    print("[auto-fix] failing gates: " + ", ".join(gates))

    repairable, deferred = triage(gates, evaljson)
    for g, reason in deferred:
        print("[auto-fix] DEFERRED " + g + ": " + reason + " - needs a human decision")
    if not repairable:
        return die("every failing gate was triaged as not-a-code-defect: "
                   + ", ".join(g for g, _ in deferred)
                   + ". Reporting rather than repairing.")

    for attempt in range(1, RETRY_LIMIT + 1):
        print("[auto-fix] repair attempt " + str(attempt) + " of " + str(RETRY_LIMIT))
        out, err = invoke_claude(build_brief(repairable, evaljson))
        if err:
            return die("cannot invoke the repair agent: " + err)
        if not reverify(base):
            print("[auto-fix] gates still failing after attempt " + str(attempt))
            continue
        st = run(["git", "status", "--porcelain"])
        if not st.stdout.strip():
            return die("gates pass but the agent produced no change - refusing to "
                       "report a repair that did not happen")
        run(["git", "add", "-A"])
        run(["git", "commit", "-m",
             "fix(ci): self-repair " + ", ".join(repairable)
             + "\n\nAIRE-Version: 1.0"])
        print("[auto-fix] repaired and committed on attempt " + str(attempt))
        return 0

    return die("retryLimitForSelfRepair (" + str(RETRY_LIMIT)
               + ") exhausted; gates still failing: " + ", ".join(repairable), code=1)


if __name__ == "__main__":
    sys.exit(main())
