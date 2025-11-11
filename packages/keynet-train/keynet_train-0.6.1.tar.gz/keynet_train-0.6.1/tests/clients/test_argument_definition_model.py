"""
Tests for ArgumentDefinition model.

Tests the Pydantic model for argument definitions that will be sent to Backend API.
"""

import json

from keynet_train.clients.models import ArgumentDefinition, ArgumentType


class TestArgumentDefinitionModel:
    """Test ArgumentDefinition Pydantic model."""

    def test_create_argument_definition(self):
        """Test creating ArgumentDefinition with all fields."""
        arg_def = ArgumentDefinition(
            name="learning_rate",
            type=ArgumentType.FLOAT,
            default=0.001,
            required=False,
            help="Learning rate for optimizer",
            choices=None,
        )

        assert arg_def.name == "learning_rate"
        assert arg_def.type == ArgumentType.FLOAT
        assert arg_def.default == 0.001
        assert arg_def.required is False
        assert arg_def.help == "Learning rate for optimizer"
        assert arg_def.choices is None

    def test_create_argument_definition_minimal(self):
        """Test creating ArgumentDefinition with minimal fields."""
        arg_def = ArgumentDefinition(
            name="epochs",
            type=ArgumentType.INTEGER,
        )

        assert arg_def.name == "epochs"
        assert arg_def.type == ArgumentType.INTEGER
        assert arg_def.default is None
        assert arg_def.required is False
        assert arg_def.help is None
        assert arg_def.choices is None

    def test_argument_type_enum_values(self):
        """Test ArgumentType enum has correct values."""
        assert ArgumentType.STRING == "str"
        assert ArgumentType.INTEGER == "int"
        assert ArgumentType.FLOAT == "float"
        assert ArgumentType.BOOLEAN == "bool"

    def test_argument_definition_with_choices(self):
        """Test ArgumentDefinition with choices field."""
        arg_def = ArgumentDefinition(
            name="optimizer",
            type=ArgumentType.STRING,
            choices=["adam", "sgd", "rmsprop"],
            default="adam",
        )

        assert arg_def.choices == ["adam", "sgd", "rmsprop"]
        assert arg_def.default == "adam"

    def test_serialize_to_camelcase(self):
        """Test ArgumentDefinition serializes to camelCase for API."""
        arg_def = ArgumentDefinition(
            name="batch_size",
            type=ArgumentType.INTEGER,
            default=32,
            required=True,
            help="Batch size for training",
        )

        # Serialize with aliases (camelCase)
        data = arg_def.model_dump(by_alias=True)

        # Note: 'name', 'type', 'default', 'required', 'help', 'choices' don't need camelCase
        # as they are simple single words or already conventional
        assert data["name"] == "batch_size"
        assert data["type"] == "int"
        assert data["default"] == 32
        assert data["required"] is True
        assert data["help"] == "Batch size for training"

    def test_serialize_to_json(self):
        """Test ArgumentDefinition can be serialized to JSON."""
        arg_def = ArgumentDefinition(
            name="learning_rate",
            type=ArgumentType.FLOAT,
            default=0.001,
        )

        json_str = arg_def.model_dump_json()
        data = json.loads(json_str)

        assert data["name"] == "learning_rate"
        assert data["type"] == "float"
        assert data["default"] == 0.001

    def test_deserialize_from_dict(self):
        """Test creating ArgumentDefinition from dict."""
        data = {
            "name": "epochs",
            "type": "int",
            "default": 10,
            "required": True,
            "help": "Number of epochs",
        }

        arg_def = ArgumentDefinition(**data)

        assert arg_def.name == "epochs"
        assert arg_def.type == ArgumentType.INTEGER
        assert arg_def.default == 10
        assert arg_def.required is True
