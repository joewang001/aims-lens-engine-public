#!/usr/bin/env python3
"""Validate and submit routine public-lens changes through the automation PR."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

REPOSITORY = "joewang001/aims-lens-engine-public"
BRANCH = "automation/public-lens-source-agent"
ALLOWED_REMOTES = {
    f"git@github.com:{REPOSITORY}.git",
    f"https://github.com/{REPOSITORY}.git",
    f"https://github.com/{REPOSITORY}",
}
ROOT = Path(__file__).resolve().parents[1]


def validate_paths(paths):
    for name in paths:
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe changed path: {name}")
        if not (name.startswith(("company_lenses/", "docs/refresh-candidates/"))
                or name in {"public_manifest.yaml", "tests/test_public_lens_operations.py"}):
            raise ValueError(f"requires a maintainer PR outside routine lens scope: {name}")
        # A newly staged link must not escape the public checkout when tools read it.
        if (ROOT / name).is_symlink():
            raise ValueError(f"symlink changes require maintainer review: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", required=True, help="Commit description of the public-source change.")
    args = parser.parse_args()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TZ="America/Toronto")

    def git(*arguments, check=True):
        return subprocess.run(["git", *arguments], cwd=ROOT, env=env, check=check,
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def run(*arguments):
        subprocess.run([sys.executable, *arguments], cwd=ROOT, env=env, check=True)

    if Path(git("rev-parse", "--show-toplevel").stdout.strip()).resolve() != ROOT:
        raise ValueError("run from the dedicated public repository, not a parent backup repository")
    remotes = git("remote", "get-url", "--all", "--push", "origin").stdout.splitlines()
    if len(remotes) != 1 or remotes[0] not in ALLOWED_REMOTES:
        raise ValueError("origin must have exactly one push URL for the approved public repository")
    if git("branch", "--show-current").stdout.strip() in {"", "main", "master"}:
        raise ValueError("switch to a named work branch before publishing; main is never pushed")
    git("fetch", "--prune", "origin")
    if git("merge-base", "--is-ancestor", "origin/main", "HEAD", check=False).returncode:
        raise ValueError("main advanced: preserve work and rebase/merge before publishing")
    remote = f"refs/remotes/origin/{BRANCH}"
    if git("show-ref", "--verify", "--quiet", remote, check=False).returncode == 0:
        if git("merge-base", "--is-ancestor", remote, "origin/main", check=False).returncode:
            raise ValueError("an automation branch is pending; refusing to overwrite it")

    def changed():
        tracked = git("diff", "--name-only", "-z", "origin/main").stdout.split("\0")
        others = git("ls-files", "--others", "--exclude-standard", "-z").stdout.split("\0")
        return sorted(set(filter(None, tracked + others)))

    paths = changed()
    validate_paths(paths)
    if not paths:
        print(json.dumps({"status": "no_changes"}))
        return 0
    run("tools/public_lens_operations.py", "audit-gaps", "--catalog-reserve-target", "8")
    run("-m", "unittest", "discover", "-s", "tests", "-q")
    run("tools/scan_public_export.py", "--allowlist")
    run("tools/validate_public_lens_coverage.py", "--min-companies", "12")
    paths = changed()
    validate_paths(paths)
    git("diff", "--check")
    git("add", "--", *paths)
    if git("diff", "--cached", "--quiet", check=False).returncode:
        git("commit", "-m", args.message)
    head = git("rev-parse", "HEAD").stdout.strip()
    # Never force push or target main. GitHub validates this exact SHA before merging.
    pushed = git("push", "origin", f"HEAD:refs/heads/{BRANCH}")
    print(pushed.stderr.strip(), flush=True)
    print(json.dumps({"status": "submitted", "head": head, "branch": BRANCH,
                      "repository": REPOSITORY, "merge": "pending_GitHub_checks"}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"public_lens_publish_failed: {exc}", file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(exc.stderr, file=sys.stderr)
        sys.exit(1)
