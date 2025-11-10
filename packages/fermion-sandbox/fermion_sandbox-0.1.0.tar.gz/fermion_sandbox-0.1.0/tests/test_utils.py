"""Tests for utility functions."""

import pytest
from fermion_sandbox import encode_base64url, decode_base64url
from fermion_sandbox.utils import normalize_path


class TestBase64URL:
    """Tests for Base64URL encoding/decoding."""

    def test_encode_simple_string(self):
        """Test encoding a simple string."""
        result = encode_base64url("hello")
        assert isinstance(result, str)
        assert result == "aGVsbG8"

    def test_decode_simple_string(self):
        """Test decoding a simple string."""
        result = decode_base64url("aGVsbG8")
        assert result == "hello"

    def test_encode_decode_roundtrip(self):
        """Test that encoding and decoding are reversible."""
        test_strings = [
            "hello world",
            "Hello, World!",
            "Test123",
            "Special chars: !@#$%^&*()",
            "Unicode: 你好世界",
            "Multiline\ntext\nwith\nnewlines",
            "",
        ]

        for original in test_strings:
            encoded = encode_base64url(original)
            decoded = decode_base64url(encoded)
            assert decoded == original, f"Failed for: {original!r}"

    def test_encode_removes_padding(self):
        """Test that encoding removes padding."""
        # Base64 of "hello" would normally be "aGVsbG8=" but Base64URL removes =
        encoded = encode_base64url("hello")
        assert "=" not in encoded

    def test_decode_handles_padding(self):
        """Test that decoding handles missing padding."""
        # Test with and without padding
        with_padding = "aGVsbG8="
        without_padding = "aGVsbG8"

        result1 = decode_base64url(with_padding)
        result2 = decode_base64url(without_padding)
        assert result1 == result2 == "hello"

    def test_encode_empty_string(self):
        """Test encoding empty string."""
        result = encode_base64url("")
        assert isinstance(result, str)
        decoded = decode_base64url(result)
        assert decoded == ""

    def test_decode_empty_string(self):
        """Test decoding empty Base64URL."""
        # Empty string encoded
        result = decode_base64url("")
        assert result == ""


class TestNormalizePath:
    """Tests for path normalization."""

    def test_tilde_expansion(self):
        """Test that ~ is expanded to /home/damner."""
        assert normalize_path("~/test.py") == "/home/damner/test.py"
        assert normalize_path("~/dir/file.js") == "/home/damner/dir/file.js"

    def test_absolute_path_preserved(self):
        """Test that absolute paths starting with /home/damner are preserved."""
        path = "/home/damner/test.py"
        assert normalize_path(path) == path

        path = "/home/damner/subdir/file.js"
        assert normalize_path(path) == path
        
        # Also test /home/damner/code paths are still accepted
        path = "/home/damner/code/test.py"
        assert normalize_path(path) == path

    def test_invalid_path_raises_error(self):
        """Test that invalid paths raise ValueError."""
        invalid_paths = [
            "/tmp/file.py",
            "/etc/passwd",
            "relative/path.py",
            "../file.py",
            "file.py",
        ]

        for path in invalid_paths:
            with pytest.raises(ValueError, match="Path must start with"):
                normalize_path(path)

    def test_edge_cases(self):
        """Test edge cases."""
        # Just ~
        assert normalize_path("~") == "/home/damner"

        # ~ with trailing slash
        assert normalize_path("~/") == "/home/damner/"

        # Nested paths
        assert normalize_path("~/a/b/c/d.py") == "/home/damner/a/b/c/d.py"

