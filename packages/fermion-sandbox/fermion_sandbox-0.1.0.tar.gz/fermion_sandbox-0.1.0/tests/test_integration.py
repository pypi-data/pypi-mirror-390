"""Integration tests for Fermion Sandbox SDK.

These tests require a valid FERMION_API_KEY environment variable.
Skip these tests if the API key is not available.

To run:
    FERMION_API_KEY=your-key pytest tests/test_integration.py

To skip:
    pytest tests/test_integration.py -m "not integration"
"""

import os
import pytest
from fermion_sandbox import Sandbox


# Check if API key is available
SKIP_INTEGRATION = not os.getenv("FERMION_API_KEY")


@pytest.mark.skipif(SKIP_INTEGRATION, reason="FERMION_API_KEY not set")
@pytest.mark.asyncio
class TestSandboxIntegration:
    """Integration tests that require actual API access."""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment."""
        key = os.getenv("FERMION_API_KEY")
        if not key:
            pytest.skip("FERMION_API_KEY not set")
        return key

    @pytest.fixture
    async def sandbox(self, api_key):
        """Create and cleanup sandbox for each test."""
        sandbox = Sandbox(api_key=api_key)
        yield sandbox
        # Cleanup
        if sandbox.is_connected():
            await sandbox.disconnect()

    async def test_create_sandbox(self, sandbox):
        """Test creating a new sandbox."""
        result = await sandbox.create(should_backup_filesystem=False)
        assert result
        assert "playgroundSnippetId" in result
        assert sandbox.is_connected()

    async def test_run_simple_command(self, sandbox):
        """Test running a simple command."""
        await sandbox.create(should_backup_filesystem=False)
        result = await sandbox.run_command(cmd="echo", args=["hello"])
        assert result.stdout.strip() == "hello"
        # Note: run_command doesn't return exit_code, only stdout/stderr

    async def test_file_operations(self, sandbox):
        """Test file write and read operations."""
        await sandbox.create(should_backup_filesystem=False)

        # Write file
        test_content = "Hello, Fermion Sandbox!"
        await sandbox.write_file(path="~/test.txt", content=test_content)

        # Read file back
        response = await sandbox.get_file("~/test.txt")
        assert response.text.strip() == test_content

    async def test_streaming_command(self, sandbox):
        """Test streaming command output."""
        await sandbox.create(should_backup_filesystem=False)

        output_lines = []

        def on_stdout(data):
            output_lines.append(data.strip())

        result = await sandbox.run_streaming_command(
            cmd="bash",
            args=["-c", "echo line1 && echo line2"],
            on_stdout=on_stdout,
        )

        assert len(output_lines) > 0
        assert result.exit_code == 0

    async def test_quick_run(self, sandbox):
        """Test quick code execution."""
        await sandbox.create(should_backup_filesystem=False)
        result = await sandbox.quick_run(
            runtime="Python",
            source_code='print("Hello, World!")',
        )

        assert result is not None
        assert result.run_status
        assert result.program_run_data is not None


@pytest.mark.skipif(SKIP_INTEGRATION, reason="FERMION_API_KEY not set")
@pytest.mark.asyncio
async def test_sandbox_disconnect_handles_not_connected():
    """Test that disconnect raises error when not connected."""
    api_key = os.getenv("FERMION_API_KEY")
    sandbox = Sandbox(api_key=api_key)
    # Should raise error if not connected (matching JS SDK behavior)
    with pytest.raises(Exception, match="Not connected"):
        await sandbox.disconnect()

