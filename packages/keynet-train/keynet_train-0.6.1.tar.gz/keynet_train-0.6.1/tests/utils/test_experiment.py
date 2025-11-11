"""Experiment 이름 생성 유틸리티 테스트."""

import pytest

from keynet_train.utils.experiment import generate_experiment_name


class TestGenerateExperimentName:
    """model_id와 model_name으로 experiment 이름 생성 테스트."""

    def test_with_model_id_and_model_name(self):
        """model_id와 model_name이 모두 있을 때 experiment 이름 테스트."""
        result = generate_experiment_name(
            model_id="42", model_name="resnet50-classifier"
        )
        assert result == "42_resnet50-classifier"

    def test_with_none_model_id(self):
        """model_id가 None일 때 experiment 이름 테스트."""
        result = generate_experiment_name(model_id=None, model_name="bert-sentiment")
        assert result == "bert-sentiment"

    def test_with_empty_string_model_id(self):
        """model_id가 빈 문자열일 때 (None으로 처리) experiment 이름 테스트."""
        result = generate_experiment_name(model_id="", model_name="vit-classifier")
        assert result == "vit-classifier"

    def test_with_numeric_model_id(self):
        """숫자형 model_id로 experiment 이름 테스트."""
        result = generate_experiment_name(model_id="999", model_name="efficientnet-b0")
        assert result == "999_efficientnet-b0"

    def test_with_hyphenated_model_id(self):
        """하이픈이 포함된 model_id로 experiment 이름 테스트."""
        result = generate_experiment_name(
            model_id="project-42-v2", model_name="custom-model"
        )
        assert result == "project-42-v2_custom-model"

    def test_model_name_required(self):
        """model_name이 필수임을 테스트."""
        with pytest.raises(ValueError, match="model_name is required"):
            generate_experiment_name(model_id="42", model_name="")

    def test_model_name_none_raises_error(self):
        """model_name이 None이면 ValueError 발생하는지 테스트."""
        with pytest.raises(ValueError, match="model_name is required"):
            generate_experiment_name(model_id="42", model_name=None)

    def test_whitespace_handling_in_model_id(self):
        """model_id의 앞뒤 공백이 제거되는지 테스트."""
        result = generate_experiment_name(model_id="  42  ", model_name="model")
        assert result == "42_model"

    def test_whitespace_only_model_id_treated_as_none(self):
        """공백만 있는 model_id가 None으로 처리되는지 테스트."""
        result = generate_experiment_name(model_id="   ", model_name="model")
        assert result == "model"
