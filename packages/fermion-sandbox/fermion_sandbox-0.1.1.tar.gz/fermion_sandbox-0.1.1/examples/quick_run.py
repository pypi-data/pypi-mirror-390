"""Example of quick code execution without full sandbox.

Quick run is useful for simple code execution without needing a full container.
Perfect for code snippets, algorithm challenges, or quick tests.

Run with:
    export FERMION_API_KEY='your-api-key'
    python examples/quick_run.py
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
        # Create sandbox connection (required for quick_run)
        await sandbox.create(should_backup_filesystem=False)

        # Python example - simple print statements
        print("=" * 50)
        print("Example 1: Running Python code")
        print("=" * 50)
        result = await sandbox.quick_run(
            runtime='Python',
            source_code='print("Hello from Python!")\nprint(f"2 + 2 = {2 + 2}")'
        )

        if result.program_run_data:
            stdout = result.program_run_data.stdout
            print(f"Status: {result.run_status.value}")
            print(f"Output:\n{stdout}")
            print()

        # C++ example with stdin input
        print("=" * 50)
        print("Example 2: Running C++ code with stdin input")
        print("=" * 50)
        cpp_code = """
#include <iostream>
using namespace std;
int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
"""

        result = await sandbox.quick_run(
            runtime='C++',
            source_code=cpp_code,
            stdin='10 20',
            expected_output='30\n'
        )

        if result.program_run_data:
            stdout = result.program_run_data.stdout
            print(f"Status: {result.run_status.value}")
            print(f"Output:\n{stdout}")
            print(f"Memory used: {result.program_run_data.memory_used_in_kilobyte}KB")
            print()

        print("✓ Quick run examples completed successfully!")
    finally:
        await sandbox.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
