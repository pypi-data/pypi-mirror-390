"""ArgumentParserExtractor 출력을 ArgumentDefinition으로 변환하는 테스트"""

from keynet_train.clients.converters import convert_to_argument_definitions
from keynet_train.clients.models import ArgumentDefinition, ArgumentType


def test_convert_empty_arguments():
    """빈 arguments 리스트 처리"""
    extractor_output = {"arguments": []}

    result = convert_to_argument_definitions(extractor_output)

    assert result == []


def test_convert_single_argument():
    """단일 argument 변환"""
    extractor_output = {
        "arguments": [
            {
                "name": "learning_rate",
                "type": "float",
                "default": 0.001,
                "required": True,
                "help": "Learning rate",
            }
        ]
    }

    result = convert_to_argument_definitions(extractor_output)

    assert len(result) == 1
    assert isinstance(result[0], ArgumentDefinition)
    assert result[0].name == "learning_rate"
    assert result[0].type == ArgumentType.FLOAT
    assert result[0].default == 0.001
    assert result[0].required is True
    assert result[0].help == "Learning rate"
    assert result[0].choices is None


def test_convert_multiple_arguments():
    """여러 arguments 변환"""
    extractor_output = {
        "arguments": [
            {
                "name": "learning_rate",
                "type": "float",
                "default": 0.001,
                "required": True,
                "help": "Learning rate",
            },
            {
                "name": "batch_size",
                "type": "int",
                "default": 32,
                "required": False,
            },
            {
                "name": "optimizer",
                "type": "str",
                "default": "adam",
                "required": True,
                "help": "Optimizer name",
                "choices": ["adam", "sgd", "rmsprop"],
            },
        ]
    }

    result = convert_to_argument_definitions(extractor_output)

    assert len(result) == 3

    # First argument
    assert result[0].name == "learning_rate"
    assert result[0].type == ArgumentType.FLOAT

    # Second argument
    assert result[1].name == "batch_size"
    assert result[1].type == ArgumentType.INTEGER
    assert result[1].required is False
    assert result[1].help is None

    # Third argument
    assert result[2].name == "optimizer"
    assert result[2].type == ArgumentType.STRING
    assert result[2].choices == ["adam", "sgd", "rmsprop"]


def test_convert_with_missing_optional_fields():
    """선택적 필드가 없을 때 처리"""
    extractor_output = {
        "arguments": [
            {
                "name": "epochs",
                "type": "int",
            }
        ]
    }

    result = convert_to_argument_definitions(extractor_output)

    assert len(result) == 1
    assert result[0].name == "epochs"
    assert result[0].type == ArgumentType.INTEGER
    assert result[0].default is None
    assert result[0].required is False  # default False
    assert result[0].help is None
    assert result[0].choices is None


def test_convert_all_argument_types():
    """모든 ArgumentType 변환 검증"""
    extractor_output = {
        "arguments": [
            {"name": "name", "type": "str"},
            {"name": "count", "type": "int"},
            {"name": "rate", "type": "float"},
            {"name": "flag", "type": "bool"},
        ]
    }

    result = convert_to_argument_definitions(extractor_output)

    assert len(result) == 4
    assert result[0].type == ArgumentType.STRING
    assert result[1].type == ArgumentType.INTEGER
    assert result[2].type == ArgumentType.FLOAT
    assert result[3].type == ArgumentType.BOOLEAN


def test_convert_without_arguments_key():
    """'arguments' 키가 없을 때 빈 리스트 반환"""
    extractor_output = {}

    result = convert_to_argument_definitions(extractor_output)

    assert result == []


def test_convert_with_none_arguments():
    """'arguments'가 None일 때 빈 리스트 반환"""
    extractor_output = {"arguments": None}

    result = convert_to_argument_definitions(extractor_output)

    assert result == []
