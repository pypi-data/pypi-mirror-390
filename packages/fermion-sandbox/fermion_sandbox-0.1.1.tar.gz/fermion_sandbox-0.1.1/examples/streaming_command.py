"""Example of running streaming commands with real-time output.

Streaming is useful for long-running commands where you want to see
output as it happens, rather than waiting for completion.

Run with:
    export FERMION_API_KEY='your-api-key'
    python examples/streaming_command.py
"""

import asyncio
import os
import sys
from fermion_sandbox import Sandbox


async def main():
    api_key = os.getenv('FERMION_API_KEY')
    if not api_key:
        print("Error: FERMION_API_KEY environment variable is required", file=sys.stderr)
        print("Set it with: export FERMION_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(1)

    sandbox = Sandbox(api_key=api_key)

    try:
        print("Creating sandbox...")
        await sandbox.create(should_backup_filesystem=False, git_repo_url='https://github.com/gautamtayal1/perpetual-trading')
        print("✓ Sandbox created\n")

        # Run pnpm install with streaming output
        await sandbox.run_streaming_command(
            cmd='bash', 
            args=['-c', 'cd ~/perpetual-trading && pnpm install'], 
            on_stdout=lambda data: print(data.strip()), 
            on_stderr=lambda data: print(data.strip())
        )
        
        file_content = await sandbox.get_file(path='/home/damner/perpetual-trading/package.json')
        print(file_content.text)

    finally:
        await sandbox.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
