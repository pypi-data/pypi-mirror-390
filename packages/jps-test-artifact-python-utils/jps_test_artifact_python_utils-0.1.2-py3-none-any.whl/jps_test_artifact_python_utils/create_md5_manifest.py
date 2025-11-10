#!/usr/bin/env python3
"""
create_md5_manifest.py
======================

Summary
-------
Generates an MD5 manifest (`scripts/md5_manifest.txt`) for all files within
a test case directory (`test-case-XXX`). Each entry includes absolute file
path, MD5 checksum, file size, and timestamp. A concise execution report is
written to the output directory.

Compliance
----------
Implements the following SRS requirements:

- CLP1 : Command-line Parameters
- LOG1 / LOG2 : Logging behavior
- GG2 : Standard output behavior (absolute path to report file)
- EXC1 : Exception handling and controlled exit codes
- VAL1 : Validation of directory naming convention (test-case-XXX)
- GEN1 : Manifest generation logic (absolute paths, MD5, bytes, timestamp)
- REP1 : Report creation summarizing results and file counts

Usage
-----
$ python create_md5_manifest.py --test-case-dir <path> [--outdir <dir>] [--logfile <file>]

References
----------
SRS: jps-test-artifact-python-utils create_md5_manifest.py SRS v1.0.0
"""

from __future__ import annotations

import getpass
import hashlib
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List

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
    logger = logging.getLogger("create_md5_manifest")
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


def iter_files(root: Path, exclude: Path | None = None):
    """Yield all files under a root directory, optionally excluding one path.

    Args:
        root: The root directory to search recursively for files.
        exclude: An optional path to exclude from results (such as the manifest file).

    Yields:
        Path objects for each discovered file under `root` except the excluded path.
    """
    for p in root.rglob("*"):
        if p.is_file() and (exclude is None or p.resolve() != exclude.resolve()):
            yield p


def compute_md5(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute MD5 checksum for a file.

    Args:
        file_path: File to compute checksum for.
        chunk_size: Bytes to read per iteration (default 1MB).

    Returns:
        Hexadecimal MD5 digest string.
    """
    h = hashlib.md5()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


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
    outdir: Path = typer.Option(
        default_outdir(Path(__file__).stem),
        "--outdir",
        help="Where to write logs/report. Defaults to /tmp/[user]/<progname>/<timestamp>.",
    ),
    logfile: Path = typer.Option(
        None,
        "--logfile",
        help="Optional logfile path. Defaults to <outdir>/<progname>.log.",
    ),
):
    """Generate MD5 manifest and concise execution report.

    Implements CLP1, LOG1/LOG2, GG2, VAL1, GEN1, and REP1 from SRS.

    Args:
        test_case_dir: Path to the test case directory.
        outdir: Output directory for logs and reports.
        logfile: Optional logfile override.

    Raises:
        Exit: On validation or write failure.
    """
    validate_test_case_dir(test_case_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    final_log = logfile if logfile else outdir / f"{Path(__file__).stem}.log"
    logger = setup_logging(final_log)

    logger.info("Starting MD5 manifest generation.")
    scripts_dir = test_case_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = scripts_dir / "md5_manifest.txt"

    if manifest_path.exists():
        typer.secho(f"Manifest already exists: {manifest_path}", err=True)
        raise typer.Exit(code=1)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    files: List[Path] = list(iter_files(test_case_dir, exclude=manifest_path))
    manifest_lines = []

    for f in files:
        md5sum = compute_md5(f)
        num_bytes = f.stat().st_size
        manifest_lines.append(f"{f.resolve()}\t{md5sum}\t{num_bytes}\t{timestamp}")

    header = [
        f"## method-created: {Path(__file__).resolve()}",
        f"## date-created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"## created-by: {getpass.getuser()}",
        "## Columns:",
        "## 1: absolute file path",
        "## 2: md5sum",
        "## 3: number of bytes",
        "## 4: date/time md5sum was derived",
        "",
    ]
    manifest_path.write_text("\n".join(header + manifest_lines) + "\n", encoding="utf-8")
    logger.info("Manifest written: %s", manifest_path)

    report_path = outdir / "report.txt"
    report_content = "\n".join(
        [
            f"Program: {Path(__file__).stem}",
            f"Test case dir: {test_case_dir}",
            f"Files processed: {len(files)}",
            f"Manifest: {manifest_path.resolve()}",
            f"Log: {final_log.resolve()}",
        ]
    )
    report_path.write_text(report_content + "\n", encoding="utf-8")
    logger.info("Report written: %s", report_path)

    # GG2: print report path to stdout
    print(str(report_path.resolve()))


if __name__ == "__main__":
    app()
