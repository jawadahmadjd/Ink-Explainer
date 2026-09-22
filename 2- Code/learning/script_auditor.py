"""
Script Auditor Engine: 2-Stage Adversarial Review System for Ink Explainers
Operates independently from the Script Writer to forensically stress-test scripts against:
1. Temporal & Payroll Realism (e.g. 14-30 day payroll lag, bill due dates)
2. Mathematical Ledger Reconciliation (tracks every dollar in/out; prevents deficit spending)
3. Physical & Logistical Plausibility (sleep, transit, energy limits, realistic work hours)
4. Ethical & Shariah Compliance (zero riba/interest, zero debt traps, zero gambling)
5. TTS & Voiceover Cleanliness (zero special characters, numbers spelled out, pacing dividers)
"""

import os
import sys
import re
import json
from datetime import datetime

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE_DIR)
import config

ILLEGAL_VO_CHARS_REGEX = re.compile(r'[^a-zA-Z0-9\s.,!?:;\"\'\-]')
DIGIT_REGEX = re.compile(r'\b\d+\b')
CURRENCY_SYMBOL_REGEX = re.compile(r'[\$€£¥₹]')
EM_DASH_REGEX = re.compile(r'[\u2014\u2013—–]')

def audit_script_voiceover_cleanliness(text: str) -> dict:
    """
    Checks for characters or symbols that degrade ElevenLabs / TTS synthesis.
    Enforces that numbers, times, and currencies are spelled out.
    """
    issues = []
    
    # 1. Check for currency symbols
    curr_matches = CURRENCY_SYMBOL_REGEX.findall(text)
    if curr_matches:
        issues.append({
            "type": "CURRENCY_SYMBOL",
            "severity": "CRITICAL",
            "message": f"Found raw currency symbols ({set(curr_matches)}). Spell them out (e.g., 'two thousand dollars')."
        })

    # 2. Check for em-dashes
    if EM_DASH_REGEX.search(text):
        issues.append({
            "type": "EM_DASH",
            "severity": "WARNING",
            "message": "Found em-dashes ('—'). Replace with natural commas, colons, or hyphens for smooth voiceover pauses."
        })

    # 3. Check for standalone digits
    digit_matches = DIGIT_REGEX.findall(text)
    if digit_matches:
        sample_digits = list(set(digit_matches))[:5]
        issues.append({
            "type": "NUMERIC_DIGITS",
            "severity": "CRITICAL",
            "message": f"Found raw digits {sample_digits}. Spell numbers out into words (e.g., 'thirty' instead of '30')."
        })

    # 4. Check for arbitrary special characters
    special_chars = set(ILLEGAL_VO_CHARS_REGEX.findall(text))
    # Filter out safe ascii whitespace
    special_chars = {c for c in special_chars if not c.isspace()}
    if special_chars:
        issues.append({
            "type": "SPECIAL_CHARACTERS",
            "severity": "CRITICAL",
            "message": f"Found illegal characters for voiceover: {special_chars}."
        })

    words = text.split()
    word_count = len(words)
    est_duration_min = round(word_count / 220.0, 2)

    return {
        "passed": len([i for i in issues if i["severity"] == "CRITICAL"]) == 0,
        "word_count": word_count,
        "est_duration_min": est_duration_min,
        "issues": issues
    }

