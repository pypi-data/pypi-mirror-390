"""
Tests for UploadKey request/response models.

Tests Pydantic models for uploadKey API endpoint.
"""

import json

from keynet_train.clients.models import (
    ArgumentDefinition,
    ArgumentType,
    Model,
    UploadKeyCommand,
    UploadKeyRequest,
    UploadKeyResponse,
)


class TestUploadKeyRequest:
    """Test UploadKeyRequest model."""

    def test_create_upload_key_request(self):
        """Test creating UploadKeyRequest with hyperparameters."""
        arg1 = ArgumentDefinition(
            name="learning_rate",
            type=ArgumentType.FLOAT,
            default=0.001,
        )
        arg2 = ArgumentDefinition(
            name="epochs",
            type=ArgumentType.INTEGER,
            default=10,
        )

        request = UploadKeyRequest(
            model_name="my-training-model",
            hyper_parameters=[arg1, arg2],
        )

        assert request.model_name == "my-training-model"
        assert len(request.hyper_parameters) == 2
        assert request.hyper_parameters[0].name == "learning_rate"
        assert request.hyper_parameters[1].name == "epochs"

    def test_upload_key_request_empty_hyperparameters(self):
        """Test UploadKeyRequest with no hyperparameters."""
        request = UploadKeyRequest(model_name="simple-model")

        assert request.model_name == "simple-model"
        assert request.hyper_parameters == []

    def test_serialize_to_camelcase(self):
        """Test UploadKeyRequest serializes to camelCase for API."""
        arg = ArgumentDefinition(
            name="batch_size",
            type=ArgumentType.INTEGER,
            default=32,
        )

        request = UploadKeyRequest(
            model_name="my-model",
            hyper_parameters=[arg],
        )

        # Serialize with aliases (camelCase)
        data = request.model_dump(by_alias=True)

        assert data["modelName"] == "my-model"
        assert "hyperParameters" in data
        assert len(data["hyperParameters"]) == 1
        assert data["hyperParameters"][0]["name"] == "batch_size"

    def test_serialize_to_json(self):
        """Test UploadKeyRequest can be serialized to JSON."""
        request = UploadKeyRequest(
            model_name="test-model",
            hyper_parameters=[],
        )

        json_str = request.model_dump_json(by_alias=True)
        data = json.loads(json_str)

        assert data["modelName"] == "test-model"
        assert data["hyperParameters"] == []


class TestUploadKeyResponse:
    """Test UploadKeyResponse model."""

    def test_create_upload_key_response(self):
        """Test creating UploadKeyResponse."""
        command = UploadKeyCommand(
            tag="docker tag <YOUR_IMAGE:TAG> kitech-harbor.wimcorp.dev/kitech-model/abc123:latest",
            push="docker push kitech-harbor.wimcorp.dev/kitech-model/abc123:latest",
        )
        model = Model(id=42, name="resnet50-classifier")
        response = UploadKeyResponse(
            id=123,
            project_id=207,
            upload_key="abc123def456",
            model=model,
            command=command,
        )

        assert response.id == 123
        assert response.project_id == 207
        assert response.upload_key == "abc123def456"
        assert response.model.id == 42
        assert response.model.name == "resnet50-classifier"
        assert response.command.tag.startswith("docker tag")
        assert response.command.push.startswith("docker push")

    def test_deserialize_from_camelcase(self):
        """Test UploadKeyResponse deserializes from camelCase API response."""
        # Actual API response format
        api_data = {
            "id": 253,
            "projectId": 207,
            "uploadKey": "iw6pu99p6hlp11dwi3taz",
            "model": {"id": 42, "name": "resnet50-classifier"},
            "command": {
                "tag": "docker tag <YOUR_IMAGE:TAG> kitech-harbor.wimcorp.dev/kitech-model/iw6pu99p6hlp11dwi3taz:latest",
                "push": "docker push kitech-harbor.wimcorp.dev/kitech-model/iw6pu99p6hlp11dwi3taz:latest",
            },
        }

        response = UploadKeyResponse(**api_data)

        assert response.id == 253
        assert response.project_id == 207
        assert response.upload_key == "iw6pu99p6hlp11dwi3taz"
        assert response.model.id == 42
        assert response.model.name == "resnet50-classifier"
        assert "kitech-model" in response.command.push

    def test_deserialize_from_json(self):
        """Test UploadKeyResponse can be deserialized from JSON."""
        json_str = """
        {
            "id": 789,
            "projectId": 100,
            "uploadKey": "key123",
            "model": {
                "id": 99,
                "name": "test-model"
            },
            "command": {
                "tag": "docker tag <YOUR_IMAGE:TAG> harbor.example.com/project/key123:v1.0",
                "push": "docker push harbor.example.com/project/key123:v1.0"
            }
        }
        """

        response = UploadKeyResponse.model_validate_json(json_str)

        assert response.id == 789
        assert response.project_id == 100
        assert response.upload_key == "key123"
        assert response.model.id == 99
        assert response.model.name == "test-model"
        assert isinstance(response.command, UploadKeyCommand)

    def test_access_via_snake_case(self):
        """Test accessing fields via snake_case attribute names."""
        command = UploadKeyCommand(
            tag="docker tag test",
            push="docker push test",
        )
        model = Model(id=50, name="test-classifier")
        response = UploadKeyResponse(
            id=999,
            project_id=100,
            upload_key="test_key",
            model=model,
            command=command,
        )

        # Should be accessible via snake_case
        assert response.upload_key == "test_key"
        assert response.project_id == 100
        assert response.id == 999
        assert response.model.id == 50
        assert response.model.name == "test-classifier"

    def test_get_image_reference(self):
        """Test extracting image reference from push command."""
        command = UploadKeyCommand(
            tag="docker tag <YOUR_IMAGE:TAG> kitech-harbor.wimcorp.dev/kitech-model/abc123:latest",
            push="docker push kitech-harbor.wimcorp.dev/kitech-model/abc123:latest",
        )
        model = Model(id=30, name="image-classifier")
        response = UploadKeyResponse(
            id=123,
            project_id=207,
            upload_key="abc123",
            model=model,
            command=command,
        )

        image_ref = response.get_image_reference()
        assert image_ref == "kitech-harbor.wimcorp.dev/kitech-model/abc123:latest"
