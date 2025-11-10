# tests/test_clients/test_mlflow_client.py
import json
import os
from contextlib import contextmanager
from unittest.mock import MagicMock

import mlflow
import pytest

from modelhub.clients.mlflow_client import MLflowClient
from modelhub.core import ModelhubCredential


@pytest.fixture
def mock_credential():
    """Create a mock ModelhubCredential."""
    credential = MagicMock(spec=ModelhubCredential)
    credential.get_token.return_value = "fake-token"
    credential._modelhub_url = "http://api.fake"
    return credential


# Updated fake_get fixture with proper signature
@pytest.fixture
def fake_get():
    def _fake_get(self, endpoint, **kwargs):
        if endpoint == "mlflow/tracking_uri":
            return {"tracking_uri": "http://fake-tracking.uri"}
        elif endpoint == "mlflow/credentials":
            return {"username": "testuser", "password": "testpass"}
        return {}

    return _fake_get


# For most tests, supply a dummy token to bypass get_token network calls.
@pytest.fixture
def mlflow_client(monkeypatch, fake_get, mock_credential):
    # Patch the get method on MLflowClient to use our fake_get.
    monkeypatch.setattr(MLflowClient, "get", fake_get)
    # Create client with mock credential
    client = MLflowClient(
        credential=mock_credential, client_id="1"
    )
    return client


def test_configure_mlflow(monkeypatch, mlflow_client):
    # Patch mlflow functions to capture calls.
    fake_set_tracking_uri = MagicMock()
    fake_set_registry_uri = MagicMock()
    monkeypatch.setattr(mlflow, "set_tracking_uri", fake_set_tracking_uri)
    monkeypatch.setattr(mlflow, "set_registry_uri", fake_set_registry_uri)

    # Re-run configuration to ensure our new BFF proxy pattern is used.
    mlflow_client.configure_mlflow()

    # Verify the BFF proxy pattern is used (with client/copilot path as BaseClient provides)
    expected_uri = "http://api.fake/modelhub/api/v1/client/1/copilot/test-copilot-id/mlflow-tracking"
    fake_set_tracking_uri.assert_called_with(expected_uri)
    fake_set_registry_uri.assert_called_with(expected_uri)
    # Verify that MLFLOW_TRACKING_TOKEN was set instead of username/password
    assert os.environ.get("MLFLOW_TRACKING_TOKEN") == "fake-token"


def test_configure_mlflow_missing_api_url():
    # Create a credential with missing modelhub_url
    from autonomize.exceptions.core.credentials import (
        ModelhubMissingCredentialsException,
    )

    mock_credential = MagicMock(spec=ModelhubCredential)
    mock_credential._modelhub_url = None  # This should cause initialization to fail
    mock_credential.get_token.return_value = "fake-token"

    # Expect exception during MLflowClient initialization when modelhub_url is missing
    with pytest.raises(
        ModelhubMissingCredentialsException, match="Unable to construct API URL"
    ):
        MLflowClient(
            credential=mock_credential, client_id="1"
        )


