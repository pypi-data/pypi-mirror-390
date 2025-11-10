#!/usr/bin/env python3
"""
setup_functional_test.py
========================

Summary
-------
Prepares the directory structure and driver script for a functional test
associated with a specific `test-case-XXX` directory.  The program creates
the `scripts/` subdirectory (if missing) and generates a small shell script
(`run_functional_test.sh`) that executes the provided or prompted primary
executable.  A concise execution report is written to the output directory.

Compliance
----------
Implements:
- CLP1 : Command-line Parameters
- LOG1 / LOG2 : Logging behavior
- GG2 : Standard output behavior (absolute path to report file)
- EXC1 : Controlled exit codes
- VAL1 : Validation of test-case-XXX directory naming
- SET1 : Functional test setup logic
- REP1 : Report generation summarizing results

Usage
-----
python setup_functional_test.py
--test-case-dir <path>
[--primary-executable <file>]
[--outdir <dir>]
[--logfile <file>]
"""

from __future__ import annotations

import getpass
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def setup_logging(logfile: Path) -> logging.Logger:
    """Configure logging such that INFO+ goes to file and WARNING+ goes to stderr.

    Args:
        logfile: Path to the log file.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("setup_functional_test")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fmt = logging.Formatter("%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(stream=sys.stderr)
    sh.setLevel(logging.WARNING)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def validate_test_case_dir(path: Path) -> None:
    """Validate that the directory name follows the test-case-XXX pattern.

    Args:
        path: Path to the test case directory.

    Raises:
        BadParameter: If the directory name does not match required format.
    """
    if not path.is_dir():
        raise typer.BadParameter(f"Not a directory: {path}")
    name = path.name
    if not name.startswith("test-case-"):
        raise typer.BadParameter("Directory name must start with 'test-case-'.")
    suffix = name.replace("test-case-", "")
    if not suffix.isdigit() or len(suffix) != 3 or suffix == "000":
        raise typer.BadParameter("Basename must end with a three-digit integer 001..999.")


def default_outdir(progname: str) -> Path:
    """Construct default output directory under /tmp/<user>/<progname>/<timestamp>.

    Args:
        progname: Name of the running program, used as the subdirectory.

    Returns:
        Path to the newly constructed output directory.
    """
    user = getpass.getuser()
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return Path(f"/tmp/{user}/{progname}/{ts}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    test_case_dir: Path = typer.Option(
        ...,
        "--test-case-dir",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Path to the test case directory (must be named test-case-XXX).",
    ),
    primary_executable: Optional[Path] = typer.Option(
        None,
        "--primary-executable",
        help="Optional path to the primary executable. If omitted, user will be prompted.",
    ),
    outdir: Path = typer.Option(
        default_outdir(Path(__file__).stem),
        "--outdir",
        help="Where to write logs/report. Defaults to /tmp/[user]/<progname>/<timestamp>.",
    ),
    logfile: Optional[Path] = typer.Option(
        None,
        "--logfile",
        help="Optional logfile path. Defaults to <outdir>/<progname>.log.",
    ),
):
    """Prepare scripts/ folder and driver script for functional testing.

    Args:
        test_case_dir: Path to the test-case-XXX directory.
        primary_executable: Path to the primary executable to run.
        outdir: Directory to write logs and report.
        logfile: Optional path to the logfile.

    Raises:
        Exit: On validation or setup failure.
    """
    validate_test_case_dir(test_case_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    final_log = logfile if logfile else outdir / f"{Path(__file__).stem}.log"
    logger = setup_logging(final_log)

    # Prompt for executable if missing
    if primary_executable is None:
        response = input("Enter path to primary executable: ").strip()
        primary_executable = Path(response)

    if not primary_executable.exists():
        typer.secho(f"Error: primary executable not found: {primary_executable}", err=True)
        raise typer.Exit(code=2)

    logger.info("Setting up functional test environment for: %s", test_case_dir)
    scripts_dir = test_case_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    run_script = scripts_dir / "run_functional_test.sh"
    script_content = f"""#!/usr/bin/env bash
# Auto-generated by setup_functional_test.py
set -e
echo "Running functional test..."
"{primary_executable}" "$@"
"""
    run_script.write_text(script_content, encoding="utf-8")
    run_script.chmod(0o755)
    logger.info("Generated driver script: %s", run_script)

    # Prepare report
    report_path = outdir / "report.txt"
    report_content = "\n".join(
        [
            f"Program: {Path(__file__).stem}",
            f"Test case dir: {test_case_dir}",
            f"Executable: {primary_executable.resolve()}",
            f"Driver script: {run_script.resolve()}",
            f"Log: {final_log.resolve()}",
        ]
    )
    report_path.write_text(report_content + "\n", encoding="utf-8")
    logger.info("Report written: %s", report_path)

    # GG2: print absolute path to report file
    print(str(report_path.resolve()))

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
