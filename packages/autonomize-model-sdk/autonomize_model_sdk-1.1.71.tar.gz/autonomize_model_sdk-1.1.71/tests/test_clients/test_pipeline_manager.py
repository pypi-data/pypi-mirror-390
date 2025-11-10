import os
from unittest.mock import MagicMock

import httpx
import pytest
import yaml

import modelhub.clients.pipeline_manager as pm
from modelhub.clients.pipeline_manager import PipelineManager
from modelhub.core import (
    ModelHubAPIException,
    ModelhubCredential,
    ModelHubResourceNotFoundException,
)
from modelhub.models.models import PipelineCreateRequest


@pytest.fixture
def mock_credential():
    """Create a mock ModelhubCredential."""
    credential = MagicMock(spec=ModelhubCredential)
    credential.get_token.return_value = "dummy-token"
    credential._modelhub_url = "http://dummy"
    return credential


@pytest.fixture
def pipeline_manager(mock_credential):
    return PipelineManager(
        credential=mock_credential, client_id="1"
    )


def create_temp_yaml(tmp_path, data, filename="config.yaml"):
    file_path = tmp_path / filename
    file_path.write_text(yaml.dump(data), encoding="utf-8")
    return file_path


def fake_encode_file(path):
    return f"encoded_{os.path.basename(path)}"


def test_load_config_success(tmp_path, pipeline_manager, monkeypatch):
    config_data = {
        "name": "pipeline1",
        "description": "Test pipeline",
        "experiment_id": "exp1",
        "dataset_id": "ds1",
        "image_tag": "v1",
        "stages": [
            {
                "name": "stage1",
                "type": "type1",
                "script": "path/to/script.sh",
                "requirements": "path/to/requirements.txt",
            },
            {
                "name": "stage2",
                "type": "type2",
                "blob_storage_config": {
                    "container": "mycontainer",
                    "blob_url": "http://blob.url",
                    "mount_path": "/mnt/path",
                },
            },
        ],
    }
    config_file = create_temp_yaml(tmp_path, config_data)
    monkeypatch.setattr(pm, "encode_file", fake_encode_file)

    pipeline_request = pipeline_manager.load_config(str(config_file))
    assert isinstance(pipeline_request, PipelineCreateRequest)

    stage1 = pipeline_request.stages[0]
    assert stage1.script == "encoded_script.sh"
    assert stage1.requirements == "encoded_requirements.txt"
    assert stage1.depends_on == []
    assert stage1.params == {}
    assert stage1.tolerations == []
    assert stage1.node_selector == {}

    stage2 = pipeline_request.stages[1]
    assert stage2.blob_storage_config.container == "mycontainer"
    assert stage2.blob_storage_config.blob_url == "http://blob.url"
    assert stage2.blob_storage_config.mount_path == "/mnt/path"


def test_load_config_with_artifacts(tmp_path, pipeline_manager, monkeypatch):
    config_data = {
        "name": "pipeline_with_artifacts",
        "description": "Test pipeline with artifacts",
        "experiment_id": "exp1",
        "dataset_id": "ds1",
        "image_tag": "v1",
        "stages": [
            {
                "name": "stage1",
                "type": "type1",
                "artifacts": {
                    "outputs": [{"name": "artifact1", "path": "/path/to/artifact1"}]
                },
            },
            {
                "name": "stage2",
                "type": "type2",
                "depends_on": ["stage1"],
                "artifacts": {
                    "inputs": [{"name": "artifact1", "path": "/path/to/input1"}]
                },
            },
            {
                "name": "stage3",
                "type": "type3",
                "artifacts": {
                    "outputs": [
                        {
                            "name": "artifact2",
                            "path": "/path/to/artifact2",
                            "archive": {"none": {}},
                        }
                    ]
                },
            },
        ],
    }
    config_file = create_temp_yaml(tmp_path, config_data)
    monkeypatch.setattr(pm, "encode_file", fake_encode_file)

    pipeline_request = pipeline_manager.load_config(str(config_file))

    # Check stage1 artifact outputs
    stage1 = pipeline_request.stages[0]
    assert stage1.artifacts.outputs[0].name == "artifact1"
    assert stage1.artifacts.outputs[0].path == "/path/to/artifact1"
    assert hasattr(stage1.artifacts, "inputs")
    assert len(stage1.artifacts.inputs) == 0

    # Check stage2 artifact inputs
    stage2 = pipeline_request.stages[1]
    assert stage2.artifacts.inputs[0].name == "artifact1"
    assert stage2.artifacts.inputs[0].path == "/path/to/input1"

    # Check stage3 output artifact with archive option
    stage3 = pipeline_request.stages[2]
    assert stage3.artifacts.outputs[0].name == "artifact2"
    assert "none" in stage3.artifacts.outputs[0].archive
    # Access as dictionary key instead of attribute
    assert stage3.artifacts.outputs[0].archive["none"] == {}


