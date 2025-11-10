import json
import os
import sys
from unittest.mock import Mock, call, patch

import pytest

from modelhub.cli import main as cli_main
from modelhub.core import ModelHubException


@pytest.fixture
def mock_env_vars():
    """Fixture to set up environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "MODELHUB_BASE_URL": "http://test-url.com",
            "MODELHUB_CLIENT_ID": "test-client-id",
            "MODELHUB_CLIENT_SECRET": "test-client-secret",
        },
    ):
        yield


@pytest.fixture
def mock_credential():
    """Fixture to mock the ModelhubCredential class."""
    with patch("modelhub.cli.ModelhubCredential") as mock_cred:
        # Create a mock instance to be returned by the constructor
        mock_instance = Mock()
        mock_cred.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_pipeline_manager(mock_credential):
    """Fixture to mock the PipelineManager class."""
    with patch("modelhub.cli.PipelineManager") as mock_pm:
        # Create a mock instance to be returned by the constructor
        mock_instance = Mock()
        mock_pm.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_exit():
    """Fixture to mock sys.exit so tests don't actually exit."""
    with patch("sys.exit") as mock_exit:
        yield mock_exit


@pytest.fixture
def mock_print():
    """Fixture to mock print function to capture output."""
    with patch("builtins.print") as mock_print:
        yield mock_print


@pytest.fixture
def mock_os_path_exists():
    """Fixture to mock os.path.exists."""
    with patch("os.path.exists") as mock_exists:
        # Default to True for most files
        mock_exists.return_value = True
        yield mock_exists


def test_missing_env_var():
    """Test behavior when MODELHUB_BASE_URL environment variable is not set."""
    with patch.dict(os.environ, clear=True):
        with patch("sys.argv", ["modelhub", "validate", "-f", "test.yaml"]):
            with pytest.raises(SystemExit):
                cli_main()


def test_validate_valid_pipeline(
    mock_env_vars, mock_pipeline_manager, mock_exit, mock_print
):
    """Test validate command with a valid pipeline configuration."""
    # Set up mock for validate_pipeline to return a successful result
    mock_pipeline_manager.validate_pipeline.return_value = {
        "valid": True,
        "warnings": [],
        "errors": [],
    }

    # Set up command line arguments
    with patch("sys.argv", ["modelhub", "validate", "-f", "valid_pipeline.yaml"]):
        cli_main()

    # Check that validate_pipeline was called with correct arguments
    mock_pipeline_manager.validate_pipeline.assert_called_once_with(
        "valid_pipeline.yaml"
    )

    # Check output messages
    mock_print.assert_any_call("Validating pipeline configuration: valid_pipeline.yaml")
    mock_print.assert_any_call("✅ Pipeline configuration is valid.")

    # Check exit code
    mock_exit.assert_called_once_with(0)


def test_validate_invalid_pipeline(
    mock_env_vars, mock_pipeline_manager, mock_exit, mock_print
):
    """Test validate command with an invalid pipeline configuration."""
    # Set up mock for validate_pipeline to return errors
    mock_pipeline_manager.validate_pipeline.return_value = {
        "valid": False,
        "warnings": ["Warning 1"],
        "errors": ["Error 1", "Error 2"],
    }

    # Set up command line arguments
    with patch("sys.argv", ["modelhub", "validate", "-f", "invalid_pipeline.yaml"]):
        cli_main()

    # Check that validate_pipeline was called with correct arguments
    mock_pipeline_manager.validate_pipeline.assert_called_once_with(
        "invalid_pipeline.yaml"
    )

    # Check output messages
    mock_print.assert_any_call(
        "Validating pipeline configuration: invalid_pipeline.yaml"
    )
    mock_print.assert_any_call("❌ Pipeline configuration has errors.")
    mock_print.assert_any_call("\nWarnings:")
    mock_print.assert_any_call("  1. Warning 1")
    mock_print.assert_any_call("\nErrors:")
    mock_print.assert_any_call("  1. Error 1")
    mock_print.assert_any_call("  2. Error 2")

    # Check exit code
    mock_exit.assert_called_once_with(1)


