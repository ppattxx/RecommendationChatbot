"""Run web parity experiment suite in one command.

This script executes, in order:
1. generate_test_cases.py
2. generate_query_trial_table.py
3. test_query_evaluator.py

By default it runs in WEB_API_MODE=live against WEB_API_BASE_URL=http://localhost:5500
so outputs mirror the same backend used by the frontend.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_step(step_name: str, script_path: Path, env: dict) -> int:
    print("\n" + "=" * 100)
    print(f"STEP: {step_name}")
    print(f"SCRIPT: {script_path}")
    print("=" * 100)

    process = subprocess.run([sys.executable, str(script_path)], env=env)
    if process.returncode != 0:
        print(f"\n[FAIL] {step_name} failed with exit code {process.returncode}")
    else:
        print(f"\n[PASS] {step_name} completed")
    return process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run FE/BE web parity suite for experiment scripts.")
    parser.add_argument(
        "--mode",
        default=os.getenv("WEB_API_MODE", "live"),
        choices=["live", "local", "auto"],
        help="Pipeline mode: live (recommended), local, or auto",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("WEB_API_BASE_URL", "http://localhost:5500"),
        help="Backend base URL for live mode",
    )
    args = parser.parse_args()

    tests_dir = Path(__file__).parent

    env = os.environ.copy()
    env["WEB_API_MODE"] = args.mode
    env["WEB_API_BASE_URL"] = args.base_url

    print("\nWEB PARITY SUITE CONFIG")
    print(f"- WEB_API_MODE={env['WEB_API_MODE']}")
    print(f"- WEB_API_BASE_URL={env['WEB_API_BASE_URL']}")

    steps = [
        ("Generate Test Cases", tests_dir / "generate_test_cases.py"),
        ("Generate Query Trial Table", tests_dir / "generate_query_trial_table.py"),
        ("Evaluate Query Cases", tests_dir / "test_query_evaluator.py"),
    ]

    for step_name, script_path in steps:
        code = run_step(step_name, script_path, env)
        if code != 0:
            print("\nSUITE STATUS: FAILED")
            return code

    print("\n" + "=" * 100)
    print("SUITE STATUS: PASS")
    print("All scripts are aligned to web pipeline and completed successfully.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
