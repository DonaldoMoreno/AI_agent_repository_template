#!/usr/bin/env python3
"""Generate a patch based on logs using simple heuristics.

Heuristics implemented:
- Detect Python `ModuleNotFoundError` / `ImportError` and add missing modules
  to `requirements.txt` (create if missing).
- Detect missing C headers ("No such file or directory" for .h files) and
  create `.fixbot_system_deps.txt` listing the missing headers for maintainers.

The script still attempts to call OpenAI if `OPENAI_API_KEY` is present and
the `openai` package is installed; if that fails, heuristics are used as a
fallback. The generated output is a unified-diff patch suitable for `git apply`.
"""
import argparse
import os
import sys
import re
import difflib


def make_new_file_diff(path, relpath, new_lines):
    # When file doesn't exist, produce a diff against /dev/null
    header = ["--- /dev/null", f"+++ b/{relpath}", f"@@ -0,0 +1,{len(new_lines)} @@"]
    body = [("+" + line.rstrip("\n")) for line in new_lines]
    return "\n".join(header + body) + "\n"


def make_update_file_diff(path, relpath, old_lines, new_lines):
    ud = difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{relpath}", tofile=f"b/{relpath}", lineterm="")
    return "\n".join(list(ud)) + "\n"


def write_requirements_patch(out_path, repo_root, missing_modules):
    if not missing_modules:
        return False

    req_path = os.path.join(repo_root, "requirements.txt")
    rel = "requirements.txt"
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8", errors="ignore") as f:
            old = f.read().splitlines()
        added = [m for m in missing_modules if m not in [l.strip() for l in old]]
        if not added:
            return False
        new = old + added
        diff = make_update_file_diff(req_path, rel, old, new)
    else:
        new = missing_modules
        diff = make_new_file_diff(req_path, rel, new)

    with open(out_path, "a", encoding="utf-8") as o:
        o.write(diff)
    return True


def write_system_deps_patch(out_path, repo_root, missing_headers):
    if not missing_headers:
        return False
    rel = ".fixbot_system_deps.txt"
    lines = ["The following headers were reported missing during CI/compile:"] + missing_headers
    diff = make_new_file_diff(os.path.join(repo_root, rel), rel, lines)
    with open(out_path, "a", encoding="utf-8") as o:
        o.write(diff)
    return True


def heuristics_make_patch(logs_path, repo_root, out_path):
    with open(logs_path, "r", encoding="utf-8", errors="ignore") as f:
        logs = f.read()

    # Detect missing Python modules
    missing = set()
    for m in re.findall(r"ModuleNotFoundError: No module named '([A-Za-z0-9_]+)'", logs):
        missing.add(m.lower())
    for m in re.findall(r"ImportError: No module named ([A-Za-z0-9_]+)", logs):
        missing.add(m.lower())

    # Also detect pip errors referencing a package
    for m in re.findall(r"No matching distribution found for ([A-Za-z0-9_\-\.]+)", logs):
        missing.add(m.lower())

    missing_list = sorted(missing)

    # Detect missing headers
    missing_headers = []
    for hdr in re.findall(r"fatal error: ([A-Za-z0-9_\-\/]+\.h): No such file or directory", logs):
        if hdr not in missing_headers:
            missing_headers.append(hdr)

    # Build patch file (append modes so multiple changes are combined)
    # Remove output if exists so we write fresh
    if os.path.exists(out_path):
        os.remove(out_path)

    wrote_any = False
    wrote_any = write_requirements_patch(out_path, repo_root, missing_list) or wrote_any
    wrote_any = write_system_deps_patch(out_path, repo_root, missing_headers) or wrote_any

    if not wrote_any:
        # Fallback: create a placeholder notice file
        notice_lines = ["FixBot could not identify an automatic fix.", "See .fixbot_logs.txt for details."]
        diff = make_new_file_diff(None, ".fixbot_notice.txt", notice_lines)
        with open(out_path, "a", encoding="utf-8") as o:
            o.write(diff)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--logs", required=True)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    # Attempt OpenAI first (best-effort). If it fails, fall back to heuristics.
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            import openai
            openai.api_key = openai_key
            with open(args.logs, "r", encoding="utf-8", errors="ignore") as f:
                logs = f.read(8192)
            prompt = (
                "You are a tool that outputs a minimal unified-diff patch to fix CI failures. "
                "Output ONLY the patch.\n\nLogs:\n" + logs
            )
            try:
                # Use Completion API if available; caller may override.
                resp = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens=800)
                patch_text = resp.choices[0].text.strip()
                if patch_text:
                    with open(args.out, "w", encoding="utf-8") as o:
                        o.write(patch_text)
                    print("Wrote patch from OpenAI to", args.out)
                    return
            except Exception:
                pass
        except Exception:
            pass

    # Fallback heuristics
    heuristics_make_patch(args.logs, args.repo_root, args.out)
    print("Wrote heuristic patch to", args.out)


if __name__ == "__main__":
    main()