def test_load_config_invalid_artifacts(tmp_path, pipeline_manager):
    config_data = {
        "name": "pipeline_invalid_artifacts",
        "description": "Test pipeline with invalid artifacts",
        "experiment_id": "exp1",
        "dataset_id": "ds1",
        "image_tag": "v1",
        "stages": [
            {
                "name": "stage_invalid",
                "type": "type1",
                "artifacts": {
                    "outputs": ["invalid_output"]  # Not a dict with name and path
                },
            }
        ],
    }
    config_file = create_temp_yaml(tmp_path, config_data)
    with pytest.raises(
        ModelHubAPIException,
        match="Invalid artifact configuration in outputs for stage stage_invalid",
    ):
        pipeline_manager.load_config(str(config_file))


def test_load_config_invalid_blob_storage_config(tmp_path, pipeline_manager):
    config_data = {
        "name": "pipeline1",
        "description": "Test pipeline",
        "experiment_id": "exp1",
        "dataset_id": "ds1",
        "image_tag": "v1",
        "stages": [
            {
                "name": "stage_invalid",
                "type": "type1",
                "blob_storage_config": {"container": "mycontainer"},
            }
        ],
    }
    config_file = create_temp_yaml(tmp_path, config_data)
    with pytest.raises(
        ModelHubAPIException,
        match="Invalid blob_storage_config for stage stage_invalid",
    ):
        pipeline_manager.load_config(str(config_file))


def test_validate_pipeline(tmp_path, pipeline_manager, monkeypatch):
    # Create valid pipeline configuration
    valid_config = {
        "name": "valid_pipeline",
        "description": "Valid pipeline",
        "experiment_id": "exp1",
        "dataset_id": "ds1",
        "image_tag": "v1",
        "stages": [
            {
                "name": "stage1",
                "type": "type1",
                "artifacts": {
                    "outputs": [{"name": "artifact1", "path": "/path/to/artifact1"}]
                },
            },
            {
                "name": "stage2",
                "type": "type2",
                "depends_on": ["stage1"],
                "artifacts": {
                    "inputs": [{"name": "artifact1", "path": "/path/to/input1"}]
                },
            },
        ],
    }
    valid_config_file = create_temp_yaml(tmp_path, valid_config, "valid_config.yaml")

    # Create invalid pipeline configuration (missing dependency)
    invalid_config = {
        "name": "invalid_pipeline",
        "description": "Invalid pipeline",
        "experiment_id": "exp1",
        "dataset_id": "ds1",
        "image_tag": "v1",
        "stages": [
            {
                "name": "stage1",
                "type": "type1",
                "artifacts": {
                    "outputs": [{"name": "artifact1", "path": "/path/to/artifact1"}]
                },
            },
            {
                "name": "stage2",
                "type": "type2",
                # Missing depends_on: ["stage1"]
                "artifacts": {
                    "inputs": [{"name": "artifact1", "path": "/path/to/input1"}]
                },
            },
        ],
    }
    invalid_config_file = create_temp_yaml(
        tmp_path, invalid_config, "invalid_config.yaml"
    )

    # Create another invalid pipeline configuration (artifact not produced)
    missing_artifact_config = {
        "name": "missing_artifact_pipeline",
        "description": "Missing artifact pipeline",
        "experiment_id": "exp1",
        "dataset_id": "ds1",
        "image_tag": "v1",
        "stages": [
            {"name": "stage1", "type": "type1"},
            {
                "name": "stage2",
                "type": "type2",
                "depends_on": ["stage1"],
                "artifacts": {
                    "inputs": [
                        {"name": "nonexistent_artifact", "path": "/path/to/input1"}
                    ]
                },
            },
        ],
    }
    missing_artifact_file = create_temp_yaml(
        tmp_path, missing_artifact_config, "missing_artifact.yaml"
    )

    monkeypatch.setattr(pm, "encode_file", fake_encode_file)

    # Test valid configuration
    valid_result = pipeline_manager.validate_pipeline(str(valid_config_file))
    assert valid_result["valid"] is True
    assert len(valid_result["errors"]) == 0

    # Test invalid configuration (missing dependency)
    invalid_result = pipeline_manager.validate_pipeline(str(invalid_config_file))
    assert invalid_result["valid"] is False
    assert len(invalid_result["errors"]) > 0
    assert (
        "requires artifact 'artifact1' but doesn't depend on the stage that produces it"
        in invalid_result["errors"][0]
    )

    # Test invalid configuration (missing artifact)
    missing_artifact_result = pipeline_manager.validate_pipeline(
        str(missing_artifact_file)
    )
    assert missing_artifact_result["valid"] is False
    assert len(missing_artifact_result["errors"]) > 0
    assert (
        "requires artifact 'nonexistent_artifact' but no stage produces it"
        in missing_artifact_result["errors"][0]
    )


