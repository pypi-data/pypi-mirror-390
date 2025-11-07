import json
import base64
from typing import AsyncIterator

import google.genai as genai
from google.genai.types import Blob, Content, FunctionDeclaration, Part
from google.genai.types import Tool as GeminiTool
from google.oauth2 import service_account

from .model_abstract import (
    ContentType,
    EmbeddingRequest,
    EmbeddingResponse,
    FunctionCall,
    GenerateRequest,
    GenerateResponse,
    LLMModelAbstract,
    Message,
    ModelCapability,
    StreamChunk,
    Tool,
    ToolCall,
)


class VertexAIModel(LLMModelAbstract):
    """
    Vertex AI model implementation using google-genai SDK.

    Supports all models available on Vertex AI:
    - Gemini models (gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp)
    - Claude models via Vertex AI (claude-3-5-sonnet-v2@20241022, etc.)
    """

    def __init__(
        self,
        project_id: str,
        model_name: str = "gemini-2.5-flash",
        location: str = "us-central1",
        credentials: dict | None = None,
    ):
        """
        Initialize Vertex AI model via google-genai SDK.

        Args:
            model_name: Model identifier (e.g., "gemini-2.0-flash-exp", "claude-3-5-sonnet-v2@20241022")
            project_id: GCP project ID
            location: GCP location (us-central1 for Gemini, us-east5 for Claude)
            credentials: Optional service account credentials dict
        """
        self._model_name = model_name
        self._project_id = project_id
        self._location = location

        # Initialize client with Vertex AI
        client_kwargs = {
            "vertexai": True,
            "project": project_id,
            "location": location,
        }

        # Add credentials if provided
        if credentials:
            creds = service_account.Credentials.from_service_account_info(
                credentials, scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            client_kwargs["credentials"] = creds

        self.client = genai.Client(**client_kwargs)
        self._capabilities = self._determine_capabilities()

    def _determine_capabilities(self) -> ModelCapability:
        """Determine capabilities based on model name."""
        caps = (
            ModelCapability.TEXT_GENERATION
            | ModelCapability.STREAMING
            | ModelCapability.STRUCTURED_OUTPUT
            | ModelCapability.TOOL_CALLING
            | ModelCapability.VISION
            | ModelCapability.MULTIMODAL_INPUT
            | ModelCapability.AUDIO_INPUT
        )
        return caps

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str):
        self._model_name = value
        self._capabilities = self._determine_capabilities()

    @property
    def capabilities(self) -> ModelCapability:
        return self._capabilities

    def _convert_message(self, msg: Message) -> Content:
        """Convert internal Message to Vertex AI Content format."""
        parts = []

        if isinstance(msg.content, str):
            parts.append(Part(text=msg.content))
        else:
            # Multimodal content
            for part in msg.content:
                if part.type == ContentType.TEXT:
                    parts.append(Part(text=part.content))
                elif part.type == ContentType.IMAGE_URL:
                    # For URLs, we'd need to fetch and convert to inline data
                    parts.append(
                        Part(
                            inline_data=Blob(
                                mime_type=part.mime_type or "image/jpeg",
                                data=part.content.encode(),
                            )
                        )
                    )
                elif part.type == ContentType.IMAGE_BASE64:
                    # part.content is base64 string; Vertex needs raw bytes
                    raw = base64.b64decode(part.content, validate=True)
                    parts.append(
                        Part(
                            inline_data=Blob(
                                mime_type=part.mime_type or "image/png",
                                data=raw,
                            )
                        )
                    )
                elif part.type == ContentType.AUDIO_BASE64:
                    raw = base64.b64decode(part.content, validate=True)
                    parts.append(
                        Part(
                            inline_data=Blob(
                                mime_type=part.mime_type or "audio/wav",
                                data=raw,
                            )
                        )
                    )
                elif part.type == ContentType.FILE_BASE64:
                    raw = base64.b64decode(part.content, validate=True)
                    parts.append(
                        Part(
                            inline_data=Blob(
                                mime_type=part.mime_type or "application/octet-stream",
                                data=raw,
                            )
                        )
                    )
        return Content(role=msg.role, parts=parts)

    def _convert_tools(self, tools: list[Tool]) -> list[GeminiTool]:
        """Convert internal Tool definitions to Vertex AI format."""
        function_declarations = []
        for tool in tools:
            func_def = tool.function
            # Clean schema: remove $ref and $defs (Vertex AI doesn't support them)
            parameters = self._clean_json_schema(func_def.parameters)

            function_declarations.append(
                FunctionDeclaration(
                    name=func_def.name,
                    description=func_def.description,
                    parameters=parameters,
                )
            )

        return [GeminiTool(function_declarations=function_declarations)]

    def _clean_json_schema(self, schema: dict) -> dict:
        """
        Remove $ref and $defs from JSON Schema as Vertex AI doesn't support them.
        """
        if not isinstance(schema, dict):
            return schema

        cleaned = {}
        for key, value in schema.items():
            if key in ("$ref", "$defs", "definitions"):
                continue
            if isinstance(value, dict):
                cleaned[key] = self._clean_json_schema(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._clean_json_schema(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                cleaned[key] = value

        return cleaned

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Generate a response using Vertex AI."""
        await self.validate_request(request)

        # Separate system message from conversation
        system_instruction = None
        messages = []
        for msg in request.messages:
            if msg.role == "system":
                system_instruction = msg.content if isinstance(msg.content, str) else ""
            else:
                messages.append(self._convert_message(msg))

        config_kwargs = {}
        if request.temperature is not None:
            config_kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            config_kwargs["max_output_tokens"] = request.max_tokens
        if request.top_p is not None:
            config_kwargs["top_p"] = request.top_p
        if request.stop:
            config_kwargs["stop_sequences"] = request.stop
        if request.response_format:
            # Vertex AI uses response_mime_type and response_schema
            config_kwargs["response_mime_type"] = "application/json"
            if "schema" in request.response_format:
                config_kwargs["response_schema"] = self._clean_json_schema(
                    request.response_format["schema"]
                )

        # Build config object
        config = (
            genai.types.GenerateContentConfig(**config_kwargs)
            if config_kwargs
            else None
        )

        # Add tools to config if present
        if request.tools:
            if config is None:
                config = genai.types.GenerateContentConfig()
            config.tools = self._convert_tools(request.tools)

        # Add system instruction to config if present
        if system_instruction:
            if config is None:
                config = genai.types.GenerateContentConfig()
            config.system_instruction = system_instruction

        response = await self.client.aio.models.generate_content(
            model=self._model_name,
            contents=messages,
            config=config,
        )
        # Extract content
        content = None
        if response.text:
            content = response.text

        # Extract tool calls
        tool_calls = None
        if response.candidates and response.candidates[0].content.parts:
            function_calls = []
            for part in response.candidates[0].content.parts:
                if not hasattr(part, "function_call") or not part.function_call:
                    continue
                fc = part.function_call
                args_dict = dict(fc.args) if fc.args else {}
                function_calls.append(
                    ToolCall(
                        id=fc.name,
                        type="function",
                        function=FunctionCall(
                            name=fc.name,
                            arguments=json.dumps(args_dict),
                        ),
                    )
                )
            if function_calls:
                tool_calls = function_calls

        # Extract finish reason
        finish_reason = None
        if response.candidates:
            finish_reason = str(response.candidates[0].finish_reason)

        # Extract usage
        usage = None
        if response.usage_metadata:
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }

        return GenerateResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
        )

    async def generate_stream(
        self, request: GenerateRequest
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response using Vertex AI."""
        await self.validate_request(request)

        # Separate system message from conversation
        system_instruction = None
        messages = []
        for msg in request.messages:
            if msg.role == "system":
                system_instruction = msg.content if isinstance(msg.content, str) else ""
            else:
                messages.append(self._convert_message(msg))

        config_kwargs = {}
        if request.temperature is not None:
            config_kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            config_kwargs["max_output_tokens"] = request.max_tokens
        if request.top_p is not None:
            config_kwargs["top_p"] = request.top_p
        if request.stop:
            config_kwargs["stop_sequences"] = request.stop
        if request.response_format:
            config_kwargs["response_mime_type"] = "application/json"
            if "schema" in request.response_format:
                config_kwargs["response_schema"] = self._clean_json_schema(
                    request.response_format["schema"]
                )

        # Build config object
        config = (
            genai.types.GenerateContentConfig(**config_kwargs)
            if config_kwargs
            else None
        )

        # Add tools to config if present
        if request.tools:
            if config is None:
                config = genai.types.GenerateContentConfig()
            config.tools = self._convert_tools(request.tools)

        # Add system instruction to config if present
        if system_instruction:
            if config is None:
                config = genai.types.GenerateContentConfig()
            config.system_instruction = system_instruction

        model_name = self._model_name
        stream = await self.client.aio.models.generate_content_stream(
            model=model_name,
            contents=messages,
            config=config,
        )

        async for chunk in stream:
            content = None
            if chunk.text:
                content = chunk.text

            # Extract tool calls from chunk
            tool_calls = None
            if chunk.candidates and chunk.candidates[0].content.parts:
                function_calls = []
                for part in chunk.candidates[0].content.parts:
                    if not hasattr(part, "function_call") or not part.function_call:
                        continue
                    fc = part.function_call
                    args_dict = dict(fc.args) if fc.args else {}
                    function_calls.append(
                        ToolCall(
                            id=fc.name,
                            type="function",
                            function=FunctionCall(
                                name=fc.name,
                                arguments=json.dumps(args_dict),
                            ),
                        )
                    )
                if function_calls:
                    tool_calls = function_calls

            finish_reason = None
            if chunk.candidates:
                finish_reason = str(chunk.candidates[0].finish_reason)

            if content or tool_calls or finish_reason:
                yield StreamChunk(
                    content=content,
                    tool_calls=tool_calls,
                    finish_reason=finish_reason,
                )


class VertexEmbeddingModel(LLMModelAbstract):
    """
    Vertex AI embedding model using google-genai SDK with advanced features.
    """

    def __init__(
        self,
        project_id: str,
        model_name: str = "text-multilingual-embedding-002",
        location: str = "us-central1",
        credentials: dict | None = None,
        output_dimensionality: int | None = None,
        batch_size: int = 100,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ):
        self._model_name = model_name
        self._project_id = project_id
        self._location = location
        self._output_dimensionality = output_dimensionality
        self._batch_size = batch_size
        self._task_type = task_type

        client_kwargs = {
            "vertexai": True,
            "project": project_id,
            "location": location,
        }

        if credentials:
            creds = service_account.Credentials.from_service_account_info(
                credentials, scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            client_kwargs["credentials"] = creds

        self.client = genai.Client(**client_kwargs)

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def capabilities(self) -> ModelCapability:
        return ModelCapability.EMBEDDINGS

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        raise NotImplementedError("Embedding models do not support text generation")

    async def generate_stream(
        self, request: GenerateRequest
    ) -> AsyncIterator[StreamChunk]:
        raise NotImplementedError("Embedding models do not support text generation")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        inputs = [request.input] if isinstance(request.input, str) else request.input

        all_embeddings: list[list[float]] = []

        for i in range(0, len(inputs), self._batch_size):
            batch = inputs[i : i + self._batch_size]

            config_kwargs = {}
            if self._output_dimensionality:
                config_kwargs["output_dimensionality"] = self._output_dimensionality
            if self._task_type:
                config_kwargs["task_type"] = self._task_type

            config = (
                genai.types.EmbedContentConfig(**config_kwargs)
                if config_kwargs
                else None
            )

            try:
                response = await self.client.aio.models.embed_content(
                    model=self._model_name,
                    contents=batch,
                    config=config,
                )
            except Exception as e:
                raise Exception(f"Failed to embed batch: {e}")

            embeddings = [emb.values for emb in response.embeddings]
            all_embeddings.extend(embeddings)

        return EmbeddingResponse(
            embeddings=all_embeddings,
            usage=None,
        )
