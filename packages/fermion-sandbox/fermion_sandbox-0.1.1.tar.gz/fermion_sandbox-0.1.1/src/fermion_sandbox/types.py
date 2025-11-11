"""Type definitions and Pydantic models for Fermion Sandbox SDK."""

from typing import Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field


class ContainerDetails(BaseModel):
    """Container connection details."""
    playground_container_access_token: str = Field(alias="playgroundContainerAccessToken")
    subdomain: str


class RunConfig(BaseModel):
    """Configuration for code execution."""
    custom_matcher_to_use_for_expected_output: str = Field(
        default="ExactMatch",
        alias="customMatcherToUseForExpectedOutput"
    )
    expected_output_as_base64_url_encoded: str = Field(
        default="",
        alias="expectedOutputAsBase64UrlEncoded"
    )
    stdin_string_as_base64_url_encoded: str = Field(
        default="",
        alias="stdinStringAsBase64UrlEncoded"
    )
    callback_url_on_execution_completion: Optional[str] = Field(
        default=None,
        alias="callbackUrlOnExecutionCompletion"
    )
    should_enable_per_process_and_thread_cpu_time_limit: bool = Field(
        default=False,
        alias="shouldEnablePerProcessAndThreadCpuTimeLimit"
    )
    should_enable_per_process_and_thread_memory_limit: bool = Field(
        default=False,
        alias="shouldEnablePerProcessAndThreadMemoryLimit"
    )
    should_allow_internet_access: bool = Field(
        default=False,
        alias="shouldAllowInternetAccess"
    )
    compiler_flag_string: str = Field(default="", alias="compilerFlagString")
    max_file_size_in_kilobytes_files_created_or_modified: int = Field(
        default=51200,
        alias="maxFileSizeInKilobytesFilesCreatedOrModified"
    )
    stack_size_limit_in_kilobytes: int = Field(
        default=65536,
        alias="stackSizeLimitInKilobytes"
    )
    cpu_time_limit_in_milliseconds: int = Field(
        default=2000,
        alias="cpuTimeLimitInMilliseconds"
    )
    wall_time_limit_in_milliseconds: int = Field(
        default=5000,
        alias="wallTimeLimitInMilliseconds"
    )
    memory_limit_in_kilobyte: int = Field(
        default=512000,
        alias="memoryLimitInKilobyte"
    )
    max_processes_and_or_threads: int = Field(
        default=60,
        alias="maxProcessesAndOrThreads"
    )

    class Config:
        populate_by_name = True


class Language(str, Enum):
    """Supported programming languages for quick execution."""
    C = "C"
    CPP = "Cpp"
    JAVA = "Java"
    PYTHON = "Python"
    NODEJS = "Nodejs"
    SQLITE = "Sqlite_3_48_0"
    MYSQL = "Mysql_8"
    GOLANG = "Golang_1_19"
    RUST = "Rust_1_87"
    DOTNET = "Dotnet_8"


class RunStatus(str, Enum):
    """Execution result status."""
    SUCCESSFUL = "successful"
    COMPILATION_ERROR = "compilation-error"
    TIME_LIMIT_EXCEEDED = "time-limit-exceeded"
    WRONG_ANSWER = "wrong-answer"
    NON_ZERO_EXIT_CODE = "non-zero-exit-code"
    DIED_SIGSEV = "died-sigsev"
    DIED_SIGXFSZ = "died-sigxfsz"
    DIED_SIGFPE = "died-sigfpe"
    DIED_SIGABRT = "died-sigabrt"
    INTERNAL_ISOLATE_ERROR = "internal-isolate-error"
    UNKNOWN = "unknown"


class ProgramRunData(BaseModel):
    """Program execution data (Base64URL encoded)."""
    cpu_time_used_in_milliseconds: int = Field(alias="cpuTimeUsedInMilliseconds")
    wall_time_used_in_milliseconds: int = Field(alias="wallTimeUsedInMilliseconds")
    memory_used_in_kilobyte: int = Field(alias="memoryUsedInKilobyte")
    exit_signal: int = Field(alias="exitSignal")
    exit_code: int = Field(alias="exitCode")
    stdout_base64_url_encoded: Optional[str] = Field(alias="stdoutBase64UrlEncoded")
    stderr_base64_url_encoded: Optional[str] = Field(alias="stderrBase64UrlEncoded")

    class Config:
        populate_by_name = True


class DecodedProgramRunData(BaseModel):
    """Program execution data with decoded strings (not Base64URL)."""
    cpu_time_used_in_milliseconds: int
    wall_time_used_in_milliseconds: int
    memory_used_in_kilobyte: int
    exit_signal: int
    exit_code: int
    stdout: str  # Already decoded from Base64URL
    stderr: str  # Already decoded from Base64URL