def test_fix_pipeline_configuration(tmp_path, pipeline_manager, monkeypatch):
    # Create pipeline with missing dependencies
    config_data = {
        "name": "pipeline_to_fix",
        "description": "Pipeline with missing dependencies",
        "experiment_id": "exp1",
        "dataset_id": "ds1",
        "image_tag": "v1",
        "stages": [
            {
                "name": "stage1",
                "type": "type1",
                "artifacts": {
                    "outputs": [{"name": "artifact1", "path": "/path/to/artifact1"}]
                },
            },
            {
                "name": "stage2",
                "type": "type2",
                "artifacts": {
                    "outputs": [{"name": "artifact2", "path": "/path/to/artifact2"}]
                },
            },
            {
                "name": "stage3",
                "type": "type3",
                # Missing dependencies to stage1 and stage2
                "artifacts": {
                    "inputs": [
                        {"name": "artifact1", "path": "/path/to/input1"},
                        {"name": "artifact2", "path": "/path/to/input2"},
                    ]
                },
            },
        ],
    }
    config_file = create_temp_yaml(tmp_path, config_data, "config_to_fix.yaml")
    fixed_file = tmp_path / "fixed_config.yaml"

    # Run fix_pipeline_configuration
    results = pipeline_manager.fix_pipeline_configuration(
        str(config_file), str(fixed_file)
    )

    # Check that dependencies were added
    assert len(results["dependencies_added"]) == 2

    # Verify the fixed configuration
    with open(fixed_file, "r") as f:
        fixed_config = yaml.safe_load(f)

    # Check that stage3 now depends on both stage1 and stage2
    stage3 = fixed_config["stages"][2]
    assert "depends_on" in stage3
    assert "stage1" in stage3["depends_on"]
    assert "stage2" in stage3["depends_on"]


