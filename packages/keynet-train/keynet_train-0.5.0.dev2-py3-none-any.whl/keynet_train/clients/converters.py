"""ArgumentParserExtractor 출력을 Backend API 모델로 변환"""

from typing import Any

from keynet_train.clients.models import ArgumentDefinition, ArgumentType


def convert_to_argument_definitions(
    extractor_output: dict[str, Any],
) -> list[ArgumentDefinition]:
    """
    ArgumentParserExtractor 출력을 ArgumentDefinition 리스트로 변환

    Args:
        extractor_output: ArgumentParserExtractor.extract_metadata() 출력
            예: {"arguments": [{"name": "lr", "type": "float", ...}]}

    Returns:
        list[ArgumentDefinition]: Backend API에 전송할 argument 리스트

    """
    arguments = extractor_output.get("arguments")

    # arguments가 None이거나 없을 때 빈 리스트 반환
    if arguments is None:
        return []

    return [
        ArgumentDefinition(
            name=arg["name"],
            type=ArgumentType(arg["type"]),
            default=arg.get("default"),
            required=arg.get("required", False),
            help=arg.get("help"),
            choices=arg.get("choices"),
        )
        for arg in arguments
    ]
