from pathlib import Path

from typer.testing import CliRunner

from src.jps_test_artifact_python_utils import verify_md5_manifest

runner = CliRunner()


def test_verify_md5_manifest_success(tmp_path):
    """Verify correct behavior when all manifest entries match actual MD5s.

    Args:
        tmp_path: Temporary directory provided by pytest.
    """
    # Arrange
    test_case = tmp_path / "test-case-001"
    scripts_dir = test_case / "scripts"
    scripts_dir.mkdir(parents=True)
    dummy_file = test_case / "dummy.txt"
    dummy_file.write_text("data")

    import hashlib

    md5 = hashlib.md5("data".encode()).hexdigest()
    manifest_path = scripts_dir / "md5_manifest.txt"
    manifest_path.write_text(f"{dummy_file.resolve()}\t{md5}\t4\t2025-01-01-00:00:00\n")

    # Act
    result = runner.invoke(verify_md5_manifest.app, ["--test-case-dir", str(test_case)])

    # Assert
    assert result.exit_code == 0
    report_path = Path(result.stdout.strip())
    assert report_path.exists(), "Report file must exist"
    content = report_path.read_text()
    assert "Verified files" in content
    assert "passed=" in content


def test_verify_md5_manifest_missing_file(tmp_path):
    """Verify behavior when manifest lists a missing file.

    Args:
        tmp_path: Temporary directory provided by pytest.
    """
    # Arrange
    test_case = tmp_path / "test-case-002"
    scripts_dir = test_case / "scripts"
    scripts_dir.mkdir(parents=True)
    fake_file = test_case / "ghost.txt"
    md5 = "abcd1234"
    manifest_path = scripts_dir / "md5_manifest.txt"
    manifest_path.write_text(f"{fake_file.resolve()}\t{md5}\t10\t2025-01-01-00:00:00\n")

    # Act
    result = runner.invoke(verify_md5_manifest.app, ["--test-case-dir", str(test_case)])

    # Assert
    assert result.exit_code == 3, "Should exit with code 3 for missing file"
    report_path = Path(result.stdout.strip())
    assert report_path.exists(), "Report file should be generated"
    content = report_path.read_text()
    assert "missing" in content.lower()


def test_verify_md5_manifest_failure(tmp_path):
    """Verify behavior when MD5 mismatch occurs.

    Args:
        tmp_path: Temporary directory provided by pytest.
    """
    # Arrange
    test_case = tmp_path / "test-case-003"
    scripts_dir = test_case / "scripts"
    scripts_dir.mkdir(parents=True)
    file_path = test_case / "file.txt"
    file_path.write_text("content")
    import hashlib

    bad_md5 = hashlib.md5("different".encode()).hexdigest()
    manifest_path = scripts_dir / "md5_manifest.txt"
    manifest_path.write_text(f"{file_path.resolve()}\t{bad_md5}\t7\t2025-01-01-00:00:00\n")

    # Act
    result = runner.invoke(verify_md5_manifest.app, ["--test-case-dir", str(test_case)])

    # Assert
    assert result.exit_code == 1, "MD5 mismatches should return exit code 1"
    report_path = Path(result.stdout.strip())
    assert report_path.exists()
    content = report_path.read_text()
    assert "Failures:" in content
    assert str(file_path) in content