def test_validate_json_format(
    mock_env_vars, mock_pipeline_manager, mock_exit, mock_print
):
    """Test validate command with JSON output format."""
    # Set up mock for validate_pipeline to return a result
    validation_result = {"valid": True, "warnings": ["Warning 1"], "errors": []}
    mock_pipeline_manager.validate_pipeline.return_value = validation_result

    # Set up command line arguments
    with patch(
        "sys.argv", ["modelhub", "validate", "-f", "pipeline.yaml", "--format", "json"]
    ):
        cli_main()

    # Check that validate_pipeline was called
    mock_pipeline_manager.validate_pipeline.assert_called_once_with("pipeline.yaml")

    # Check JSON output
    mock_print.assert_any_call(json.dumps(validation_result, indent=2))

    # Check exit code
    mock_exit.assert_called_once_with(0)


def test_validate_with_fix(mock_env_vars, mock_pipeline_manager, mock_exit, mock_print):
    """Test validate command with --fix option."""
    # Set up mock for validate_pipeline to return initial validation failure
    mock_pipeline_manager.validate_pipeline.side_effect = [
        {
            "valid": False,
            "warnings": [],
            "errors": ["Missing dependency for artifact 'artifact1'"],
        },
        # Second call after fixing returns success
        {"valid": True, "warnings": [], "errors": []},
    ]

    # Set up mock for fix_pipeline_configuration
    mock_pipeline_manager.fix_pipeline_configuration.return_value = {
        "dependencies_added": [
            {
                "stage": "stage2",
                "added_dependency": "stage1",
                "for_artifact": "artifact1",
            }
        ]
    }

    # Set up command line arguments
    with patch("sys.argv", ["modelhub", "validate", "-f", "pipeline.yaml", "--fix"]):
        cli_main()

    # Check that validate_pipeline was called twice
    assert mock_pipeline_manager.validate_pipeline.call_count == 2
    mock_pipeline_manager.validate_pipeline.assert_has_calls(
        [call("pipeline.yaml"), call("pipeline.yaml")]  # Second call to check if fixed
    )

    # Check that fix_pipeline_configuration was called
    mock_pipeline_manager.fix_pipeline_configuration.assert_called_once_with(
        "pipeline.yaml", None
    )

    # Check output messages
    mock_print.assert_any_call("\nAttempting to fix configuration issues...")
    mock_print.assert_any_call("\nFixed by adding dependencies:")
    mock_print.assert_any_call(
        "  • Added 'stage1' as dependency for 'stage2' (needed for artifact 'artifact1')"
    )
    mock_print.assert_any_call(
        "\n✅ Pipeline configuration has been fixed and saved to pipeline.yaml"
    )

    # Check exit code
    mock_exit.assert_called_once_with(0)


def test_validate_with_fix_custom_output(
    mock_env_vars, mock_pipeline_manager, mock_exit, mock_print
):
    """Test validate command with --fix and custom output path."""
    # Set up mock for validate_pipeline to return initial validation failure
    mock_pipeline_manager.validate_pipeline.side_effect = [
        {"valid": False, "warnings": [], "errors": ["Missing dependency"]},
        # Second call after fixing returns success
        {"valid": True, "warnings": [], "errors": []},
    ]

    # Set up mock for fix_pipeline_configuration
    mock_pipeline_manager.fix_pipeline_configuration.return_value = {
        "dependencies_added": [
            {
                "stage": "stage2",
                "added_dependency": "stage1",
                "for_artifact": "artifact1",
            }
        ]
    }

    # Set up command line arguments
    with patch(
        "sys.argv",
        [
            "modelhub",
            "validate",
            "-f",
            "pipeline.yaml",
            "--fix",
            "--output",
            "fixed.yaml",
        ],
    ):
        cli_main()

    # Check that fix_pipeline_configuration was called with custom output
    mock_pipeline_manager.fix_pipeline_configuration.assert_called_once_with(
        "pipeline.yaml", "fixed.yaml"
    )

    # Check that validate_pipeline was called with the output file for the second validation
    mock_pipeline_manager.validate_pipeline.assert_has_calls(
        [call("pipeline.yaml"), call("fixed.yaml")]
    )

    # Check output message has the custom output path
    mock_print.assert_any_call(
        "\n✅ Pipeline configuration has been fixed and saved to fixed.yaml"
    )


