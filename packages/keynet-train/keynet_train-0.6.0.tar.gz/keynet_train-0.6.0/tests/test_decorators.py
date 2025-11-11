"""데코레이터 서브패키지 테스트."""


class TestDecoratorImports:
    """데코레이터 import 테스트."""

    def test_trace_pytorch_import(self):
        """trace_pytorch 데코레이터 import 확인."""
        from keynet_train.decorators import trace_pytorch

        assert callable(trace_pytorch)

    def test_log_onnx_model_import(self):
        """log_onnx_model 함수 import 확인."""
        from keynet_train.decorators import log_onnx_model

        assert callable(log_onnx_model)

    def test_public_api_import(self):
        """공개 API에서 import 확인."""
        from keynet_train import log_onnx_model, trace_pytorch

        assert callable(trace_pytorch)
        assert callable(log_onnx_model)


class TestDecoratorExecution:
    """데코레이터 실행 테스트 (모의 객체 사용)."""

    def test_trace_pytorch_decorator_structure(self):
        """trace_pytorch 데코레이터 구조 확인."""
        from keynet_train.decorators import trace_pytorch

        # 데코레이터 호출 확인
        decorator = trace_pytorch("test-model", None)  # type: ignore
        assert callable(decorator)

    def test_pytorch_module_import(self):
        """PyTorch 모듈 import 확인."""
        from keynet_train.decorators.pytorch import (
            _convert_to_numpy,
            _generate_input_output_names,
            _infer_model_schema,
        )

        # 유틸리티 함수들이 정의되어 있는지 확인
        assert callable(_convert_to_numpy)
        assert callable(_infer_model_schema)
        assert callable(_generate_input_output_names)

    def test_onnx_module_import(self):
        """ONNX 모듈 import 확인."""
        from keynet_train.decorators.onnx import log_onnx_model

        assert callable(log_onnx_model)
