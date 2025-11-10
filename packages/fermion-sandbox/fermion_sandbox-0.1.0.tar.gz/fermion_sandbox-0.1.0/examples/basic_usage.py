"""Basic usage example for Fermion Sandbox SDK.

This example demonstrates the core functionality:
- Creating a sandbox container
- Running commands
- Writing and reading files

Run with:
    export FERMION_API_KEY='your-api-key'
    python examples/basic_usage.py
"""

import asyncio
import os
import sys
from fermion_sandbox import Sandbox


async def main():
    # Get API key from environment
    api_key = os.getenv('FERMION_API_KEY')
    if not api_key:
        print("Error: FERMION_API_KEY environment variable is required", file=sys.stderr)
        print("Set it with: export FERMION_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(1)

    # Create sandbox instance
    sandbox = Sandbox(api_key=api_key)

    try:
        # Create a new container
        result = await sandbox.create(should_backup_filesystem=False)
        snippet_id = result['playgroundSnippetId']
        print(f"✓ Sandbox created with snippet ID: {snippet_id}")

        # Run a simple command
        print("\nRunning command: node --version")
        result = await sandbox.run_command(cmd='node', args=['--version'])
        print(f"✓ Node version: {result.stdout.strip()}")

        # Write a file
        print("\nWriting file: ~/hello.js")
        await sandbox.write_file(
            path='~/hello.js',
            content='console.log("Hello from Fermion Sandbox!")'
        )
        print("✓ File written")

        # Execute the file
        print("\nExecuting file: node hello.js")
        result = await sandbox.run_command(cmd='node', args=['hello.js'])
        print(f"✓ Output: {result.stdout.strip()}")

        # Read the file back
        print("\nReading file: ~/hello.js")
        response = await sandbox.get_file('~/hello.js')
        content = response.text
        print(f"✓ File content: {content}")

        # List files
        print("\nListing files:")
        result = await sandbox.run_command(cmd='ls', args=['-la'])
        print(result.stdout)

    finally:
        # Clean up
        print("\nDisconnecting...")
        await sandbox.disconnect()
        print("✓ Disconnected")


if __name__ == '__main__':
    asyncio.run(main())