def test_validate_with_fix_no_fixes_possible(
    mock_env_vars, mock_pipeline_manager, mock_exit, mock_print
):
    """Test validate command with --fix where no fixes are possible."""
    # Set up mock for validate_pipeline to return validation failure
    mock_pipeline_manager.validate_pipeline.return_value = {
        "valid": False,
        "warnings": [],
        "errors": ["Complex error that can't be fixed automatically"],
    }

    # Set up mock for fix_pipeline_configuration with no fixes
    mock_pipeline_manager.fix_pipeline_configuration.return_value = {
        "dependencies_added": []
    }

    # Set up command line arguments
    with patch("sys.argv", ["modelhub", "validate", "-f", "pipeline.yaml", "--fix"]):
        cli_main()

    # Check output message
    mock_print.assert_any_call("\nNo fixes could be applied automatically.")

    # Check exit code
    mock_exit.assert_called_once_with(1)


def test_validate_with_pyproject(
    mock_env_vars, mock_pipeline_manager, mock_exit, mock_print, mock_os_path_exists
):
    """Test validate command with pyproject.toml path."""
    # Set up mock for validate_pipeline
    mock_pipeline_manager.validate_pipeline.return_value = {
        "valid": True,
        "warnings": [],
        "errors": [],
    }

    # Set up command line arguments
    with patch(
        "sys.argv",
        [
            "modelhub",
            "validate",
            "-f",
            "pipeline.yaml",
            "--pyproject",
            "custom/pyproject.toml",
        ],
    ):
        cli_main()

    # We don't pass pyproject.toml to validate_pipeline as it's only for load_config
    mock_pipeline_manager.validate_pipeline.assert_called_once_with("pipeline.yaml")


def test_start_local_mode(
    mock_env_vars, mock_pipeline_manager, mock_os_path_exists, mock_print
):
    """Test start command in local mode."""
    # Set up mock for start_pipeline
    mock_pipeline_manager.start_pipeline.return_value = {
        "pipeline_id": "12345",
        "status": "submitted",
    }

    # Set up command line arguments
    with patch(
        "sys.argv", ["modelhub", "start", "-f", "pipeline.yaml", "--mode", "local"]
    ):
        cli_main()

    # Check that start_pipeline was called with correct arguments
    mock_pipeline_manager.start_pipeline.assert_called_once_with(
        "pipeline.yaml", "pyproject.toml"
    )

    # Check output messages
    mock_print.assert_any_call(
        "Starting pipeline locally using pipeline.yaml with pyproject file pyproject.toml ..."
    )
    mock_print.assert_any_call(
        "Pipeline started:", {"pipeline_id": "12345", "status": "submitted"}
    )


def test_start_cicd_mode(mock_env_vars, mock_pipeline_manager, mock_print):
    """Test start command in cicd mode."""
    # Set up mock for start_pipeline
    mock_pipeline_manager.start_pipeline.return_value = {
        "pipeline_id": "12345",
        "status": "submitted",
    }

    # Set up command line arguments
    with patch(
        "sys.argv", ["modelhub", "start", "-f", "pipeline.yaml", "--mode", "cicd"]
    ):
        cli_main()

    # Check that start_pipeline was called with correct arguments (no pyproject)
    mock_pipeline_manager.start_pipeline.assert_called_once_with("pipeline.yaml")

    # Check output messages
    mock_print.assert_any_call(
        "Starting pipeline in CI/CD mode using pipeline.yaml ..."
    )
    mock_print.assert_any_call(
        "Pipeline started in CI/CD mode:",
        {"pipeline_id": "12345", "status": "submitted"},
    )


def test_start_with_validation_success(
    mock_env_vars, mock_pipeline_manager, mock_print
):
    """Test start command with validation that succeeds."""
    # Set up mock for validate_pipeline to return success
    mock_pipeline_manager.validate_pipeline.return_value = {
        "valid": True,
        "warnings": ["Sample warning"],
        "errors": [],
    }

    # Set up mock for start_pipeline
    mock_pipeline_manager.start_pipeline.return_value = {
        "pipeline_id": "12345",
        "status": "submitted",
    }

    # Set up command line arguments
    with patch("sys.argv", ["modelhub", "start", "-f", "pipeline.yaml", "--validate"]):
        cli_main()

    # Check that validate_pipeline was called
    mock_pipeline_manager.validate_pipeline.assert_called_once_with("pipeline.yaml")

    # Check that start_pipeline was called (validation succeeded)
    mock_pipeline_manager.start_pipeline.assert_called_once()

    # Check output messages
    mock_print.assert_any_call("✅ Pipeline configuration is valid.")
    mock_print.assert_any_call("\nWarnings:")
    mock_print.assert_any_call("  • Sample warning")


