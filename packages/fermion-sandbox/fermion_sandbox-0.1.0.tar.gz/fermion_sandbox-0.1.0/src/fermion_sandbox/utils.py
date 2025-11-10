"""Utility functions for Fermion Sandbox SDK."""

import base64


def encode_base64url(data: str) -> str:
    """Encode a string to Base64URL format (URL-safe Base64).

    Base64URL encoding replaces + with -, / with _, and removes padding =

    Args:
        data: String to encode

    Returns:
        Base64URL encoded string
    """
    encoded_bytes = base64.urlsafe_b64encode(data.encode('utf-8'))
    # Remove padding
    return encoded_bytes.decode('ascii').rstrip('=')


def decode_base64url(data: str) -> str:
    """Decode a Base64URL string to a regular string.

    Args:
        data: Base64URL encoded string

    Returns:
        Decoded string
    """
    # Add padding if needed
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += '=' * padding

    decoded_bytes = base64.urlsafe_b64decode(data)
    return decoded_bytes.decode('utf-8')


def normalize_path(path: str) -> str:
    """Normalize file paths for the sandbox environment.

    - Expands ~ to /home/damner (actual home directory)
    - Validates that path starts with either ~ or /home/damner

    Args:
        path: The input path (must start with ~ or /home/damner)

    Returns:
        Normalized path

    Raises:
        ValueError: If path doesn't start with ~ or /home/damner
    """
    if path.startswith('~'):
        return path.replace('~', '/home/damner', 1)
    elif path.startswith('/home/damner'):
        return path
    else:
        raise ValueError(f'Path must start with ~ or /home/damner. Got: "{path}".')
