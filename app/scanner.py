import os
import re
from typing import List, Dict

SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "aws_access_key"),
    (r"(?i)api[_-]?key\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]", "generic_api_key"),
    (r"-----BEGIN (?:RSA|DSA|EC) PRIVATE KEY-----", "private_key_block"),
]

DEP_FILE_HINTS = ["requirements.txt", "pyproject.toml", "package.json", "pom.xml", "build.gradle", "go.mod"]

def find_secrets(diff: str) -> List[str]:
    hits = []
    for pat, name in SECRET_PATTERNS:
        if re.search(pat, diff):
            hits.append(name)
    return list(sorted(set(hits)))

def find_dep_risks(diff: str) -> List[str]:
    risks = []
    # naive version check: -requests==2.31.0 +requests==2.20.0
    m = re.findall(r"-\s*([A-Za-z0-9_\-]+)==([0-9][0-9A-Za-z\.\-\+]*)\s*\n\+\s*\1==([0-9][0-9A-Za-z\.\-\+]*)", diff)
    for pkg, old, new in m:
        if version_lower(new, old):
            risks.append(f"dependency_downgrade:{pkg}:{old}->{new}")
    # file hints
    if any(f in diff for f in DEP_FILE_HINTS):
        risks.append("dependency_file_modified")
    return list(sorted(set(risks)))

def version_lower(a: str, b: str) -> bool:
    def parts(v): return [int(x) if x.isdigit() else x for x in re.split(r'[.\-+]', v)]
    return parts(a) < parts(b)

def find_missing_tests(diff: str) -> List[str]:
    touched_code = re.findall(r"^\+\s*(def |class |function |public |private )", diff, re.MULTILINE)
    tests_touched = re.search(r"tests?/|test_", diff, re.IGNORECASE)
    if touched_code and not tests_touched:
        return ["code_changed_no_tests_changed"]
    return []

def llm_enrich(findings: List[str]) -> List[str] | None:
    if not os.getenv("OPENAI_API_KEY"):
        return None
    tips = [
        "Explain risk context and suggest remediation steps.",
        "Auto-generate a PR comment summarizing findings.",
    ]
    return list(dict.fromkeys(findings + tips))

def scan_diff(repo: str, diff: str) -> Dict:
    findings = []
    secrets = find_secrets(diff)
    if secrets:
        findings.append(f"secrets:{','.join(secrets)}")

    deps = find_dep_risks(diff)
    findings.extend(deps)

    tests = find_missing_tests(diff)
    findings.extend(tests)

    suggestions = []
    if secrets:
        suggestions.append("Remove secret and rotate credentials immediately; add secret scanning pre-commit.")
    if any(f.startswith("dependency_downgrade") for f in findings):
        suggestions.append("Reconsider dependency downgrade; document justification or pin via lockfile.")
    if "dependency_file_modified" in findings:
        suggestions.append("Run full dependency audit; verify SBOM/licensing if applicable.")
    if "code_changed_no_tests_changed" in findings:
        suggestions.append("Add/expand tests for changed code paths; enforce via coverage gate.")

    enriched = llm_enrich(suggestions)

    return {
        "repo": repo,
        "findings": list(dict.fromkeys(findings)),
        "suggestions": enriched or suggestions,
        "llm_enriched": enriched is not None,
    }
