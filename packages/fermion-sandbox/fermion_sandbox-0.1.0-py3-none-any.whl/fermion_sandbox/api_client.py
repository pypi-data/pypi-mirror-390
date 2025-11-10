"""API client for Fermion backend."""

from typing import Any, Dict, List, Optional, Union
import httpx

from .types import (
    ContainerDetails,
    RunConfig,
    DsaExecutionResult,
    DsaCodeExecutionEntry,
    BootParams,
    CreatePlaygroundSnippetRequest,
    CreatePlaygroundSnippetResponse,
    StartPlaygroundSessionRequest,
    StartPlaygroundSessionResponse,
    AttentionNeededResponse,
    OkSessionResponse,
    GetRunningPlaygroundSessionDetailsParams,
    GetRunningPlaygroundSessionDetailsRequest,
    GetRunningPlaygroundSessionDetailsResponse,
    WaitingForUpscaleResponse,
    ReadyResponse,
    RequestDsaExecutionRequest,
    RequestDsaExecutionResponse,
    GetDsaExecutionResultRequest,
    GetDsaExecutionResultResponse,
)


class ApiClient:
    """Client for Fermion API."""

    def __init__(self, api_key: Optional[str]) -> None:
        """Initialize API client.

        Args:
            api_key: API key for authentication

        Raises:
            ValueError: If API key is not provided
        """
        if not api_key or api_key.strip() == '':
            raise ValueError(
                'API key is required. Please provide a valid API key when creating the sandbox.'
            )

        self.api_key = api_key
        self.base_url = 'https://backend.codedamn.com/api'
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def _call(
        self,
        function_name: str,
        namespace: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make an API call.

        Args:
            function_name: Name of the function to call
            namespace: API namespace (public or fermion-user)
            data: Request data

        Returns:
            Response data

        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the API returns an error
        """
        request = {
            "context": {"namespace": namespace, "functionName": function_name},
            "data": data
        }

        response = await self.client.post(
            self.base_url,
            json={"data": [request]},
            headers={
                "Content-Type": "application/json",
                "Fermion-Api-Key": self.api_key
            }
        )

        response.raise_for_status()
        raw_response = response.json()

        if not raw_response or len(raw_response) == 0:
            raise ValueError("Empty response from API")

        api_response = raw_response[0]

        # Handle API errors
        if api_response.get("output", {}).get("status") == "error":
            error_message = api_response["output"].get("errorMessage", "Unknown error")
            raise ValueError(f"API error: {error_message}")

        return api_response["output"]["data"]

    async def create_playground_snippet(
        self,
        boot_params: BootParams
    ) -> CreatePlaygroundSnippetResponse:
        """Create a new playground snippet.

        Args:
            boot_params: Boot parameters for the snippet

        Returns:
            CreatePlaygroundSnippetResponse with snippet ID
        """
        request = CreatePlaygroundSnippetRequest(boot_params=boot_params)
        data = await self._call(
            function_name="create-new-playground-snippet",
            namespace="public",
            data=request.model_dump(by_alias=True)
        )
        return CreatePlaygroundSnippetResponse(**data)

    async def start_playground_session(
        self,
        playground_snippet_id: str
    ) -> StartPlaygroundSessionResponse:
        """Start a playground session.

        Args:
            playground_snippet_id: ID of the playground snippet

        Returns:
            StartPlaygroundSessionResponse with session details
        """
        request = StartPlaygroundSessionRequest(playground_snippet_id=playground_snippet_id)
        data = await self._call(
            function_name="start-playground-session",
            namespace="public",
            data=request.model_dump(by_alias=True)
        )
        # The response is wrapped in a "response" field
        response_data = data.get("response", data)
        # Parse the response - it can be either AttentionNeededResponse or OkSessionResponse
        if response_data.get("status") == "attention-needed":
            return AttentionNeededResponse(**response_data)
        else:
            return OkSessionResponse(**response_data)

    async def get_running_playground_session_details(
        self,
        params: GetRunningPlaygroundSessionDetailsParams
    ) -> GetRunningPlaygroundSessionDetailsResponse:
        """Get details of a running playground session.

        Args:
            params: Query parameters

        Returns:
            GetRunningPlaygroundSessionDetailsResponse with session details
        """
        request = GetRunningPlaygroundSessionDetailsRequest(params=params)
        data = await self._call(
            function_name="get-running-playground-session-details",
            namespace="fermion-user",
            data=request.model_dump(by_alias=True)
        )
        # The response is wrapped in a "response" field
        response_data = data.get("response", data)
        # Parse the response - it can be either WaitingForUpscaleResponse or ReadyResponse
        if response_data.get("isWaitingForUpscale") is True:
            return WaitingForUpscaleResponse(**response_data)
        else:
            return ReadyResponse(**response_data)

    async def request_dsa_execution(
        self,
        params: RequestDsaExecutionRequest
    ) -> RequestDsaExecutionResponse:
        """Request DSA code execution.

        Args:
            params: Request parameters with entries

        Returns:
            RequestDsaExecutionResponse with task IDs
        """
        # Validate entries with Pydantic (matches Zod validation in TypeScript)
        validated_entries = []
        
        for entry in params.entries:
            # Convert to dict - exclude_none=True to match TypeScript behavior
            # TypeScript .optional() means undefined fields are omitted from JSON
            validated_entry = entry.model_dump(by_alias=True, exclude_none=True)
            # Ensure language is string value, not enum
            if isinstance(validated_entry.get("language"), type(params.entries[0].language)):
                validated_entry["language"] = validated_entry["language"].value
            validated_entries.append(validated_entry)
        
        # Pass just the entries - _call will wrap it in "data"
        validated_params = {"entries": validated_entries}

        result = await self._call(
            function_name="request-dsa-code-execution-batch",
            namespace="public",
            data=validated_params
        )
        return RequestDsaExecutionResponse(**result)

    async def get_dsa_execution_result(
        self,
        task_unique_ids: List[str]
    ) -> GetDsaExecutionResultResponse:
        """Get DSA execution result.

        Args:
            task_unique_ids: List of task IDs

        Returns:
            GetDsaExecutionResultResponse with execution results
        """
        request = GetDsaExecutionResultRequest(task_unique_ids=task_unique_ids)
        result = await self._call(
            function_name="get-dsa-code-execution-result-batch",
            namespace="public",
            data=request.model_dump(by_alias=True)
        )
        return GetDsaExecutionResultResponse(**result)