def test_start_run(tmp_path, monkeypatch, mlflow_client):
    # Create a fake run object with an info attribute.
    fake_run = MagicMock()
    fake_run.info.run_id = "fake-run-id"

    @contextmanager
    def fake_start_run(*args, **kwargs):
        yield fake_run

    monkeypatch.setattr(mlflow, "start_run", fake_start_run)

    # Use a temporary directory as the output_path.
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    run_id_file = output_dir / "run_id"

    with mlflow_client.start_run(
        run_name="test-run", output_path=str(output_dir)
    ) as run:
        assert run.info.run_id == "fake-run-id"

    # Check that the run_id file was created and contains the expected run_id.
    assert run_id_file.exists()
    with open(run_id_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content == "fake-run-id"


def test_end_run(monkeypatch, mlflow_client):
    fake_end_run = MagicMock()
    monkeypatch.setattr(mlflow, "end_run", fake_end_run)

    mlflow_client.end_run(status="FINISHED")
    fake_end_run.assert_called_with(status="FINISHED")


def test_get_previous_stage_run_id(tmp_path, mlflow_client):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    run_id_file = output_dir / "run_id"
    run_id_file.write_text("previous-run-id", encoding="utf-8")

    run_id = mlflow_client.get_previous_stage_run_id(output_path=str(output_dir))
    assert run_id == "previous-run-id"


def test_get_previous_stage_run_id_file_not_found(tmp_path, mlflow_client):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        mlflow_client.get_previous_stage_run_id(output_path=str(output_dir))


def test_set_experiment(monkeypatch, mlflow_client):
    fake_set_experiment = MagicMock()
    monkeypatch.setattr(mlflow, "set_experiment", fake_set_experiment)

    mlflow_client.set_experiment("exp_name", "exp_id")
    fake_set_experiment.assert_called_with("exp_name", "exp_id")


def test_log_param(monkeypatch, mlflow_client):
    fake_log_param = MagicMock()
    monkeypatch.setattr(mlflow, "log_param", fake_log_param)

    mlflow_client.log_param("param1", "value1")
    fake_log_param.assert_called_with("param1", "value1")


def test_log_metric(monkeypatch, mlflow_client):
    fake_log_metric = MagicMock()
    monkeypatch.setattr(mlflow, "log_metric", fake_log_metric)

    mlflow_client.log_metric("metric1", 123.45)
    fake_log_metric.assert_called_with("metric1", 123.45)


def test_log_artifact(monkeypatch, mlflow_client):
    fake_log_artifact = MagicMock()
    monkeypatch.setattr(mlflow, "log_artifact", fake_log_artifact)

    mlflow_client.log_artifact("dummy/path", artifact_path="artifact", run_id="run123")
    fake_log_artifact.assert_called_with("dummy/path", "artifact", "run123")


def test_get_run(monkeypatch, mlflow_client):
    fake_run = MagicMock()
    fake_run.to_dictionary.return_value = {"run": "data"}
    fake_get_run = MagicMock(return_value=fake_run)
    monkeypatch.setattr(mlflow, "get_run", fake_get_run)

    run_data = mlflow_client.get_run("run123")
    fake_get_run.assert_called_with("run123")
    assert run_data == {"run": "data"}


def test_load_model(monkeypatch, mlflow_client):
    fake_model = object()
    fake_load_model = MagicMock(return_value=fake_model)

    # Import the module where MLflowClient is defined.
    import modelhub.clients.mlflow_client as ml_client_mod

    # Create a fake pyfunc object with our fake load_model.
    class FakePyfunc:
        pass

    FakePyfunc.load_model = fake_load_model

    # Create a fake mlflow object with a 'pyfunc' attribute.
    class FakeMLflow:
        pass

    FakeMLflow.pyfunc = FakePyfunc

    # Patch the module-level mlflow in modelhub.clients.mlflow_client.
    monkeypatch.setattr(ml_client_mod, "mlflow", FakeMLflow)

    # Call load_model and check it works
    model = mlflow_client.load_model("model_uri")
    assert model is fake_model
    fake_load_model.assert_called_with("model_uri")


def test_save_model(monkeypatch, mlflow_client):
    fake_save_model = MagicMock()

    # Import the module where MLflowClient is defined.
    import modelhub.clients.mlflow_client as ml_client_mod

    # Create a fake pyfunc with our fake save_model.
    class FakePyfunc:
        pass

    FakePyfunc.save_model = fake_save_model

    # Create a fake mlflow that has a pyfunc attribute.
    class FakeMLflow:
        pass

    FakeMLflow.pyfunc = FakePyfunc

    # Replace the module-level mlflow in modelhub.clients.mlflow_client with our fake.
    monkeypatch.setattr(ml_client_mod, "mlflow", FakeMLflow)

    dummy_model = object()
    mlflow_client.save_model(dummy_model, "model_path")
    fake_save_model.assert_called_with(dummy_model, "model_path")


def test_mlflow_property(mlflow_client):
    # Simply verify that the property returns the mlflow module.
    assert mlflow_client.mlflow is mlflow


def test_context_manager(monkeypatch, mock_credential):
    # Ensure that __enter__ returns self and __exit__ calls end_run.
    def fake_get(self, endpoint, **kwargs):
        if endpoint == "mlflow/tracking_uri":
            return {"tracking_uri": "http://fake-tracking.uri"}
        elif endpoint == "mlflow/credentials":
            return {"username": "user", "password": "pass"}
        return {}

    monkeypatch.setattr(MLflowClient, "get", fake_get)

    # Create client with mock credential
    client = MLflowClient(
        credential=mock_credential, client_id="1"
    )

    fake_end_run = MagicMock()
    monkeypatch.setattr(client, "end_run", fake_end_run)

    with client as c:
        # __enter__ should return self.
        assert c is client
    fake_end_run.assert_called_once()


def test_register_model(monkeypatch, mlflow_client):
    # Mock the register_model function
    fake_register_model = MagicMock()
    model_version = MagicMock()
    model_version.name = "test-model"
    model_version.version = "1"
    model_version.run_id = "test-run-id"
    model_version.status = "READY"
    fake_register_model.return_value = model_version
    monkeypatch.setattr(mlflow, "register_model", fake_register_model)

    # Mock the get_run function to return expected data structure
    fake_run = MagicMock()
    fake_run.to_dictionary.return_value = {
        "data": {
            "metrics": {
                "precision": 0.9,
                "recall": 0.85,
                "f1_score": 0.87,
                "total_count": 1000,
            },
            "params": {
                "dataset": "test-dataset",
                "dataset_description": "Test dataset",
                "preprocessing": "Test preprocessing",
                "train_samples": "800",
                "test_samples": "100",
                "val_samples": "100",
            },
        }
    }
    fake_get_run = MagicMock(return_value=fake_run)
    monkeypatch.setattr(mlflow, "get_run", fake_get_run)

    # Mock the create_model_card_from_json method
    fake_create_model_card = MagicMock(
        return_value={"id": "card-123", "name": "test-model"}
    )
    monkeypatch.setattr(
        mlflow_client, "create_model_card_from_json", fake_create_model_card
    )

    # Test data - provide all required fields for ModelCardSchema
    model_card_data = {
        "name": "test-model",
        "version": "1.0",
        "title": "Test Model",
        "description": "Test model description",
        "input": {
            "type": "text",
            "description": "Text input",
            "sample": "Sample input text",
        },
        "output": {
            "format": "text",
            "description": "Text output",
            "sample": "Sample output text",
        },
        "architecture": {
            "type": "transformer",
            "description": "Transformer architecture",
            "models": [
                {
                    "name": "test-model",
                    "base_model": "https://huggingface.co/test-model",
                    "class_labels": ["label1", "label2"],
                }
            ],
        },
        "training_data": {
            "dataset": "test-dataset",
            "description": "Test dataset description",
            "preprocessing": "Test preprocessing",
            "split": {"train": 800, "test": 100, "validation": 100},
        },
        "performance": {
            "overall": {
                "precision": 0.9,
                "recall": 0.85,
                "f1_score": 0.87,
                "total_count": 1000,
            }
        },
        "contact": {
            "name": "Test Owner",
            "email": "test@example.com",
            "repository": "https://github.com/test/model",
        },
        "inference": {"endpoint": "http://test-model-service:8000/"},
        "is_deleted": False,
    }

    # Call the method
    result = mlflow_client.register_model(
        run_id="test-run-id", model_name="test-model", model_card_data=model_card_data
    )

    # Assertions
    fake_get_run.assert_called_with("test-run-id")
    fake_register_model.assert_called_with(
        model_uri="runs:/test-run-id/model",
        name="test-model",
        await_registration_for=300,
    )

    assert result["model_registration"]["name"] == "test-model"
    assert result["model_registration"]["version"] == "1"
    assert result["model_registration"]["run_id"] == "test-run-id"
    assert result["model_registration"]["status"] == "READY"

    # Verify model card was created with correct data
    fake_create_model_card.assert_called_once()
    model_card_data = fake_create_model_card.call_args[0][0]
    assert model_card_data["name"] == "test-model"
    assert model_card_data["version"] == "1"
    assert model_card_data["description"] == "Test model description"
    assert "performance" in model_card_data
    assert "training_data" in model_card_data
    assert "inference" in model_card_data


def test_create_model_card_from_json_dict(monkeypatch, mlflow_client):
    # Mock the request method
    fake_response = {"id": "card-123", "name": "test-model"}
    fake_request = MagicMock(return_value=fake_response)
    monkeypatch.setattr(mlflow_client, "request", fake_request)

    # Mock the ModelCardSchema validation
    fake_schema = MagicMock()
    fake_schema.dict.return_value = {"name": "test-model", "version": "1.0"}
    fake_model_card_schema = MagicMock(return_value=fake_schema)
    monkeypatch.setattr(
        "modelhub.clients.mlflow_client.ModelCardSchema", fake_model_card_schema
    )

    # Test with dictionary input
    input_data = {"name": "test-model", "version": "1.0"}
    result = mlflow_client.create_model_card_from_json(input_data)

    # Assertions
    fake_model_card_schema.assert_called_with(**input_data)
    fake_request.assert_called_with(
        "POST", "model-card", json={"name": "test-model", "version": "1.0"}
    )
    assert result == fake_response


def test_create_model_card_from_json_file(tmp_path, monkeypatch, mlflow_client):
    # Create a temporary JSON file
    json_file = tmp_path / "model_card.json"
    json_content = {"name": "test-model", "version": "1.0"}
    with open(json_file, "w") as f:
        json.dump(json_content, f)

    # Mock the request method
    fake_response = {"id": "card-123", "name": "test-model"}
    fake_request = MagicMock(return_value=fake_response)
    monkeypatch.setattr(mlflow_client, "request", fake_request)

    # Mock the ModelCardSchema validation
    fake_schema = MagicMock()
    fake_schema.dict.return_value = {"name": "test-model", "version": "1.0"}
    fake_model_card_schema = MagicMock(return_value=fake_schema)
    monkeypatch.setattr(
        "modelhub.clients.mlflow_client.ModelCardSchema", fake_model_card_schema
    )

    # Call the method with file path
    result = mlflow_client.create_model_card_from_json(str(json_file))

    # Assertions
    fake_model_card_schema.assert_called_with(**json_content)
    fake_request.assert_called_with(
        "POST", "model-card", json={"name": "test-model", "version": "1.0"}
    )
    assert result == fake_response


def test_create_model_card_from_json_string(monkeypatch, mlflow_client):
    # Create a JSON string
    json_string = '{"name": "test-model", "version": "1.0"}'

    # Mock the request method
    fake_response = {"id": "card-123", "name": "test-model"}
    fake_request = MagicMock(return_value=fake_response)
    monkeypatch.setattr(mlflow_client, "request", fake_request)

    # Mock the ModelCardSchema validation
    fake_schema = MagicMock()
    fake_schema.dict.return_value = {"name": "test-model", "version": "1.0"}
    fake_model_card_schema = MagicMock(return_value=fake_schema)
    monkeypatch.setattr(
        "modelhub.clients.mlflow_client.ModelCardSchema", fake_model_card_schema
    )

    # Call the method with JSON string
    result = mlflow_client.create_model_card_from_json(json_string)

    # Assertions
    fake_model_card_schema.assert_called_with(**json.loads(json_string))
    fake_request.assert_called_with(
        "POST", "model-card", json={"name": "test-model", "version": "1.0"}
    )
    assert result == fake_response


def test_create_model_card_from_json_error(monkeypatch, mlflow_client):
    # Mock the ModelCardSchema to raise an exception
    def mock_schema_error(**kwargs):
        raise ValueError("Invalid model card schema")

    monkeypatch.setattr(
        "modelhub.clients.mlflow_client.ModelCardSchema", mock_schema_error
    )

    # Test with invalid data
    with pytest.raises(ValueError, match="Invalid model card schema"):
        mlflow_client.create_model_card_from_json({"invalid": "data"})


def test_update_model_card(monkeypatch, mlflow_client):
    # Mock the request method
    fake_response = {"id": "card-123", "name": "updated-model", "version": "1.1"}
    fake_request = MagicMock(return_value=fake_response)
    monkeypatch.setattr(mlflow_client, "request", fake_request)

    # Test data
    model_id = "card-123"
    updates = {"name": "updated-model", "version": "1.1"}

    # Call the method
    result = mlflow_client.update_model_card(model_id, updates)

    # Assertions
    fake_request.assert_called_with("PATCH", f"model-card/{model_id}", json=updates)
    assert result == fake_response


def test_update_model_card_error(monkeypatch, mlflow_client):
    # Mock the request method to raise an exception
    def mock_request_error(*args, **kwargs):
        raise Exception("API error")

    monkeypatch.setattr(mlflow_client, "request", mock_request_error)

    # Test data
    model_id = "card-123"
    updates = {"name": "updated-model"}

    # Call the method and expect error
    with pytest.raises(Exception, match="API error"):
        mlflow_client.update_model_card(model_id, updates)


def test_delete_model_card(monkeypatch, mlflow_client):
    # Mock the request method
    fake_request = MagicMock()
    monkeypatch.setattr(mlflow_client, "request", fake_request)

    # Test data
    model_id = "card-123"

    # Call the method
    result = mlflow_client.delete_model_card(model_id)

    # Assertions
    fake_request.assert_called_with("DELETE", f"model-card/{model_id}")
    assert result is True


def test_delete_model_card_error(monkeypatch, mlflow_client):
    # Mock the request method to raise an exception
    def mock_request_error(*args, **kwargs):
        raise Exception("API error")

    monkeypatch.setattr(mlflow_client, "request", mock_request_error)

    # Test data
    model_id = "card-123"

    # Call the method and expect error
    with pytest.raises(Exception, match="API error"):
        mlflow_client.delete_model_card(model_id)
