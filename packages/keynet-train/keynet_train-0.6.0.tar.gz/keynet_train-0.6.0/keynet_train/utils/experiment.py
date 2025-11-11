"""MLflow를 위한 Experiment 이름 생성 유틸리티."""

from typing import Optional


def generate_experiment_name(model_id: Optional[str], model_name: Optional[str]) -> str:
    """
    model_id와 model_name으로 MLflow experiment 이름 생성.

    우선순위:
    1. model_id 존재(None/빈값 아님): "{model_id}_{model_name}"
    2. 그 외: "{model_name}"

    Args:
        model_id: 환경변수의 선택적 model ID (MODEL_ID)
            - None 가능 (환경변수에 설정되지 않음)
            - 빈 문자열 가능 (None으로 처리)
            - 공백은 제거됨
        model_name: 데코레이터의 모델 이름 (필수)
            - None이나 빈값이면 안됨
            - 기본 experiment 이름으로 사용

    Returns:
        str: 포맷된 experiment 이름

    Raises:
        ValueError: model_name이 None이거나 비어있을 때

    Examples:
        >>> generate_experiment_name("42", "resnet50")
        '42_resnet50'

        >>> generate_experiment_name(None, "resnet50")
        'resnet50'

        >>> generate_experiment_name("", "bert-base")
        'bert-base'

        >>> generate_experiment_name("  ", "vit")
        'vit'

        >>> generate_experiment_name("42", "")
        ValueError: model_name is required

    """
    # model_name 유효성 검사
    if not model_name or (isinstance(model_name, str) and not model_name.strip()):
        raise ValueError("model_name is required and cannot be empty")

    # model_id 정규화
    normalized_model_id = None
    if model_id is not None and isinstance(model_id, str):
        stripped = model_id.strip()
        if stripped:  # 공백 제거 후 비어있지 않음
            normalized_model_id = stripped

    # Experiment 이름 구성
    if normalized_model_id:
        return f"{normalized_model_id}_{model_name}"
    else:
        return model_name