def test_start_pipeline(monkeypatch, tmp_path, pipeline_manager):
    # Create a fake pipeline request for validation
    fake_pipeline_request = PipelineCreateRequest(
        name="test_pipeline",
        description="Test pipeline",
        experiment_id="exp1",
        dataset_id="ds1",
        image_tag="v1",
        stages=[],
    )

    # Mock load_config to return the fake request
    monkeypatch.setattr(
        pipeline_manager,
        "load_config",
        lambda config_path, pyproject_path=None: fake_pipeline_request,
    )

    # Mock validate_pipeline to return success
    monkeypatch.setattr(
        pipeline_manager,
        "validate_pipeline",
        lambda config_path=None, pipeline_request=None: {
            "valid": True,
            "warnings": [],
            "errors": [],
        },
    )

    fake_pipeline = {
        "pipeline_id": "1234",
        "stages": [{"name": "stage1"}, {"name": "stage2"}],
    }
    monkeypatch.setattr(
        pipeline_manager,
        "create_or_update",
        lambda config_path, pyproject_path=None: fake_pipeline,
    )

    submit_called = False

    def fake_submit(pipeline_id):
        nonlocal submit_called
        submit_called = True
        return {"result": "submitted", "pipeline_id": pipeline_id}

    monkeypatch.setattr(pipeline_manager, "submit", fake_submit)
    config_file = create_temp_yaml(tmp_path, {"dummy": "data"})
    result = pipeline_manager.start_pipeline(str(config_file))
    assert result == {"result": "submitted", "pipeline_id": "1234"}
    assert submit_called


def test_start_pipeline_validate_only(monkeypatch, tmp_path, pipeline_manager):
    # Create a fake pipeline request for validation
    fake_pipeline_request = PipelineCreateRequest(
        name="test_pipeline",
        description="Test pipeline",
        experiment_id="exp1",
        dataset_id="ds1",
        image_tag="v1",
        stages=[],
    )

    # Mock load_config to return the fake request
    monkeypatch.setattr(
        pipeline_manager,
        "load_config",
        lambda config_path, pyproject_path=None: fake_pipeline_request,
    )

    # Mock validation results
    validation_results = {"valid": True, "warnings": ["Sample warning"], "errors": []}
    monkeypatch.setattr(
        pipeline_manager,
        "validate_pipeline",
        lambda config_path=None, pipeline_request=None: validation_results,
    )

    create_update_called = False

    def fake_create_or_update(config_path, pyproject_path=None):
        nonlocal create_update_called
        create_update_called = True
        return {"pipeline_id": "1234"}

    monkeypatch.setattr(pipeline_manager, "create_or_update", fake_create_or_update)

    submit_called = False

    def fake_submit(pipeline_id):
        nonlocal submit_called
        submit_called = True
        return {"result": "submitted"}

    monkeypatch.setattr(pipeline_manager, "submit", fake_submit)

    # Run start_pipeline with validate_only=True
    config_file = create_temp_yaml(tmp_path, {"dummy": "data"})
    result = pipeline_manager.start_pipeline(str(config_file), validate_only=True)

    # Check that only validation was performed
    assert result == validation_results
    assert not create_update_called
    assert not submit_called


def test_start_pipeline_validation_failure(monkeypatch, tmp_path, pipeline_manager):
    # Create a fake pipeline request for validation
    fake_pipeline_request = PipelineCreateRequest(
        name="test_pipeline",
        description="Test pipeline",
        experiment_id="exp1",
        dataset_id="ds1",
        image_tag="v1",
        stages=[],
    )

    # Mock load_config to return the fake request
    monkeypatch.setattr(
        pipeline_manager,
        "load_config",
        lambda config_path, pyproject_path=None: fake_pipeline_request,
    )

    # Mock validation results with errors
    validation_results = {
        "valid": False,
        "warnings": [],
        "errors": [
            "Stage 'stage2' requires artifact 'artifact1' but no stage produces it."
        ],
    }
    monkeypatch.setattr(
        pipeline_manager,
        "validate_pipeline",
        lambda config_path=None, pipeline_request=None: validation_results,
    )

    create_update_called = False

    def fake_create_or_update(config_path, pyproject_path=None):
        nonlocal create_update_called
        create_update_called = True
        return {"pipeline_id": "1234"}

    monkeypatch.setattr(pipeline_manager, "create_or_update", fake_create_or_update)

    submit_called = False

    def fake_submit(pipeline_id):
        nonlocal submit_called
        submit_called = True
        return {"result": "submitted"}

    monkeypatch.setattr(pipeline_manager, "submit", fake_submit)

    # Run start_pipeline
    config_file = create_temp_yaml(tmp_path, {"dummy": "data"})
    result = pipeline_manager.start_pipeline(str(config_file))

    # Check that validation failed and pipeline was not created/submitted
    assert result == validation_results
    assert not create_update_called
    assert not submit_called