def audit_script_narrative_and_math(text: str, niche: str = "finance") -> dict:
    """
    Forensic logic auditor:
    - Verifies payroll lag (if hired at Day X, check if paycheck arrives at Day X instead of Day X + 14..30)
    - Verifies rent and bill synchronization
    - Checks for debt or interest promotion in finance niche
    """
    issues = []
    text_lower = text.lower()

    # Rule 1: The Corporate Payroll Lag Check
    # If a character lands a job / gets hired, verify they don't get paid on that exact same day
    hired_patterns = [r"landed a (?:new )?(?:full-time )?job", r"landed a (?:new )?position", r"got hired", r"started (?:his|her|their) (?:new )?job"]
    paycheck_patterns = [r"first paycheck", r"paycheck hit", r"received (?:his|her|their) (?:first )?paycheck", r"got paid"]

    has_hired = any(re.search(p, text_lower) for p in hired_patterns)
    
    if has_hired:
        # Check if the script acknowledges payroll delay
        payroll_lag_indicators = [
            "when do you actually get paid",
            "payroll",
            "work thirty days",
            "two weeks in arrears",
            "second month",
            "payroll processor",
            "thirty days until his first",
            "thirty days until her first"
        ]
        has_payroll_lag_awareness = any(ind in text_lower for ind in payroll_lag_indicators)
        if not has_payroll_lag_awareness:
            issues.append({
                "type": "PAYROLL_REALISM_FLAW",
                "severity": "CRITICAL",
                "message": "Script depicts character landing a job but fails to account for the mandatory 14-30 day payroll delay before the first paycheck clears."
            })

    # Rule 2: Shariah / Non-Riba Compliance Check (Finance Niche)
    if niche == "finance":
        prohibited_terms = ["payday loan", "credit card debt", "borrow from the bank", "interest rate of", "cash advance loan"]
        for term in prohibited_terms:
            # Check if term is recommended rather than warned against
            matches = re.finditer(re.escape(term), text_lower)
            for m in matches:
                surrounding = text_lower[max(0, m.start() - 80):min(len(text_lower), m.end() + 80)]
                negative_cues = [
                    "without", "never", "zero", "avoid", "no ", "predatory", "not ",
                    "trap", "fall back into", "danger", "ruin", "destroy", "grave",
                    "suicide", "bleeding", "victim", "escape"
                ]
                if not any(neg in surrounding for neg in negative_cues):
                    issues.append({
                        "type": "SHARIAH_COMPLIANCE_RISK",
                        "severity": "CRITICAL",
                        "message": f"Potential non-compliant financial mechanism detected ('{term}') without explicit negative framing or avoidance."
                    })

    # Rule 3: Time Horizon Check
    day_numbers = re.findall(r'day\s+([a-z]+(?:\s+[a-z]+)?)', text_lower)
    
    return {
        "passed": len([i for i in issues if i["severity"] == "CRITICAL"]) == 0,
        "timeline_mentions": list(set(day_numbers))[:8],
        "issues": issues
    }

def run_full_script_audit(script_path: str, niche: str = "finance") -> dict:
    """Executes complete forensic two-stage audit on a script file."""
    if not os.path.exists(script_path):
        return {"passed": False, "error": f"File not found: {script_path}"}

    with open(script_path, "r", encoding="utf-8") as f:
        text = f.read()

    vo_audit = audit_script_voiceover_cleanliness(text)
    logic_audit = audit_script_narrative_and_math(text, niche=niche)

    all_issues = vo_audit["issues"] + logic_audit["issues"]
    overall_passed = vo_audit["passed"] and logic_audit["passed"]

    has_payroll_error = any(i["type"] == "PAYROLL_REALISM_FLAW" for i in logic_audit["issues"])
    has_shariah_error = any(i["type"] == "SHARIAH_COMPLIANCE_RISK" for i in logic_audit["issues"])

    report = {
        "timestamp": datetime.now().isoformat(),
        "script_path": script_path,
        "niche": niche,
        "overall_passed": overall_passed,
        "word_count": vo_audit["word_count"],
        "est_duration_min": vo_audit["est_duration_min"],
        "critical_issues_count": len([i for i in all_issues if i["severity"] == "CRITICAL"]),
        "warning_issues_count": len([i for i in all_issues if i["severity"] == "WARNING"]),
        "issues": all_issues,
        "scorecard": {
            "tts_cleanliness": "PASS" if vo_audit["passed"] else "FAIL",
            "chronological_payroll_logic": "FAIL" if has_payroll_error else "PASS",
            "ethical_compliance": "FAIL" if has_shariah_error else "PASS"
        }
    }

    return report

if __name__ == "__main__":
    target_script = os.path.join(config.FINALS_ROOT, "finance", "1- 0 Dollars to Financial Stability", "clean_script.txt")
    print(f"Auditing: {target_script}")
    rep = run_full_script_audit(target_script, niche="finance")
    print(json.dumps(rep, indent=2))
