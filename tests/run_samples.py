"""Run every skill's "Try it" commands on its made-up sample data. Run from the repo root: python3 tests/run_samples.py"""
import pathlib, re, shlex, shutil, subprocess, sys, tempfile

root = pathlib.Path(__file__).resolve().parent.parent
failed = 0
for readme in sorted(root.glob("skills/*/*/README.md")):
    m = re.search(r"## Try it.*?```\n(.*?)```", readme.read_text(encoding="utf-8"), re.S)
    if not m:
        continue
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / readme.parent.name
        shutil.copytree(readme.parent, work)
        for line in [l for l in m.group(1).splitlines() if l.strip()]:
            args = shlex.split(line)
            args[0] = sys.executable
            r = subprocess.run(args, cwd=work, capture_output=True, text=True)
            ok = r.returncode == 0
            failed += not ok
            print(("PASS" if ok else "FAIL"), readme.parent.name, "|", line)
            if not ok:
                print(r.stdout[-800:], r.stderr[-800:])
print(f"{failed} failed")
sys.exit(1 if failed else 0)
