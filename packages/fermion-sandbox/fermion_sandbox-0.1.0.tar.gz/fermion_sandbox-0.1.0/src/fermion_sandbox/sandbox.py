"""Main Sandbox class for managing isolated code execution containers."""

import asyncio
from typing import Optional, Callable, Literal, Union, Dict
import httpx

from .api_client import ApiClient
from .websocket_client import SandboxWebSocket, StreamingTaskHandler
from .types import (
    ContainerDetails,
    DsaExecutionResult,
    DsaCodeExecutionEntry,
    Language,
    RunConfig,
    BootParams,
    RunLongRunningCommandRequest,
    RunLongRunningCommandData,
    EvalSmallCodeSnippetRequest,
    WebSocketResponsePayload,
    RunLongRunningCommandResponse,
    EvalSmallCodeSnippetResponse,
    GetRunningPlaygroundSessionDetailsParams,
    ReadyResponse,
    AttentionNeededResponse,
    OkSessionResponse,
    CodingTaskStatus,
    RunResult,
)
from .utils import encode_base64url


class CommandResult:
    """Result from command execution."""

    def __init__(self, stdout: str, stderr: str, exit_code: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code


class Sandbox:
    """Main Sandbox class for managing isolated code execution containers.

    The Sandbox class provides a complete interface for creating, managing, and interacting with
    secure, isolated code execution environments. Each sandbox runs in a containerized environment
    with its own filesystem, process space, and network isolation.

    Key features:
    - Isolated Linux containers for secure code execution
    - Real-time WebSocket communication for streaming output
    - File system operations (read/write)
    - Git repository cloning during initialization
    - Public URL exposure for web servers (ports 3000, 1337, 1338)
    - Persistent filesystem snapshots (optional)

    Example:
        ```python
        # Basic usage - create and connect to a new sandbox
        sandbox = Sandbox(api_key='your-api-key')
        await sandbox.create(should_backup_filesystem=False)

        # Run a simple command
        result = await sandbox.run_command(cmd='node', args=['--version'])
        print('Node version:', result.stdout)

        # Write and execute a file
        await sandbox.write_file(
            path='~/hello.js',
            content='console.log("Hello from sandbox!")'
        )
        output = await sandbox.run_command(cmd='node', args=['hello.js'])

        # Clean up when done
        await sandbox.disconnect()
        ```
    """

    def __init__(self, api_key: str) -> None:
        """Initialize Sandbox client.

        Args:
            api_key: API key for authentication with the Fermion sandbox service (required)

        Example:
            ```python
            # Initialize sandbox client
            sandbox = Sandbox(api_key='your-api-key')

            # Then create a new container
            await sandbox.create(g_backup_filesystem=False)

            # Or connect to existing snippet
            await sandbox.from_snippet('snippet-id-here')
            ```
        """
        self.api_key = api_key
        self.playground_session_id: Optional[str] = None
        self.playground_snippet_id: Optional[str] = None
        self.container_details: Optional[ContainerDetails] = None
        self.timeout: float = 30.0
        self.ws: Optional[SandboxWebSocket] = None

    async def create(
        self,
        should_backup_filesystem: bool,
        git_repo_url: Optional[str] = None
    ) -> Dict[str, str]:
        """Create a new sandbox container and establish connection.

        This method provisions a new container from scratch and establishes a WebSocket connection.
        The process includes:
        1. Creating a new playground snippet with the specified settings
        2. Starting a playground session for that snippet
        3. Waiting for container provisioning (polls until ready or timeout)
        4. Establishing WebSocket connection to the container
        5. Waiting for container server to be ready
        6. Cloning the git repository if provided

        Args:
            should_backup_filesystem: Whether to persist filesystem changes after shutdown
            git_repo_url: Optional git repository URL to clone after container is ready

        Returns:
            Dictionary with playgroundSnippetId key when the sandbox is ready

        Raises:
            Exception: If container provisioning times out (default: 30 seconds)
            Exception: If session creation fails or requires attention
            Exception: If WebSocket connection fails
            Exception: If git clone fails (when git_repo_url is provided)

        Example:
            ```python
            # Create basic sandbox
            sandbox = Sandbox(api_key='your-api-key')
            result = await sandbox.create(should_backup_filesystem=False)
            print('Created sandbox with snippet ID:', result['playgroundSnippetId'])

            # Create sandbox with git repository
            result = await sandbox.create(
                should_backup_filesystem=True,
                git_repo_url='https://github.com/user/repo.git'
            )
            ```
        """
        if self.is_connected():
            raise Exception("WebSocket already connected")
        
        api = ApiClient(self.api_key)

        try:
            # Create playground snippet
            boot_params = BootParams(
                source="empty",
                should_backup_filesystem=should_backup_filesystem
            )
            snippet_data = await api.create_playground_snippet(boot_params=boot_params)
            self.playground_snippet_id = snippet_data.playground_snippet_id

            # Start playground session
            session_data = await api.start_playground_session(
                playground_snippet_id=self.playground_snippet_id
            )

            # Handle attention-needed response
            if isinstance(session_data, AttentionNeededResponse):
                attention_type = session_data.attention_type
                if attention_type == "cannot-get-new":
                    raise Exception("Cannot get new session")
                elif attention_type == "can-terminate-and-get-new":
                    raise Exception("Can terminate and get new session")
                elif attention_type == "can-create-account-and-get-new":
                    raise Exception("Can create account and get new session")
                else:
                    raise Exception(f"Session creation requires attention: {attention_type}")

            if isinstance(session_data, OkSessionResponse):
                self.playground_session_id = session_data.playground_session_id
            else:
                raise Exception("Failed to get playground session ID from response")

            # Wait for container provisioning
            interval = 0.5
            max_attempts = int(self.timeout / interval)

            for _ in range(max_attempts):
                details_params = GetRunningPlaygroundSessionDetailsParams(
                    playground_session_id=self.playground_session_id,
                    is_waiting_for_upscale=False,
                    playground_type="PlaygroundSnippet",
                    playground_snippet_id=self.playground_snippet_id
                )
                details_data = await api.get_running_playground_session_details(params=details_params)

                if isinstance(details_data, ReadyResponse):
                    self.container_details = details_data.container_details

                    # Establish WebSocket connection
                    if self.container_details:
                        ws_url = f"wss://{self.container_details.subdomain}-13372.run-code.com"
                        self.ws = SandboxWebSocket(
                            url=ws_url,
                            token=self.container_details.playground_container_access_token
                        )
                        await self.ws.connect()

                        # Wait for container server ready
                        await self.ws.wait_for_next_future_websocket_event("ContainerServerReady", timeout=10.0)

                    # Clone git repository if provided
                    if git_repo_url and git_repo_url != '':
                        result = await self.run_streaming_command(
                            cmd='git',
                            args=['clone', git_repo_url],
                            on_stdout=lambda data: print(data.strip()),
                            on_stderr=lambda data: print(data.strip())
                        )
                        print(f"Git clone completed with exit code: {result.exit_code}")

                    return {"playgroundSnippetId": self.playground_snippet_id}

                await asyncio.sleep(interval)

            raise Exception("Provisioning timeout")

        finally:
            await api.close()

    async def from_snippet(self, playground_snippet_id: str) -> None:
        """Connect to an existing sandbox using a playground snippet ID.

        This method connects to an existing playground snippet that was previously created.
        Use this to reconnect to a sandbox that has persistent filesystem enabled, or to
        share sandbox environments between different sessions or users.

        Args:
            playground_snippet_id: The ID of an existing playground snippet

        Raises:
            Exception: If container provisioning times out
            Exception: If session creation fails or requires attention
            Exception: If the snippet ID is invalid or not found
            Exception: If WebSocket connection fails

        Example:
            ```python
            # Connect to existing sandbox
            sandbox = Sandbox(api_key='your-api-key')
            await sandbox.from_snippet('existing-snippet-id')

            # Now you can use the sandbox
            result = await sandbox.run_command(cmd='ls', args=['-la'])
            print(result.stdout)
            ```
        """
        if self.is_connected():
            raise Exception("WebSocket already connected")
        
        api = ApiClient(self.api_key)

        try:
            # Start playground session
            session_data = await api.start_playground_session(
                playground_snippet_id=playground_snippet_id
            )

            # Handle attention-needed response
            if isinstance(session_data, AttentionNeededResponse):
                attention_type = session_data.attention_type
                if attention_type == "cannot-get-new":
                    raise Exception("Cannot get new session")
                elif attention_type == "can-terminate-and-get-new":
                    raise Exception("Can terminate and get new session")
                elif attention_type == "can-create-account-and-get-new":
                    raise Exception("Can create account and get new session")
                else:
                    raise Exception(f"Session creation requires attention: {attention_type}")

            if isinstance(session_data, OkSessionResponse):
                self.playground_session_id = session_data.playground_session_id
            else:
                raise Exception("Failed to get playground session ID from response")

            # Wait for container provisioning
            interval = 0.5
            max_attempts = int(self.timeout / interval)

            for _ in range(max_attempts):
                details_params = GetRunningPlaygroundSessionDetailsParams(
                    playground_session_id=self.playground_session_id,
                    is_waiting_for_upscale=False,
                    playground_type="PlaygroundSnippet",
                    playground_snippet_id=playground_snippet_id
                )
                details_data = await api.get_running_playground_session_details(params=details_params)

                if isinstance(details_data, ReadyResponse):
                    self.container_details = details_data.container_details

                    # Establish WebSocket connection
                    if self.container_details:
                        ws_url = f"wss://{self.container_details.subdomain}-13372.run-code.com"
                        self.ws = SandboxWebSocket(
                            url=ws_url,
                            token=self.container_details.playground_container_access_token
                        )
                        await self.ws.connect()

                        # Wait for container server ready
                        await self.ws.wait_for_next_future_websocket_event("ContainerServerReady", timeout=10.0)

                    return

                await asyncio.sleep(interval)

            raise Exception("Provisioning timeout")

        finally:
            await api.close()

    async def disconnect(self) -> None:
        """Disconnect from the container and clean up resources.

        This closes the WebSocket connection and notifies the container server.
        Always call this when you're done with the sandbox to free up resources.

        Example:
            ```python
            sandbox = Sandbox(api_key='your-api-key')
            await sandbox.create(should_backup_filesystem=False)
            # ... do work ...
            await sandbox.disconnect()
            ```
        """
        if not self.is_connected():
            raise Exception(
                "Not connected to sandbox. Please call create() or from_snippet() first."
            )
        
        if self.ws:
            self.ws.disable_ws_auto_reconnect()

        if self.container_details:
            url = (
                f"https://{self.container_details.subdomain}-13372.run-code.com/disconnect-sandbox"
                f"?playground-container-access-token={self.container_details.playground_container_access_token}"
            )
            async with httpx.AsyncClient(verify=False) as client:
                try:
                    await client.get(url)
                except Exception as e:
                    print(f"Failed to disconnect from container: {e}")

        if self.ws:
            await self.ws.disconnect()
            self.ws = None

    async def get_file(self, path: str) -> httpx.Response:
        """Retrieve a file from the container filesystem.

        Args:
            path: Path to the file (passed as-is to the backend)

        Returns:
            Response object - use .text, .read(), etc.

        Raises:
            Exception: If file is not found (404)
            Exception: If container is not initialized
            Exception: If not connected to sandbox

        Example:
            ```python
            # Get as text
            response = await sandbox.get_file('~/output.txt')
            text = response.text
            print(text)

            # Get with absolute path
            response = await sandbox.get_file('/home/damner/code/data.bin')
            data = response.content
            ```
        """
        if not self.is_connected():
            raise Exception(
                "Not connected to sandbox. Please call create() or from_snippet() first."
            )
        
        if not self.container_details:
            raise Exception("No container found")

        url = (
            f"https://{self.container_details.subdomain}-13372.run-code.com/static-server"
            f"?full-path={path}"
            f"&playground-container-access-token={self.container_details.playground_container_access_token}"
        )

        # Create SSL context that allows connection even with certificate issues
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url)

            if not response.is_success:
                if response.status_code == 404:
                    raise Exception(f"File not found: {path}")
                raise Exception(f"Failed to get file: {response.status_code} {response.reason_phrase}")

            return response

    async def write_file(
        self,
        path: str,
        content: Union[str, bytes]
    ) -> None:
        """Write a file to the container filesystem.

        Args:
            path: Path where the file should be written (passed as-is to the backend)
            content: File content as string or bytes

        Raises:
            Exception: If container is not initialized
            Exception: If write operation fails
            Exception: If not connected to sandbox

        Example:
            ```python
            # Write text file
            await sandbox.write_file(
                path='~/script.js',
                content='console.log("Hello")'
            )

            # Write binary file with absolute path
            await sandbox.write_file(
                path='/home/damner/code/data.bin',
                content=bytes([1, 2, 3, 4])
            )
            ```
        """
        if not self.is_connected():
            raise Exception(
                "Not connected to sandbox. Please call create() or from_snippet() first."
            )
        
        if not self.container_details:
            raise Exception("No container found")

        url = (
            f"https://{self.container_details.subdomain}-13372.run-code.com/static-server"
            f"?full-path={path}"
            f"&playground-container-access-token={self.container_details.playground_container_access_token}"
        )

        # Create SSL context that allows connection even with certificate issues
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.put(url, content=content)

            if not response.is_success:
                error_text = response.text if hasattr(response, 'text') else response.reason_phrase
                raise Exception(f"Failed to set file: {response.status_code} {response.reason_phrase} - {error_text}")

    async def run_streaming_command(
        self,
        cmd: str,
        args: Optional[list[str]] = None,
        stdin: Optional[str] = None,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None
    ) -> CommandResult:
        """Execute a long-running command with streaming output.

        Use this for commands that produce continuous output (e.g., build processes, servers, watchers).
        Callbacks are invoked as data arrives. The coroutine completes when the command exits.

        Args:
            cmd: Command to execute (e.g., 'npm', 'git', 'node')
            args: Command arguments as list
            stdin: Optional standard input to send to the command
            on_stdout: Optional callback for stdout data chunks as they arrive
            on_stderr: Optional callback for stderr data chunks as they arrive

        Returns:
            CommandResult with stdout, stderr, and exit_code

        Raises:
            Exception: If WebSocket is not connected
            Exception: If command execution fails to start

        Example:
            ```python
            result = await sandbox.run_streaming_command(
                cmd='npm',
                args=['install', 'express'],
                on_stdout=lambda data: print(data.strip()),
                on_stderr=lambda data: print(data.strip())
            )
            print('Exit code:', result.exit_code)
            ```
        """
        if not self.is_connected():
            raise Exception(
                "Not connected to sandbox. Please call create() or from_snippet() first."
            )
        
        if not self.ws:
            raise Exception("Not connected")

        if args is None:
            args = []

        # Send command
        command_data = RunLongRunningCommandData(
            command=cmd,
            args=args,
            stdin=stdin
        )
        request = RunLongRunningCommandRequest(
            event_type="RunLongRunningCommand",
            data=command_data
        )
        
        # Exclude None values to match JavaScript behavior (undefined fields are omitted)
        request_dict = request.model_dump(by_alias=True, exclude_none=True)
        response = await self.ws.send(
            {"payload": request_dict},
            timeout=30.0
        )

        # Parse response
        if not isinstance(response, dict) or response.get("eventType") != "RunLongRunningCommand":
            raise Exception("Unexpected response event type")

        response_obj = RunLongRunningCommandResponse(**response)
        unique_task_id = response_obj.data.unique_task_id

        # Create future for completion
        future: asyncio.Future = asyncio.Future()
        stdout_buffer: list[str] = []
        stderr_buffer: list[str] = []

        def handle_stdout(data: str) -> None:
            stdout_buffer.append(data)
            if on_stdout:
                on_stdout(data)

        def handle_stderr(data: str) -> None:
            stderr_buffer.append(data)
            if on_stderr:
                on_stderr(data)

        def handle_close(exit_code: int) -> None:
            if not future.done():
                future.set_result(exit_code)

        # Register handler
        self.ws.add_streaming_task_handler(
            unique_task_id=unique_task_id,
            handler=StreamingTaskHandler(
                on_stdout=handle_stdout,
                on_stderr=handle_stderr,
                on_close=handle_close
            )
        )

        # Wait for completion
        exit_code = await future

        return CommandResult(
            stdout=''.join(stdout_buffer),
            stderr=''.join(stderr_buffer),
            exit_code=exit_code
        )

    async def run_command(
        self,
        cmd: str,
        args: Optional[list[str]] = None
    ) -> CommandResult:
        """Execute a short command and wait for completion.

        Use this for quick commands that complete within seconds (e.g., file operations, simple scripts).
        This command cannot run for more than 5 seconds.
        For long-running commands, use run_streaming_command() instead.

        Args:
            cmd: Command to execute
            args: Optional command arguments

        Returns:
            CommandResult with stdout and stderr strings

        Raises:
            Exception: If WebSocket is not connected
            Exception: If response type is unexpected

        Example:
            ```python
            result = await sandbox.run_command(
                cmd='ls',
                args=['-la', '/home/user']
            )
            print(result.stdout)
            print(result.stderr)
            ```
        """
        if not self.is_connected():
            raise Exception(
                "Not connected to sandbox. Please call create() or from_snippet() first."
            )
        
        if not self.ws:
            raise Exception("Not connected")

        if args is None:
            args = []

        full_command = f"{cmd} {' '.join(args)}" if args else cmd

        request = EvalSmallCodeSnippetRequest(
            event_type="EvalSmallCodeSnippetInsideContainer",
            command=full_command
        )
        response = await self.ws.send(
            {"payload": request.model_dump(by_alias=True)},
            timeout=30.0
        )

        # Parse response
        if not isinstance(response, dict) or response.get("eventType") != "EvalSmallCodeSnippetInsideContainer":
            raise Exception("Unexpected response event type")

        response_obj = EvalSmallCodeSnippetResponse(**response)
        return CommandResult(
            stdout=response_obj.stdout,
            stderr=response_obj.stderr
        )

    def get_session_id(self) -> Optional[str]:
        """Get the current playground session ID.
        
        Returns:
            The session ID or None if not initialized
        """
        return self.playground_session_id

    def get_container_details(self) -> Optional[ContainerDetails]:
        """Get the container connection details.

        Returns:
            Container details including subdomain and access token, or None if not initialized
        """
        return self.container_details

    def is_connected(self) -> bool:
        """Check if the WebSocket connection is active.

        Returns:
            True if connected, False otherwise
        """
        return self.ws.is_connected() if self.ws else False

    async def expose_port(
        self,
        port: Literal[3000, 1337, 1338]
    ) -> str:
        """Get the public URL for a specific port.

        The sandbox automatically exposes certain ports publicly for running web servers and APIs.
        Any service running on these ports inside the container will be accessible via HTTPS.
        Supported ports: 3000, 1337, 1338

        Args:
            port: Port number (must be 3000, 1337, or 1338)

        Returns:
            The public HTTPS URL for the specified port

        Raises:
            Exception: If container is not initialized
            Exception: If not connected to sandbox

        Example:
            ```python
            # Start a web server on port 3000
            await sandbox.write_file(
                path='~/server.js',
                content='''
                const http = require('http');
                http.createServer((req, res) => {
                  res.writeHead(200, {'Content-Type': 'text/plain'});
                  res.end('Hello World');
                }).listen(3000);
                console.log('Server running on port 3000');
                '''
            )

            # Start the server in the background
            asyncio.create_task(sandbox.run_streaming_command(
                cmd='node',
                args=['server.js'],
                on_stdout=lambda data: print(data)
            ))

            # Get the public URL
            url = await sandbox.expose_port(3000)
            print(f'Server accessible at: {url}')
            # Output: https://abc123-3000.run-code.com
            ```
        """
        if not self.is_connected():
            raise Exception(
                "Not connected to sandbox. Please call create() or from_snippet() first."
            )
        
        if not self.container_details:
            raise Exception("Not connected to sandbox. Please call create() or from_snippet() first.")

        return f"https://{self.container_details.subdomain}-{port}.run-code.com"

    def get_public_urls(self) -> Dict[int, str]:
        """Get all available public URLs for the container.

        Returns an object with public URLs for all supported ports (3000, 1337, 1338).
        These URLs are always available, but will only respond if a server is running on that port.

        Returns:
            Dictionary mapping port numbers to their public URLs

        Raises:
            Exception: If container is not initialized

        Example:
            ```python
            urls = sandbox.get_public_urls()
            print(urls)
            # Output:
            # {
            #   3000: 'https://abc123-3000.run-code.com',
            #   1337: 'https://abc123-1337.run-code.com',
            #   1338: 'https://abc123-1338.run-code.com'
            # }
            ```
        """
        if not self.container_details:
            raise Exception("No container found")

        return {
            3000: f"https://{self.container_details.subdomain}-3000.run-code.com",
            1337: f"https://{self.container_details.subdomain}-1337.run-code.com",
            1338: f"https://{self.container_details.subdomain}-1338.run-code.com",
        }

    async def quick_run(
        self,
        runtime: Literal['C', 'C++', 'Java', 'Python', 'Node.js', 'SQLite', 'MySQL', 'Go', 'Rust', '.NET'],
        source_code: str,
        stdin: Optional[str] = None,
        expected_output: Optional[str] = None,
        additional_files_as_zip: Optional[str] = None
    ) -> 'RunResult':
        """Execute code using the DSA execution API and return the results.

        This method provides a simple way to execute code in various languages without
        needing to set up a full sandbox container. It uses Fermion's DSA execution API
        which handles code compilation and execution in isolated environments.

        Args:
            runtime: Programming language (C, C++, Java, Python, Node.js, SQLite, MySQL, Go, Rust, .NET)
            source_code: Source code to execute (will be Base64URL encoded automatically)
            stdin: Optional standard input for the program (will be Base64URL encoded automatically)
            expected_output: Optional expected output for validation (will be Base64URL encoded automatically)
            additional_files_as_zip: Optional additional files as Base64URL encoded zip

        Returns:
            RunResult with execution details (run status, stdout/stderr, resource usage, compilation errors)

        Raises:
            Exception: If code submission fails
            Exception: If polling timeout is reached
            Exception: If API key is not set
            Exception: If not connected to sandbox

        Example:
            ```python
            # Simple Python execution
            sandbox = Sandbox(api_key='your-api-key')
            await sandbox.create(should_backup_filesystem=False)
            result = await sandbox.quick_run(
                runtime='Python',
                source_code='print("Hello, World!")'
            )
            print(result.program_run_data.stdout_base64_url_encoded)

            # C++ with input and expected output
            result = await sandbox.quick_run(
                runtime='C++',
                source_code='''
                    #include <iostream>
                    using namespace std;
                    int main() {
                      int a, b;
                      cin >> a >> b;
                      cout << a + b << endl;
                      return 0;
                    }
                ''',
                stdin='5 3',
                expected_output='8'
            )
            print(result.run_status)  # "successful" or "wrong-answer"
            ```
        """
        if not self.is_connected():
            raise Exception(
                "Not connected to sandbox. Please call create() or from_snippet() first."
            )
        
        api = ApiClient(self.api_key)

        runtime_map = {
            'C': Language.C,
            'C++': Language.CPP,
            'Java': Language.JAVA,
            'Python': Language.PYTHON,
            'Node.js': Language.NODEJS,
            'SQLite': Language.SQLITE,
            'Go': Language.GOLANG,
            'Rust': Language.RUST,
            '.NET': Language.DOTNET,
            'MySQL': Language.MYSQL
        }

        language = runtime_map[runtime]
        source_code_encoded = encode_base64url(source_code)
        stdin_encoded = encode_base64url(stdin) if stdin else ''
        expected_output_encoded = encode_base64url(expected_output) if expected_output else ''

        # Build runConfig exactly as TypeScript does
        run_config = RunConfig(
            custom_matcher_to_use_for_expected_output="ExactMatch",
            expected_output_as_base64_url_encoded=expected_output_encoded,
            stdin_string_as_base64_url_encoded=stdin_encoded,
            should_enable_per_process_and_thread_cpu_time_limit=False,
            should_enable_per_process_and_thread_memory_limit=False,
            should_allow_internet_access=False,
            compiler_flag_string="",
            max_file_size_in_kilobytes_files_created_or_modified=51200,
            stack_size_limit_in_kilobytes=65536,
            cpu_time_limit_in_milliseconds=2000,
            wall_time_limit_in_milliseconds=5000,
            memory_limit_in_kilobyte=512000,
            max_processes_and_or_threads=60
        )

        from .types import AdditionalFilesAsZip, RequestDsaExecutionRequest, DsaCodeExecutionEntry

        entry = DsaCodeExecutionEntry(
            language=language,
            run_config=run_config,
            source_code_as_base64_url_encoded=source_code_encoded,
            additional_files_as_zip=AdditionalFilesAsZip(
                type="base64url-encoding",
                base64_url_encoded_zip=additional_files_as_zip
            ) if additional_files_as_zip else None
        )

        try:
            # Pass entries array - request_dsa_execution will wrap it properly
            execution_request = RequestDsaExecutionRequest(entries=[entry])
            execution_response = await api.request_dsa_execution(params=execution_request)
            task_ids = execution_response.task_ids
            task_id = task_ids[0] if task_ids else None

            if not task_id:
                raise Exception("No task ID returned from execution request")

            poll_interval = 0.5
            max_attempts = 60

            for _ in range(max_attempts):
                result_response = await api.get_dsa_execution_result(
                    task_unique_ids=[task_id]
                )

                tasks = result_response.tasks
                if not tasks:
                    raise Exception("No result returned from result request")

                result = tasks[0]
                if result.coding_task_status == CodingTaskStatus.FINISHED:
                    if not result.run_result:
                        raise Exception("Execution finished but no result was returned")
                    return result.run_result

                await asyncio.sleep(poll_interval)

            raise Exception(f"Polling timeout: Execution did not complete after {max_attempts} attempts")

        finally:
            await api.close()
