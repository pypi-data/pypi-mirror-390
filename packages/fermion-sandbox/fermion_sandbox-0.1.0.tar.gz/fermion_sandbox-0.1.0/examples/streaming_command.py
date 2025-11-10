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
        await sandbox.create(should_backup_filesystem=False)
        print("✓ Sandbox created\n")

        # Create a Python script that produces output over time
        script = """
import time
for i in range(5):
    print(f"Step {i+1} of 5")
    time.sleep(1)
print("Done!")
"""

        await sandbox.write_file(path='~/countdown.py', content=script)
        print("Running countdown script with streaming output:\n")

        # Run with streaming output (change to home directory first)
        result = await sandbox.run_streaming_command(
            cmd='bash',
            args=['-c', 'cd /home/damner/code && python3 countdown.py'],
            on_stdout=lambda data: print(f"[STDOUT] {data.strip()}"),
            on_stderr=lambda data: print(f"[STDERR] {data.strip()}")
        )

        print(f"\n✓ Command completed with exit code: {result.exit_code}")
        print(f"✓ Total stdout: {len(result.stdout)} bytes")

    finally:
        await sandbox.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
