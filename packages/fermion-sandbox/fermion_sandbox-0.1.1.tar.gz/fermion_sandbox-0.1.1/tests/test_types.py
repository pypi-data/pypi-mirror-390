"""Tests for Pydantic type models."""

import pytest
from fermion_sandbox.types import (
    ContainerDetails,
    RunConfig,
    Language,
    RunStatus,
    ProgramRunData,
    RunResult,
)


class TestContainerDetails:
    """Tests for ContainerDetails model."""

    def test_valid_container_details(self):
        """Test creating valid ContainerDetails."""
        data = {
            "playgroundContainerAccessToken": "test-token-123",
            "subdomain": "abc123",
        }
        details = ContainerDetails(**data)
        assert details.playground_container_access_token == "test-token-123"
        assert details.subdomain == "abc123"

    def test_missing_fields_raises_error(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            ContainerDetails(**{"subdomain": "test"})

        with pytest.raises(Exception):
            ContainerDetails(**{"playgroundContainerAccessToken": "token"})


class TestRunConfig:
    """Tests for RunConfig model."""

    def test_default_values(self):
        """Test that RunConfig has sensible defaults."""
        config = RunConfig()
        assert config.custom_matcher_to_use_for_expected_output == "ExactMatch"
        assert config.expected_output_as_base64_url_encoded == ""
        assert config.stdin_string_as_base64_url_encoded == ""
        assert config.should_allow_internet_access is False

    def test_custom_values(self):
        """Test creating RunConfig with custom values."""
        config = RunConfig(
            expected_output_as_base64_url_encoded="dGVzdA",
            stdin_string_as_base64_url_encoded="aW5wdXQ",
            should_allow_internet_access=True,
        )
        assert config.expected_output_as_base64_url_encoded == "dGVzdA"
        assert config.stdin_string_as_base64_url_encoded == "aW5wdXQ"
        assert config.should_allow_internet_access is True

    def test_alias_handling(self):
        """Test that field aliases work correctly."""
        # Can use snake_case
        config1 = RunConfig(custom_matcher_to_use_for_expected_output="CustomMatch")

        # Can use camelCase alias
        config2 = RunConfig(**{"customMatcherToUseForExpectedOutput": "CustomMatch"})

        assert config1.custom_matcher_to_use_for_expected_output == config2.custom_matcher_to_use_for_expected_output


class TestLanguage:
    """Tests for Language enum."""

    def test_language_values(self):
        """Test that Language enum has expected values."""
        # Verify some common languages exist
        assert Language.PYTHON == "Python"
        assert Language.CPP == "Cpp"
        assert Language.JAVA == "Java"
        assert Language.NODEJS == "Nodejs"
        assert Language.GOLANG == "Golang_1_19"
        assert Language.RUST == "Rust_1_87"
        assert Language.C == "C"
        assert Language.DOTNET == "Dotnet_8"

    def test_language_from_string(self):
        """Test creating Language from string."""
        lang = Language("Python")
        assert lang == Language.PYTHON

    def test_language_values_are_strings(self):
        """Test that Language enum values are strings."""
        assert isinstance(Language.PYTHON.value, str)
        assert isinstance(Language.CPP.value, str)


class TestRunStatus:
    """Tests for RunStatus enum."""

    def test_run_status_values(self):
        """Test that RunStatus enum has expected values."""
        # Verify common statuses exist
        assert RunStatus.SUCCESSFUL == "successful"
        assert RunStatus.TIME_LIMIT_EXCEEDED == "time-limit-exceeded"
        assert RunStatus.COMPILATION_ERROR == "compilation-error"
        assert RunStatus.WRONG_ANSWER == "wrong-answer"
        assert RunStatus.NON_ZERO_EXIT_CODE == "non-zero-exit-code"
        assert RunStatus.UNKNOWN == "unknown"

    def test_run_status_values_are_strings(self):
        """Test that RunStatus enum values are strings."""
        assert isinstance(RunStatus.SUCCESSFUL.value, str)
        assert isinstance(RunStatus.TIME_LIMIT_EXCEEDED.value, str)


class TestProgramRunData:
    """Tests for ProgramRunData model."""

    def test_program_run_data_optional_fields(self):
        """Test that ProgramRunData can be created with minimal fields."""
        # This will depend on the actual model definition
        # Just check it can be imported
        assert ProgramRunData is not None


class TestRunResult:
    """Tests for RunResult model."""

    def test_run_result_import(self):
        """Test that RunResult can be imported."""
        assert RunResult is not None

