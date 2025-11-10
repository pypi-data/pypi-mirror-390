"""Example of running a web server and getting public URL.

This demonstrates how to:
- Start a web server in the sandbox
- Get a publicly accessible URL
- Expose ports (3000, 1337, or 1338)

Run with:
    export FERMION_API_KEY='your-api-key'
    python examples/web_server.py
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

        # Create a simple HTTP server
        server_code = """
const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Hello from Fermion Sandbox!\\n');
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});
"""

        await sandbox.write_file(path='~/server.js', content=server_code)
        print("✓ Server script created\n")

        # Start the server in the background
        print("Starting server...")

        async def run_server():
            await sandbox.run_streaming_command(
                cmd='bash',
                args=['-c', 'cd /home/damner/code && node server.js'],
                on_stdout=lambda data: print(f"[SERVER] {data.strip()}"),
                on_stderr=lambda data: print(f"[ERROR] {data.strip()}")
            )

        # Run server in background
        server_task = asyncio.create_task(run_server())

        # Wait a bit for server to start
        await asyncio.sleep(2)

        # Get the public URL
        url = await sandbox.expose_port(3000)
        print(f"\n✓ Server is accessible at: {url}")
        print("  You can visit this URL in your browser!")

        # Show all available URLs
        urls = sandbox.get_public_urls()
        print(f"\n✓ All available URLs:")
        for port, url in urls.items():
            print(f"  Port {port}: {url}")

        # Keep running for a bit
        print("\nServer will run for 30 seconds...")
        await asyncio.sleep(30)

        # Cancel server
        server_task.cancel()

    finally:
        await sandbox.disconnect()
        print("\n✓ Disconnected")


if __name__ == '__main__':
    asyncio.run(main())
