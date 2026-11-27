"""Contract test for skills: run with `python3 tests/check_skills.py` from the repo root."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
errors = []
if (root / "SKILL.md").exists():
    errors.append("SKILL.md must not be at the repo root")
skills = sorted(root.glob("skills/*/*/SKILL.md"))
if not skills:
    errors.append("no skills found under skills/<category>/<name>/SKILL.md")
for path in skills:
    rel = path.relative_to(root)
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{rel}: missing frontmatter"); continue
    fm = m.group(1)
    name = re.search(r"^name: (.+)$", fm, re.M)
    desc = re.search(r"^description: (.+)$", fm, re.M)
    folder = path.parent.name
    if not name or name.group(1).strip() != folder:
        errors.append(f"{rel}: name must equal folder name '{folder}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", folder) or len(folder) > 64:
        errors.append(f"{rel}: folder name must be lowercase letters, digits and hyphens, max 64")
    if not desc:
        errors.append(f"{rel}: missing description")
    elif len(desc.group(1).strip()) > 160:
        errors.append(f"{rel}: description is {len(desc.group(1).strip())} chars, max 160")
    if not re.search(r"^license: MIT$", fm, re.M):
        errors.append(f"{rel}: license must be MIT")
    cat = re.search(r"^  category: (.+)$", fm, re.M)
    if not cat or cat.group(1).strip() != path.parent.parent.name:
        errors.append(f"{rel}: metadata.category must equal parent folder")
    if len(text.splitlines()) > 500:
        errors.append(f"{rel}: over 500 lines")
    if re.search(r"\bact_\d{6,}\b", text):
        errors.append(f"{rel}: looks like a real ad account ID")
canon = root / "shared" / "store.py"
for copy in root.glob("skills/*/*/scripts/store.py"):
    if canon.exists() and copy.read_bytes() != canon.read_bytes():
        errors.append(f"{copy.relative_to(root)}: differs from shared/store.py (copy it again)")
for env in root.rglob(".env"):
    errors.append(f"{env.relative_to(root)}: .env files must never be committed")
for db in root.rglob("*.db"):
    errors.append(f"{db.relative_to(root)}: database files must never be committed")
secret_patterns = [(r"EAA[A-Za-z0-9]{30,}", "looks like a Meta access token"),
                   (r"\bact_\d{6,}\b", "looks like a real ad account ID"),
                   (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key")]
for f in root.rglob("*"):
    if not f.is_file() or ".git" in f.parts or "node_modules" in f.parts or f.suffix not in {".md", ".py", ".csv", ".json", ".ts", ".mjs", ".jsonc", ".yml", ".txt"}:
        continue
    text = f.read_text(encoding="utf-8", errors="ignore")
    for pat, why in secret_patterns:
        if re.search(pat, text) and f.name != "check_skills.py":
            errors.append(f"{f.relative_to(root)}: {why}")
for e in errors:
    print("FAIL", e)
print(f"{len(skills)} skills checked, {len(errors)} problems")
sys.exit(1 if errors else 0)
