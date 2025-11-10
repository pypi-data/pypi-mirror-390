#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

try:
  import libconf
except ImportError:
  libconf = None


def lint_with_libconf(path: Path):
  print("handleing", path)
  try:
    with open(path, encoding="utf-8") as f:
      libconf.load(f)
    return []
  except libconf.ConfigError as e:
    return [f"Parse error: {e}"]
  except Exception as e:
    return [f"Unexpected error: {e}"]


def lint_file(path: Path):
  issues = []
  if not libconf:
    issues.append("libconf not installed, cannot parse syntax precisely.")
  else:
    issues += lint_with_libconf(path)

  if issues:
    print(f"\nFile: {path}")
    for issue in issues:
      print(f"  - {issue}")


def main():
  parser = argparse.ArgumentParser(description="Libconfig syntax checker using libconf")
  parser.add_argument("target", help="File or directory to check")
  parser.add_argument("-r", "--recursive", action="store_true", help="Recursively check directories")
  args = parser.parse_args()

  target = Path(args.target)
  if not target.exists():
    print(f"Error: path not found: {target}")
    sys.exit(1)

  files = []
  if target.is_file():
    files = [target]
  elif args.recursive:
    files = [f for f in target.rglob("*") if f.suffix in (".cfg", ".conf", ".config")]
  else:
    files = [f for f in target.glob("*") if f.suffix in (".cfg", ".conf", ".config")]

  for f in files:
    lint_file(f)


if __name__ == "__main__":
  main()
