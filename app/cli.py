import argparse, sys
from .scanner import scan_diff

def main():
    parser = argparse.ArgumentParser(description="CI/CD Guardrails scanner")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--diff", required=False, help="Diff text; if omitted, read from stdin")
    args = parser.parse_args()

    diff = args.diff if args.diff is not None else sys.stdin.read()
    result = scan_diff(args.repo, diff)
    print(result)

if __name__ == "__main__":
    main()
