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
        await sandbox.create(should_backup_filesystem=False)

        # Create HTTP server
        server_code = """const http = require('http');
const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Hello from Fermion Sandbox!\\n');
});
server.listen(3000, () => console.log('Server running on port 3000'));
"""

        await sandbox.write_file(path='/home/damner/server.js', content=server_code)

        # Start server in background
        server_task = asyncio.create_task(
            sandbox.run_streaming_command(
                cmd='bash',
                args=['-c', 'node ~/server.js'],
                on_stdout=lambda data: print(f"[SERVER] {data.strip()}"),
                on_stderr=lambda data: print(f"[ERROR] {data.strip()}")
            )
        )

        await asyncio.sleep(2)

        # Get public URL
        url = await sandbox.expose_port(3000)
        print(f"✓ Server accessible at: {url}")

        # Keep server running
        await asyncio.sleep(30)

        # Stop server
        if not server_task.done():
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

    finally:
        await sandbox.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
