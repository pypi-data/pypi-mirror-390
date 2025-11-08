"""CLI 인자 파싱 테스트"""

import argparse

import pytest

from keynet_train.cli.commands.push import setup_push_parser


@pytest.fixture
def parser():
    """Argparse 파서 fixture"""
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers()
    setup_push_parser(subparsers)
    return main_parser


def test_entrypoint_required(parser):
    """entrypoint는 필수 인자"""
    # entrypoint 없이 파싱 시도 → SystemExit 발생
    with pytest.raises(SystemExit):
        parser.parse_args(["push"])


def test_entrypoint_provided(parser):
    """Entrypoint 제공 시 정상 파싱"""
    args = parser.parse_args(["push", "train.py"])
    assert args.entrypoint == "train.py"


def test_dockerfile_default(parser):
    """--dockerfile 기본값 확인"""
    args = parser.parse_args(["push", "train.py"])
    assert args.dockerfile is None  # None이면 auto-generate


def test_dockerfile_custom(parser):
    """--dockerfile 커스텀 경로"""
    args = parser.parse_args(["push", "train.py", "--dockerfile", "custom/Dockerfile"])
    assert args.dockerfile == "custom/Dockerfile"


def test_requirements_default(parser):
    """--requirements 기본값 확인"""
    args = parser.parse_args(["push", "train.py"])
    assert args.requirements is None  # None이면 auto-detect


def test_requirements_custom(parser):
    """--requirements 커스텀 경로"""
    args = parser.parse_args(
        ["push", "train.py", "--requirements", "deps/requirements.txt"]
    )
    assert args.requirements == "deps/requirements.txt"


def test_base_image_default(parser):
    """--base-image 기본값 확인 (None - auto-detect)"""
    args = parser.parse_args(["push", "train.py"])
    assert args.base_image is None  # None이면 decorator 또는 default 사용


def test_base_image_custom(parser):
    """--base-image 커스텀 이미지"""
    args = parser.parse_args(["push", "train.py", "--base-image", "python:3.11-slim"])
    assert args.base_image == "python:3.11-slim"


def test_context_default(parser):
    """--context 기본값 확인"""
    args = parser.parse_args(["push", "train.py"])
    assert args.context == "."


def test_context_custom(parser):
    """--context 커스텀 경로"""
    args = parser.parse_args(["push", "train.py", "--context", "./my-context"])
    assert args.context == "./my-context"


def test_no_cache_default(parser):
    """--no-cache 기본값 확인"""
    args = parser.parse_args(["push", "train.py"])
    assert args.no_cache is False


def test_no_cache_flag(parser):
    """--no-cache 플래그 설정"""
    args = parser.parse_args(["push", "train.py", "--no-cache"])
    assert args.no_cache is True


def test_all_optional_args_together(parser):
    """모든 선택 인자 함께 사용"""
    args = parser.parse_args(
        [
            "push",
            "train.py",
            "--dockerfile",
            "custom/Dockerfile",
            "--requirements",
            "deps/requirements.txt",
            "--base-image",
            "python:3.11",
            "--context",
            "./ctx",
            "--no-cache",
        ]
    )

    assert args.entrypoint == "train.py"
    assert args.dockerfile == "custom/Dockerfile"
    assert args.requirements == "deps/requirements.txt"
    assert args.base_image == "python:3.11"
    assert args.context == "./ctx"
    assert args.no_cache is True