def test_create_or_update_existing(monkeypatch, tmp_path, pipeline_manager):
    fake_request = PipelineCreateRequest(
        name="pipeline1",
        description="desc",
        experiment_id="exp1",
        dataset_id="ds1",
        image_tag="v1",
        stages=[],
    )
    monkeypatch.setattr(
        pipeline_manager,
        "load_config",
        lambda config_path, pyproject_path=None: fake_request,
    )

    existing_pipeline = {"pipeline_id": "existing123"}
    monkeypatch.setattr(
        pipeline_manager, "search_pipeline", lambda name: existing_pipeline
    )

    def fake_put(endpoint, json, **kwargs):
        return {
            "result": "updated",
            "endpoint": endpoint,
        }

    monkeypatch.setattr(pipeline_manager, "put", fake_put)
    config_file = create_temp_yaml(tmp_path, {"dummy": "data"})
    result = pipeline_manager.create_or_update(str(config_file))
    assert result["result"] == "updated"
    assert "pipelines/existing123" in result["endpoint"]


def test_create_or_update_new(monkeypatch, tmp_path, pipeline_manager):
    fake_request = PipelineCreateRequest(
        name="pipeline2",
        description="desc",
        experiment_id="exp2",
        dataset_id="ds2",
        image_tag="v2",
        stages=[],
    )
    monkeypatch.setattr(
        pipeline_manager,
        "load_config",
        lambda config_path, pyproject_path=None: fake_request,
    )

    monkeypatch.setattr(pipeline_manager, "search_pipeline", lambda name: None)

    def fake_post(endpoint, json, **kwargs):
        return {
            "result": "created",
            "endpoint": endpoint,
        }

    monkeypatch.setattr(pipeline_manager, "post", fake_post)
    config_file = create_temp_yaml(tmp_path, {"dummy": "data"})
    result = pipeline_manager.create_or_update(str(config_file))
    assert result["result"] == "created"
    assert result["endpoint"] == "pipelines"


def test_search_pipeline_found(monkeypatch, pipeline_manager):
    monkeypatch.setattr(
        pipeline_manager, "get", lambda endpoint, **kwargs: {"pipeline_id": "found123"}
    )
    result = pipeline_manager.search_pipeline("pipeline1")
    assert result["pipeline_id"] == "found123"


def test_search_pipeline_not_found(monkeypatch, pipeline_manager):
    def fake_get(endpoint, **kwargs):
        raise ModelHubResourceNotFoundException("Resource not found")

    monkeypatch.setattr(pipeline_manager, "get", fake_get)
    result = pipeline_manager.search_pipeline("pipeline1")
    assert result is None


def test_search_pipeline_error(monkeypatch, pipeline_manager):
    """Test handling of server error in search_pipeline."""

    def fake_get(endpoint, **kwargs):
        raise httpx.RequestError("Server error", request=None)

    monkeypatch.setattr(pipeline_manager, "get", fake_get)
    with pytest.raises(ModelHubAPIException):  # Remove the specific regex match
        pipeline_manager.search_pipeline("pipeline1")


def test_submit(monkeypatch, pipeline_manager):
    captured = {}

    def fake_post(endpoint, json, **kwargs):
        captured["endpoint"] = endpoint
        captured["json"] = json
        return {"result": "submitted"}

    monkeypatch.setattr(pipeline_manager, "post", fake_post)
    result = pipeline_manager.submit("pipeline123")
    assert result == {"result": "submitted"}
    assert captured["endpoint"] == "pipelines/pipeline123/submit"
    assert "modelhub_base_url" in captured["json"]
    assert "modelhub_client_id" in captured["json"]
    assert "modelhub_client_secret" in captured["json"]
