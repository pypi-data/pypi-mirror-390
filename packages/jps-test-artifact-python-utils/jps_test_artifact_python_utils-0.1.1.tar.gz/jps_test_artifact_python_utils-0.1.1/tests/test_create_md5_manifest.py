from pathlib import Path

from typer.testing import CliRunner

from src.jps_test_artifact_python_utils import create_md5_manifest

runner = CliRunner()


def test_create_md5_manifest_basic(tmp_path):
    """Test that manifest and report files are created successfully.

    Args:
        tmp_path: Temporary directory provided by pytest.
    """
    # Arrange
    test_case = tmp_path / "test-case-001"
    (test_case / "inputs").mkdir(parents=True)
    dummy_file = test_case / "inputs" / "dummy.txt"
    dummy_file.write_text("sample data")
    scripts_dir = test_case / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Act
    result = runner.invoke(create_md5_manifest.app, ["--test-case-dir", str(test_case)])

    # Assert
    assert result.exit_code == 0
    report_path = Path(result.stdout.strip())
    assert report_path.exists(), "Report file must exist"
    manifest = test_case / "scripts" / "md5_manifest.txt"
    assert manifest.exists(), "Manifest file should be created"
    content = manifest.read_text()
    assert "## method-created:" in content
    assert str(dummy_file) in content
