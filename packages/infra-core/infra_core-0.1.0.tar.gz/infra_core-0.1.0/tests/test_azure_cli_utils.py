import argparse

from infra_core.azure_functions import add_azure_service_arguments


def test_add_azure_service_arguments_registers_defaults() -> None:
    parser = argparse.ArgumentParser(prog="demo")

    add_azure_service_arguments(
        parser,
        base_url_env_var="SCREENSHOT_FUNC_BASE_URL",
        base_url_help="Custom base URL help",
    )

    args = parser.parse_args(
        [
            "batch-123",
            "--base-url",
            "https://example.net",
            "--poll-timeout",
            "123",
        ]
    )

    assert args.batch_id == "batch-123"
    assert args.base_url == "https://example.net"
    assert args.concurrency == 4
    assert args.poll is True
    assert args.poll_timeout == 123
    assert hasattr(args, "summary_file")


def test_add_azure_service_arguments_optional_summary() -> None:
    parser = argparse.ArgumentParser(prog="demo")
    add_azure_service_arguments(
        parser,
        base_url_env_var="SCREENSHOT_FUNC_BASE_URL",
        include_summary=False,
    )

    args = parser.parse_args(["demo-batch", "--base-url", "https://example.net"])

    assert not hasattr(args, "summary_file")