class RunResult(BaseModel):
    """Execution result details (Base64URL encoded)."""
    compiler_output_after_compilation_base64_url_encoded: Optional[str] = Field(
        alias="compilerOutputAfterCompilationBase64UrlEncoded"
    )
    finished_at: str = Field(alias="finishedAt")
    run_status: RunStatus = Field(alias="runStatus")
    program_run_data: Optional[ProgramRunData] = Field(alias="programRunData")

    class Config:
        populate_by_name = True


class DecodedRunResult(BaseModel):
    """Execution result with decoded strings (not Base64URL).

    This matches the TypeScript SDK's DecodedRunResult type.
    All Base64URL-encoded strings are automatically decoded to regular strings.
    """
    compiler_output_after_compilation: Optional[str]  # Already decoded from Base64URL
    finished_at: str
    run_status: RunStatus
    program_run_data: Optional[DecodedProgramRunData]


class CodingTaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "Pending"
    PROCESSING = "Processing"
    FINISHED = "Finished"


class DsaExecutionResult(BaseModel):
    """Result from DSA code execution."""
    task_unique_id: str = Field(alias="taskUniqueId")
    source_code_as_base64_url_encoded: Optional[str] = Field(
        default=None,
        alias="sourceCodeAsBase64UrlEncoded"
    )
    language: str
    run_config: RunConfig = Field(alias="runConfig")
    coding_task_status: CodingTaskStatus = Field(alias="codingTaskStatus")
    run_result: Optional[RunResult] = Field(alias="runResult")

    class Config:
        populate_by_name = True


class AdditionalFilesAsZip(BaseModel):
    """Additional files as a zip archive."""
    type: Literal["base64url-encoding"] = "base64url-encoding"
    base64_url_encoded_zip: str = Field(alias="base64UrlEncodedZip")

    class Config:
        populate_by_name = True


class DsaCodeExecutionEntry(BaseModel):
    """Entry for DSA code execution request."""
    language: Language
    run_config: RunConfig = Field(alias="runConfig")
    source_code_as_base64_url_encoded: str = Field(alias="sourceCodeAsBase64UrlEncoded")
    additional_files_as_zip: Optional[AdditionalFilesAsZip] = Field(
        default=None,
        alias="additionalFilesAsZip"
    )

    class Config:
        populate_by_name = True


# WebSocket request payload types
class RunLongRunningCommandData(BaseModel):
    """Data for RunLongRunningCommand request."""
    command: str
    args: list[str]
    stdin: Optional[str] = None


class RunLongRunningCommandRequest(BaseModel):
    """Request to start a long-running command with streaming output."""
    event_type: Literal["RunLongRunningCommand"] = Field(alias="eventType")
    data: RunLongRunningCommandData

    class Config:
        populate_by_name = True


class EvalSmallCodeSnippetRequest(BaseModel):
    """Request to execute a quick command and get complete output."""
    event_type: Literal["EvalSmallCodeSnippetInsideContainer"] = Field(alias="eventType")
    command: str

    class Config:
        populate_by_name = True


class HealthPingRequest(BaseModel):
    """Keep-alive ping to maintain connection."""
    event_type: Literal["HealthPing"] = Field(alias="eventType")

    class Config:
        populate_by_name = True


# Union type for all WebSocket request payloads
WebSocketRequestPayload = Union[
    RunLongRunningCommandRequest,
    EvalSmallCodeSnippetRequest,
    HealthPingRequest,
]


# WebSocket response payload types
class RunLongRunningCommandResponseData(BaseModel):
    """Data for RunLongRunningCommand response."""
    unique_task_id: str = Field(alias="uniqueTaskId")
    process_id: int = Field(alias="processId")

    class Config:
        populate_by_name = True


class RunLongRunningCommandResponse(BaseModel):
    """Response confirming long-running command started."""
    event_type: Literal["RunLongRunningCommand"] = Field(alias="eventType")
    data: RunLongRunningCommandResponseData

    class Config:
        populate_by_name = True


class EvalSmallCodeSnippetResponse(BaseModel):
    """Response with complete command output."""
    event_type: Literal["EvalSmallCodeSnippetInsideContainer"] = Field(alias="eventType")
    stdout: str
    stderr: str

    class Config:
        populate_by_name = True


class HealthPingResponse(BaseModel):
    """Health ping acknowledgment."""
    event_type: Literal["HealthPing"] = Field(alias="eventType")
    status: Literal["healthy"]

    class Config:
        populate_by_name = True


class StreamLongRunningTaskEventIoDetails(BaseModel):
    """IO event details for streaming task."""
    type: Literal["io"]
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class StreamLongRunningTaskEventCloseDetails(BaseModel):
    """Close event details for streaming task."""
    type: Literal["close"]
    code: Optional[int] = None
    error: Optional[str] = None


