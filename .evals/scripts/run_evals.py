"""J1/J2 judge gates + scorecard merge.

Scores each rubric criterion independently against the diff via the Claude Code
CLI in headless mode, merges with the D1-D7 deterministic results, and writes
eval.json + eval-summary.md.

Scoring discipline (eval-framework.md 4.1), enforced in the prompt AND validated
on the response:
  - score once, never re-roll
  - every criterion below 1.0 MUST cite file:line
  - score only what the diff shows
  - a criterion the diff cannot exercise is N/A: excluded, remaining weights
    renormalised to 1.0 - never scored 0
A malformed response is an ERROR (retry once, then fail) - never N/A.
Missing credentials is an ERROR - the gate should have run.
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
def _safe_key(raw):
    """SEC-06: EVAL_KEY is attacker-influenced (env var) and is joined into a
    path that gets mkdir'd and written to. Validate it as a single safe path
    segment; never accept separators or traversal."""
    key = (raw or "local").strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", key) or key in (".", ".."):
        raise SystemExit(
            "ERROR: EVAL_KEY must be a single path segment matching "
            "[A-Za-z0-9][A-Za-z0-9._-]{0,63} (got " + repr(raw) + "). "
            "A branch ref contains '/' and is not a valid key.")
    return key


def _validated_thresholds(cfg):
    """SEC-03: config-supplied values are consumed as gate decisions. Validate
    type and range before any of them can decide a pass/fail."""
    th = cfg.get("thresholds")
    if not isinstance(th, dict):
        raise SystemExit("ERROR: .evals/config.json has no 'thresholds' object")
    numeric = {
        "lintErrorsAllowedDelta": (0, 10000),
        "typeErrorsAllowed": (0, 10000),
        "maxCyclomaticComplexity": (1, 100),
        "secretFindingsAllowed": (0, 10000),
        "unitTestCoverageMin": (0.0, 100.0),
        "behaviorScenarioPassRateMin": (0.0, 100.0),
        "llmJudgeArchitectureScoreMin": (0.0, 1.0),
        "llmJudgeSecurityScoreMin": (0.0, 1.0),
    }
    for name, (lo, hi) in numeric.items():
        if name not in th:
            continue
        v = th[name]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise SystemExit("ERROR: threshold " + name + " must be numeric, got "
                             + type(v).__name__)
        if not (lo <= v <= hi):
            raise SystemExit("ERROR: threshold " + name + "=" + str(v)
                             + " outside [" + str(lo) + ", " + str(hi) + "]")
    if not isinstance(th.get("disallowedLicenses", []), list):
        raise SystemExit("ERROR: disallowedLicenses must be a list")
    return th


CFG = json.loads((ROOT / ".evals/config.json").read_text(encoding="utf-8"))
TH = _validated_thresholds(CFG)
KEY = _safe_key(os.environ.get("EVAL_KEY"))
EV = ROOT / ".spec/aire-docs/implementation/code/eval-evidence" / KEY
MAX_DIFF = 60000

RUBRICS = [
    ("J1", "architecture", "architecture-rubric.json", "llmJudgeArchitectureScoreMin"),
    ("J2", "security", "security-rubric.json", "llmJudgeSecurityScoreMin"),
]


def claude_bin():
    exe = shutil.which("claude")
    if not exe:
        raise SystemExit(
            "ERROR: claude CLI not found on PATH. The judge gate should have run. "
            "This is an ERROR, never N/A.")
    return exe


def get_diff(base):
    p = subprocess.run(["git", "diff", base + "...HEAD"], cwd=ROOT,
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    d = p.stdout or ""
    if not d.strip():
        p = subprocess.run(["git", "diff", base], cwd=ROOT,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        d = p.stdout or ""
    return d[:MAX_DIFF]


def build_prompt(rubric, diff):
    crit = [
        {"id": c["id"], "weight": c["weight"], "constraint": c["constraint"],
         "verifiableAs": c["verifiableAs"]}
        for c in rubric["criteria"]
    ]
    return (
        "You are scoring a code diff against a fixed rubric. Output STRICT JSON ONLY - "
        "no prose, no markdown fence, no explanation outside the JSON.\n\n"
        "RULES:\n"
        "1. Score each criterion independently, once. Never re-roll.\n"
        "2. Score ONLY what the diff shows. Do not assume code outside it.\n"
        "3. Any criterion scored below 1.0 MUST include a citation of the form "
        "\"file.py:LINE\" pointing at the offending line in the diff.\n"
        "4. If the diff cannot exercise a criterion at all, set its score to the string "
        "\"N/A\". Never score 0 for that reason - 0 means an actual violation.\n"
        "5. Return EVERY criterion id from the rubric.\n\n"
        "RESPONSE SHAPE:\n"
        '{"criteria":[{"id":"X-01","weight":0.25,"score":1.0,'
        '"citation":"path.py:12","note":"why"}]}\n\n'
        "RUBRIC:\n" + json.dumps(crit, indent=2) + "\n\nDIFF:\n" + diff + "\n"
    )


def invoke_judge(prompt):
    """Prompt goes via STDIN, never argv: a rubric+diff prompt exceeds the
    32KB Windows command-line limit (WinError 206)."""
    cmd = [claude_bin(), "-p", "--output-format", "text"]
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(prompt)
        pf = fh.name
    try:
        with open(pf, "r", encoding="utf-8") as stdin_fh:
            p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               stdin=stdin_fh, timeout=600)
        return (p.stdout or "").strip()
    finally:
        os.unlink(pf)


def extract_json(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.startswith("json"):
            t = t[4:]
    s, e = t.find("{"), t.rfind("}")
    if s < 0 or e < 0:
        raise ValueError("no JSON object in response")
    return json.loads(t[s:e + 1])


def score_rubric(gate, rubric, diff):
    """Returns (score_or_None, payload). score None == N/A for the whole rubric."""
    prompt = build_prompt(rubric, diff)
    ids = {c["id"] for c in rubric["criteria"]}
    last_err = None
    for attempt in (1, 2):  # malformed -> retry ONCE, then fail. Never N/A.
        raw = invoke_judge(prompt)
        try:
            data = extract_json(raw)
            got = {c["id"] for c in data.get("criteria", [])}
            missing = ids - got
            if missing:
                raise ValueError("missing criterion ids: " + ",".join(sorted(missing)))
            scored, na = [], []
            for c in data["criteria"]:
                if c["id"] not in ids:
                    continue
                if str(c.get("score")).upper() == "N/A":
                    na.append(c["id"])
                else:
                    s = float(c["score"])
                    if s < 1.0 and not c.get("citation"):
                        raise ValueError(
                            c["id"] + " scored " + str(s) + " with no file:line citation")
                    scored.append((c["id"], s, c.get("citation"), c.get("note")))
            if not scored:
                return None, {"gate": gate, "score": "N/A",
                              "reason": "every criterion N/A for this diff",
                              "criteria": data["criteria"], "attempt": attempt}
            wmap = {c["id"]: c["weight"] for c in rubric["criteria"]}
            total_w = sum(wmap[i] for i, _s, _c, _n in scored)
            final = sum(wmap[i] * s for i, s, _c, _n in scored) / total_w  # renormalised
            return final, {
                "gate": gate, "score": round(final, 4),
                "rubricVersion": rubric["rubricVersion"],
                "judgeModel": CFG["judge"]["model"],
                "naCriteria": na, "renormalisedFrom": round(total_w, 4),
                "criteria": data["criteria"], "attempt": attempt,
            }
        except Exception as exc:
            last_err = str(exc)
            (EV / "judge").mkdir(parents=True, exist_ok=True)
            (EV / "judge" / (gate + "-raw-attempt" + str(attempt) + ".txt")).write_text(
                raw, encoding="utf-8")
    raise SystemExit("ERROR: " + gate + " judge response unusable after 2 attempts: "
                     + str(last_err) + " (ERROR, never N/A)")


def main():
    if len(sys.argv) < 2:
        print("usage: run_evals.py <base-ref>", file=sys.stderr)
        return 2
    base = sys.argv[1]
    (EV / "judge").mkdir(parents=True, exist_ok=True)
    (ROOT / ".evals" / "_run").mkdir(parents=True, exist_ok=True)

    diff = get_diff(base)
    if not diff.strip():
        print("[run-evals] empty diff - nothing for the judge to score")

    gates, failed = {}, []

    static_path = EV / "static-evals.json"
    if static_path.exists():
        st = json.loads(static_path.read_text(encoding="utf-8"))
        for g, v in st["gates"].items():
            gates[g] = {"status": v["status"], "detail": v["detail"]}
            if v["status"] == "FAIL":
                failed.append(g)
    else:
        print("[run-evals] WARNING: no static-evals.json - run run-static-evals first")

    for gate, name, fname, th_key in RUBRICS:
        rubric = json.loads((ROOT / ".evals/rubrics" / fname).read_text(encoding="utf-8"))
        minimum = TH[th_key]
        print("[run-evals] scoring " + gate + " (" + name + ") ...")
        score, payload = score_rubric(gate, rubric, diff)
        (EV / "judge" / (name + "-score.json")).write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        if score is None:
            gates[gate] = {"status": "N/A", "detail": payload["reason"]}
            print("  [N/A ] " + gate + "  " + payload["reason"])
            continue
        ok = score >= minimum
        gates[gate] = {"status": "PASS" if ok else "FAIL",
                       "detail": "score " + str(round(score, 4))
                                 + " vs min " + str(minimum)}
        print("  [" + ("OK  " if ok else "FAIL") + "] " + gate + "  score="
              + str(round(score, 4)) + "  min=" + str(minimum))
        if not ok:
            failed.append(gate)
            for c in payload["criteria"]:
                if str(c.get("score")).upper() != "N/A" and float(c["score"]) < 1.0:
                    print("       " + c["id"] + "=" + str(c["score"])
                          + "  " + str(c.get("citation")) + "  " + str(c.get("note"))[:70])

    verdict = "FAIL" if failed else "PASS"
    payload = {"evalKey": KEY, "base": base, "gates": gates,
               "overall": {"verdict": verdict, "checksRun": len(gates),
                           "checksTotal": len(gates), "failed": failed}}
    (EV / "eval.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = ["# Eval Scorecard - " + KEY, "", "**Verdict: " + verdict + "**", "",
             "| Gate | Status | Detail |", "|---|---|---|"]
    for g, v in gates.items():
        icon = {"PASS": "PASS", "FAIL": "**FAIL**", "N/A": "N/A"}[v["status"]]
        lines.append("| " + g + " | " + icon + " | " + v["detail"] + " |")
    (EV / "eval-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (ROOT / ".evals" / "_run" / "failed-gates.txt").write_text(
        "\n".join(failed) + ("\n" if failed else ""), encoding="utf-8")
    print("[run-evals] verdict=" + verdict + "  failed=" + (str(failed) if failed else "none"))
    print("[run-evals] eval.json -> " + str(EV / "eval.json"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
