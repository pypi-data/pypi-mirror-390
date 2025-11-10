from pathlib import Path

from typer.testing import CliRunner

from src.jps_test_artifact_python_utils import setup_functional_test

runner = CliRunner()


def test_setup_functional_test_with_executable(tmp_path):
    """Verify setup when --primary-executable is provided explicitly.

    Args:
        tmp_path: Temporary directory provided by pytest.
    """
    # Arrange
    test_case = tmp_path / "test-case-001"
    test_case.mkdir(parents=True)
    executable_path = test_case / "src" / "run_pipeline.py"
    executable_path.parent.mkdir(parents=True)
    executable_path.write_text("#!/usr/bin/env python3\nprint('hello world')\n")
    executable_path.chmod(0o755)

    # Act
    result = runner.invoke(
        setup_functional_test.app,
        [
            "--test-case-dir",
            str(test_case),
            "--primary-executable",
            str(executable_path),
        ],
    )

    # Assert
    assert result.exit_code == 0, f"Unexpected exit: {result.exit_code}, {result.stdout}"
    report_path = Path(result.stdout.strip())
    assert report_path.exists(), "Report file should exist"
    scripts_dir = test_case / "scripts"
    assert scripts_dir.exists(), "scripts/ directory must be created"
    generated_files = list(scripts_dir.iterdir())
    assert any(
        "run_functional_test" in f.name for f in generated_files
    ), "Expected a run script to be generated"


def test_setup_functional_test_prompts_for_executable(tmp_path, monkeypatch):
    """Verify interactive prompt if --primary-executable is not provided.

    Args:
        tmp_path: Temporary directory provided by pytest.
        monkeypatch: Pytest monkeypatch fixture.
    """
    # Arrange
    test_case = tmp_path / "test-case-002"
    test_case.mkdir(parents=True)
    dummy_exec = test_case / "program.py"
    dummy_exec.write_text("print('dummy')\n")
    dummy_exec.chmod(0o755)

    # Simulate user input for prompt
    monkeypatch.setattr("builtins.input", lambda _: str(dummy_exec))

    # Act
    result = runner.invoke(
        setup_functional_test.app,
        ["--test-case-dir", str(test_case)],
    )

    # Assert
    assert result.exit_code == 0, "Interactive prompt should complete successfully"
    report_path = Path(result.stdout.strip())
    assert report_path.exists(), "Report file should be generated after prompt"
    assert "setup_functional_test" in result.stdout or "report" in result.stdout


def test_setup_functional_test_invalid_dir(tmp_path):
    """Verify error when an invalid test-case directory is provided.

    Args:
        tmp_path: Temporary directory provided by pytest.
    """
    # Arrange
    invalid_dir = tmp_path / "invalid-dir"
    invalid_dir.mkdir(parents=True)

    # Act
    result = runner.invoke(
        setup_functional_test.app,
        ["--test-case-dir", str(invalid_dir)],
    )

    # Assert
    assert result.exit_code != 0, "Invalid test-case dir must fail"
    assert "test-case-" in result.stderr or "BadParameter" in result.stderr


def test_setup_functional_test_missing_executable(tmp_path):
    """Verify that program exits with code 2 when primary executable path does not exist.

    Args:
        tmp_path: Temporary directory provided by pytest.
    """
    # Arrange
    test_case = tmp_path / "test-case-003"
    test_case.mkdir(parents=True)
    missing_exec = test_case / "does_not_exist.py"

    # Act
    result = runner.invoke(
        setup_functional_test.app,
        [
            "--test-case-dir",
            str(test_case),
            "--primary-executable",
            str(missing_exec),
        ],
    )

    # Assert
    assert result.exit_code == 2, f"Expected exit 2 for missing executable, got {result.exit_code}"
    assert "Error: primary executable not found" in result.stderr