StreamLongRunningTaskEventDetails = Union[
    StreamLongRunningTaskEventIoDetails,
    StreamLongRunningTaskEventCloseDetails,
]


class StreamLongRunningTaskEventResponse(BaseModel):
    """Streaming event for long-running command output."""
    event_type: Literal["StreamLongRunningTaskEvent"] = Field(alias="eventType")
    unique_task_id: str = Field(alias="uniqueTaskId")
    process_id: int = Field(alias="processId")
    event_details: StreamLongRunningTaskEventDetails = Field(alias="eventDetails")

    class Config:
        populate_by_name = True


class ContainerServerReadyResponse(BaseModel):
    """Response when container server is ready."""
    event_type: Literal["ContainerServerReady"] = Field(alias="eventType")

    class Config:
        populate_by_name = True


# Union type for all WebSocket response payloads
WebSocketResponsePayload = Union[
    RunLongRunningCommandResponse,
    EvalSmallCodeSnippetResponse,
    HealthPingResponse,
    StreamLongRunningTaskEventResponse,
    ContainerServerReadyResponse,
]


# API request/response types
class BootParams(BaseModel):
    """Boot parameters for creating a playground snippet."""
    source: Literal["empty"]
    should_backup_filesystem: bool = Field(alias="shouldBackupFilesystem")

    class Config:
        populate_by_name = True


class CreatePlaygroundSnippetRequest(BaseModel):
    """Request to create a new playground snippet."""
    boot_params: BootParams = Field(alias="bootParams")

    class Config:
        populate_by_name = True


class CreatePlaygroundSnippetResponse(BaseModel):
    """Response from creating a playground snippet."""
    playground_snippet_id: str = Field(alias="playgroundSnippetId")

    class Config:
        populate_by_name = True


class StartPlaygroundSessionRequest(BaseModel):
    """Request to start a playground session."""
    playground_snippet_id: str = Field(alias="playgroundSnippetId")

    class Config:
        populate_by_name = True


class AttentionNeededResponse(BaseModel):
    """Response when attention is needed."""
    status: Literal["attention-needed"]
    user_type: Literal["fermion-user", "codedamn-user", "unknown"] = Field(alias="userType")
    attention_type: Literal[
        "cannot-get-new",
        "can-terminate-and-get-new",
        "can-create-account-and-get-new"
    ] = Field(alias="attentionType")
    is_vpn_found: bool = Field(alias="isVpnFound")
    is_limit_exceeded: bool = Field(alias="isLimitExceeded")

    class Config:
        populate_by_name = True


class OkSessionResponse(BaseModel):
    """Response when session creation is OK."""
    status: Literal["ok"]
    playground_session_id: str = Field(alias="playgroundSessionId")

    class Config:
        populate_by_name = True


StartPlaygroundSessionResponse = Union[AttentionNeededResponse, OkSessionResponse]


class GetRunningPlaygroundSessionDetailsParams(BaseModel):
    """Parameters for getting running playground session details."""
    playground_session_id: str = Field(alias="playgroundSessionId")
    is_waiting_for_upscale: bool = Field(alias="isWaitingForUpscale")
    playground_type: Literal["PlaygroundSnippet"] = Field(alias="playgroundType")
    playground_snippet_id: str = Field(alias="playgroundSnippetId")

    class Config:
        populate_by_name = True


class GetRunningPlaygroundSessionDetailsRequest(BaseModel):
    """Request to get running playground session details."""
    params: GetRunningPlaygroundSessionDetailsParams


class WaitingForUpscaleResponse(BaseModel):
    """Response when waiting for upscale."""
    is_waiting_for_upscale: Literal[True] = Field(alias="isWaitingForUpscale")

    class Config:
        populate_by_name = True


class ReadyResponse(BaseModel):
    """Response when container is ready."""
    is_waiting_for_upscale: Literal[False] = Field(alias="isWaitingForUpscale")
    container_details: ContainerDetails = Field(alias="containerDetails")

    class Config:
        populate_by_name = True


GetRunningPlaygroundSessionDetailsResponse = Union[
    WaitingForUpscaleResponse,
    ReadyResponse,
]


class RequestDsaExecutionRequest(BaseModel):
    """Request for DSA code execution."""
    entries: list[DsaCodeExecutionEntry]


class RequestDsaExecutionResponse(BaseModel):
    """Response from DSA execution request."""
    task_ids: list[str] = Field(alias="taskIds")

    class Config:
        populate_by_name = True


class GetDsaExecutionResultRequest(BaseModel):
    """Request to get DSA execution result."""
    task_unique_ids: list[str] = Field(alias="taskUniqueIds")

    class Config:
        populate_by_name = True


class GetDsaExecutionResultResponse(BaseModel):
    """Response with DSA execution results."""
    tasks: list[DsaExecutionResult]