def test_start_with_validation_failure(
    mock_env_vars, mock_pipeline_manager, mock_print
):
    """Test start command with validation that fails."""
    # Set up mock for validate_pipeline to return failure
    mock_pipeline_manager.validate_pipeline.return_value = {
        "valid": False,
        "warnings": [],
        "errors": ["Critical error in configuration"],
    }

    # Setup sys.exit to actually raise an exception to stop execution
    with patch("sys.exit") as mock_exit:
        mock_exit.side_effect = SystemExit

        # Set up command line arguments
        with patch(
            "sys.argv", ["modelhub", "start", "-f", "pipeline.yaml", "--validate"]
        ):
            # The SystemExit exception will be raised when sys.exit is called
            with pytest.raises(SystemExit):
                cli_main()

    # Check that validate_pipeline was called
    mock_pipeline_manager.validate_pipeline.assert_called_once_with("pipeline.yaml")

    # Check output messages
    mock_print.assert_any_call("❌ Pipeline configuration has errors:")
    mock_print.assert_any_call("  • Critical error in configuration")
    mock_print.assert_any_call(
        "\nPipeline will not be started due to validation errors."
    )

    # Since execution stops at sys.exit, start_pipeline should never be called
    mock_pipeline_manager.start_pipeline.assert_not_called()


def test_missing_pyproject_in_local_mode(
    mock_env_vars, mock_pipeline_manager, mock_os_path_exists
):
    """Test error when pyproject.toml is missing in local mode."""
    # Set up os.path.exists to return False for pyproject.toml
    mock_os_path_exists.side_effect = lambda path: path != "pyproject.toml"

    # Set up command line arguments
    with patch(
        "sys.argv", ["modelhub", "start", "-f", "pipeline.yaml", "--mode", "local"]
    ):
        with pytest.raises(SystemExit):
            cli_main()

    # Check that start_pipeline was NOT called
    mock_pipeline_manager.start_pipeline.assert_not_called()


def test_missing_pyproject_in_validate(
    mock_env_vars, mock_pipeline_manager, mock_os_path_exists, mock_print, mock_exit
):
    """Test warning when pyproject.toml is specified but missing in validate command."""
    # Set up os.path.exists to return False for custom pyproject path
    mock_os_path_exists.side_effect = lambda path: path != "missing_pyproject.toml"

    # Set up mock for validate_pipeline
    mock_pipeline_manager.validate_pipeline.return_value = {
        "valid": True,
        "warnings": [],
        "errors": [],
    }

    # Set up command line arguments
    with patch(
        "sys.argv",
        [
            "modelhub",
            "validate",
            "-f",
            "pipeline.yaml",
            "--pyproject",
            "missing_pyproject.toml",
        ],
    ):
        cli_main()

    # Check warning message
    mock_print.assert_any_call(
        "Warning: pyproject.toml file not found at missing_pyproject.toml",
        file=sys.stderr,
    )

    # Check that validate_pipeline was still called
    mock_pipeline_manager.validate_pipeline.assert_called_once_with("pipeline.yaml")


def test_exception_during_validation(
    mock_env_vars, mock_pipeline_manager, mock_exit, mock_print
):
    """Test handling of exceptions during validation."""
    # Set up mock for validate_pipeline to raise an exception
    mock_pipeline_manager.validate_pipeline.side_effect = ModelHubException(
        "Test error message"
    )

    # Set up command line arguments
    with patch("sys.argv", ["modelhub", "validate", "-f", "pipeline.yaml"]):
        cli_main()

    # Check error message
    mock_print.assert_any_call(
        "Error validating pipeline: Test error message", file=sys.stderr
    )

    # Check exit code
    mock_exit.assert_called_once_with(1)
