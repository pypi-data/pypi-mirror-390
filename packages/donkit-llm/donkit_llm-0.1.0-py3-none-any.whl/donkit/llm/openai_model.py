from typing import AsyncIterator

from openai import AsyncAzureOpenAI, AsyncOpenAI

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


class OpenAIModel(LLMModelAbstract):
    """OpenAI model implementation supporting GPT-4, GPT-3.5, etc."""

    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: str | None = None,
        organization: str | None = None,
    ):
        """
        Initialize OpenAI model.

        Args:
            model_name: Model identifier (e.g., "gpt-4o", "gpt-4o-mini")
            api_key: OpenAI API key
            base_url: Optional custom base URL
            organization: Optional organization ID
        """
        self._model_name = model_name
        self._init_client(api_key, base_url, organization)
        self._capabilities = self._determine_capabilities()

    def _init_client(
        self,
        api_key: str,
        base_url: str | None = None,
        organization: str | None = None,
    ) -> None:
        """Initialize the OpenAI client. Can be overridden by subclasses."""
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            organization=organization,
        )

    def _determine_capabilities(self) -> ModelCapability:
        """Determine capabilities based on model name."""
        caps = (
            ModelCapability.TEXT_GENERATION
            | ModelCapability.STREAMING
            | ModelCapability.STRUCTURED_OUTPUT
            | ModelCapability.TOOL_CALLING
        )

        model_lower = self._model_name.lower()

        # Vision models (GPT-4o, GPT-4 Turbo, GPT-5, etc.)
        if any(
            x in model_lower
            for x in ["gpt-4o", "gpt-4-turbo", "gpt-4-vision", "gpt-5", "o1", "o3"]
        ):
            caps |= ModelCapability.VISION | ModelCapability.MULTIMODAL_INPUT

        # Audio models
        if "audio" in model_lower:
            caps |= ModelCapability.AUDIO_INPUT | ModelCapability.MULTIMODAL_INPUT

        return caps

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str):
        """
        Set new model name and recalculate capabilities.

        Args:
            value: New model name
        """
        self._model_name = value
        # Recalculate capabilities based on new model name
        self._capabilities = self._determine_capabilities()

    @property
    def capabilities(self) -> ModelCapability:
        return self._capabilities

    def _convert_message(self, msg: Message) -> dict:
        """Convert internal Message to OpenAI format."""
        result = {"role": msg.role}

        # Handle content
        if isinstance(msg.content, str):
            result["content"] = msg.content
        else:
            # Multimodal content
            content_parts = []
            for part in msg.content:
                if part.type == ContentType.TEXT:
                    content_parts.append({"type": "text", "text": part.content})
                elif part.type == ContentType.IMAGE_URL:
                    content_parts.append(
                        {"type": "image_url", "image_url": {"url": part.content}}
                    )
                elif part.type == ContentType.IMAGE_BASE64:
                    content_parts.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{part.mime_type or 'image/jpeg'};base64,{part.content}"
                            },
                        }
                    )
                # Add more content types as needed
            result["content"] = content_parts

        # Handle tool calls
        if msg.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]

        # Handle tool responses
        if msg.tool_call_id:
            result["tool_call_id"] = msg.tool_call_id

        if msg.name:
            result["name"] = msg.name

        return result

    def _convert_tools(self, tools: list[Tool]) -> list[dict]:
        """Convert internal Tool definitions to OpenAI format."""
        return [
            {
                "type": tool.type,
                "function": {
                    "name": tool.function.name,
                    "description": tool.function.description,
                    "parameters": tool.function.parameters,
                    **(
                        {"strict": tool.function.strict}
                        if tool.function.strict is not None
                        else {}
                    ),
                },
            }
            for tool in tools
        ]

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Generate a response using OpenAI API."""
        await self.validate_request(request)

        messages = [self._convert_message(msg) for msg in request.messages]

        kwargs = {
            "model": self._model_name,
            "messages": messages,
        }

        # if request.temperature is not None:
        #     kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_completion_tokens"] = (
                request.max_tokens if request.max_tokens <= 16384 else 16384
            )
        if request.top_p is not None:
            kwargs["top_p"] = request.top_p
        if request.stop:
            kwargs["stop"] = request.stop
        if request.tools:
            kwargs["tools"] = self._convert_tools(request.tools)
            # Only add tool_choice if tools are present
            if request.tool_choice:
                # Validate tool_choice - OpenAI only supports 'none', 'auto', 'required', or dict
                if isinstance(request.tool_choice, str):
                    if request.tool_choice in ("none", "auto", "required"):
                        kwargs["tool_choice"] = request.tool_choice
                    else:
                        # Invalid string value - default to 'auto'
                        kwargs["tool_choice"] = "auto"
                elif isinstance(request.tool_choice, dict):
                    kwargs["tool_choice"] = request.tool_choice
        if request.response_format:
            kwargs["response_format"] = request.response_format

        response = await self.client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        message = choice.message

        # Extract content
        content = message.content

        # Extract tool calls
        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    type=tc.type,
                    function=FunctionCall(
                        name=tc.function.name, arguments=tc.function.arguments
                    ),
                )
                for tc in message.tool_calls
            ]

        return GenerateResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            if response.usage
            else None,
        )

    async def generate_stream(
        self, request: GenerateRequest
    ) -> AsyncIterator[StreamChunk]:
        """Generate a streaming response using OpenAI API."""
        await self.validate_request(request)

        messages = [self._convert_message(msg) for msg in request.messages]

        kwargs = {
            "model": self._model_name,
            "messages": messages,
            "stream": True,
        }

        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            kwargs["top_p"] = request.top_p
        if request.stop:
            kwargs["stop"] = request.stop
        if request.tools:
            kwargs["tools"] = self._convert_tools(request.tools)
            # Only add tool_choice if tools are present
            if request.tool_choice:
                # Validate tool_choice - OpenAI only supports 'none', 'auto', 'required', or dict
                if isinstance(request.tool_choice, str):
                    if request.tool_choice in ("none", "auto", "required"):
                        kwargs["tool_choice"] = request.tool_choice
                    else:
                        # Invalid string value - default to 'auto'
                        kwargs["tool_choice"] = "auto"
                elif isinstance(request.tool_choice, dict):
                    kwargs["tool_choice"] = request.tool_choice
        if request.response_format:
            kwargs["response_format"] = request.response_format

        stream = await self.client.chat.completions.create(**kwargs)

        async for chunk in stream:
            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            content = delta.content if delta.content else None
            finish_reason = choice.finish_reason

            # Handle tool calls in streaming
            tool_calls = None
            if delta.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id or "",
                        type=tc.type or "function",
                        function=FunctionCall(
                            name=tc.function.name or "",
                            arguments=tc.function.arguments or "",
                        ),
                    )
                    for tc in delta.tool_calls
                ]

            yield StreamChunk(
                content=content,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
            )


class AzureOpenAIModel(OpenAIModel):
    """Azure OpenAI model implementation."""

    def __init__(
        self,
        model_name: str,
        api_key: str,
        azure_endpoint: str,
        deployment_name: str,
        api_version: str = "2024-08-01-preview",
    ):
        """
        Initialize Azure OpenAI model.

        Args:
            model_name: Model identifier for capability detection
            api_key: Azure OpenAI API key
            azure_endpoint: Azure endpoint URL
            deployment_name: Azure deployment name
            api_version: API version
        """
        # Store Azure-specific parameters before calling super().__init__()
        self._api_key = api_key
        self._azure_endpoint = azure_endpoint
        self._api_version = api_version
        self._base_model_name = model_name
        self._deployment_name = deployment_name

        # Call parent constructor (will call our overridden _init_client)
        super().__init__(model_name, api_key)

    def _init_client(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        organization: str | None = None,
    ) -> None:
        """Initialize Azure OpenAI client."""
        self.client = AsyncAzureOpenAI(
            api_key=self._api_key,
            azure_endpoint=self._azure_endpoint,
            api_version=self._api_version,
            azure_deployment=self._deployment_name,
        )

    def _determine_capabilities(self) -> ModelCapability:
        """Determine capabilities based on base model name."""
        caps = (
            ModelCapability.TEXT_GENERATION
            | ModelCapability.STREAMING
            | ModelCapability.TOOL_CALLING
            | ModelCapability.STRUCTURED_OUTPUT
            | ModelCapability.MULTIMODAL_INPUT
        )
        if "vision" in self._base_model_name.lower() or "4o" in self._base_model_name:
            caps |= ModelCapability.MULTIMODAL_INPUT
        return caps

    @property
    def deployment_name(self) -> str:
        """Get current deployment name."""
        return self._deployment_name

    @deployment_name.setter
    def deployment_name(self, value: str):
        """
        Set new deployment name and reinitialize client.

        Args:
            value: New deployment name
        """
        self._deployment_name = value
        # Reinitialize client with new deployment name
        self._init_client(self._api_key)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Generate a response using Azure OpenAI API with parameter adaptation."""
        # Override to adapt parameters where needed, then call parent
        return await super().generate(request)


class OpenAIEmbeddingModel(LLMModelAbstract):
    """OpenAI embedding model implementation."""

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialize OpenAI embedding model.

        Args:
            model_name: Embedding model name
            api_key: OpenAI API key
            base_url: Optional custom base URL
        """
        self._base_url = base_url
        self._api_key = api_key
        self._model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._capabilities = self._determine_capabilities()

    def _determine_capabilities(self) -> ModelCapability:
        """Determine capabilities based on model name."""
        caps = ModelCapability.EMBEDDINGS
        return caps

    @property
    def capabilities(self) -> ModelCapability:
        """Return the capabilities supported by this model."""
        return self._capabilities

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if this model supports a specific capability."""
        return bool(self.capabilities & capability)

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str):
        """
        Set new model name and recalculate capabilities.

        Args:
            value: New model name
        """
        self._model_name = value
        # Recalculate capabilities based on new model name

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, value: str):
        self._base_url = value
        self.client = AsyncOpenAI(api_key=self._api_key, base_url=value)

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = value
        self.client = AsyncOpenAI(api_key=value, base_url=self._base_url)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        raise NotImplementedError("Embedding models do not support text generation")

    async def generate_stream(
        self, request: GenerateRequest
    ) -> AsyncIterator[StreamChunk]:
        raise NotImplementedError("Embedding models do not support text generation")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings using OpenAI API."""
        inputs = [request.input] if isinstance(request.input, str) else request.input

        kwargs = {"model": self._model_name, "input": inputs}

        if request.dimensions:
            kwargs["dimensions"] = request.dimensions

        response = await self.client.embeddings.create(**kwargs)

        embeddings = [item.embedding for item in response.data]

        return EmbeddingResponse(
            embeddings=embeddings,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            if response.usage
            else None,
        )


class AzureOpenAIEmbeddingModel(LLMModelAbstract):
    """Azure OpenAI embedding model implementation."""

    def __init__(
        self,
        model_name: str,
        api_key: str,
        azure_endpoint: str,
        deployment_name: str,
        api_version: str = "2024-08-01-preview",
    ):
        """
        Initialize Azure OpenAI embedding model.

        Args:
            model_name: Model identifier (e.g., "text-embedding-3-small")
            api_key: Azure OpenAI API key
            azure_endpoint: Azure endpoint URL
            deployment_name: Azure deployment name
            api_version: API version
        """
        self._model_name = model_name
        self._deployment_name = deployment_name
        self._api_key = api_key
        self._azure_endpoint = azure_endpoint
        self._api_version = api_version

        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            azure_deployment=deployment_name,
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str):
        """
        Set new model name.

        Args:
            value: New model name
        """
        self._model_name = value
        self._deployment_name = value
        self.client = AsyncAzureOpenAI(
            api_key=self._api_key,
            azure_endpoint=self._azure_endpoint,
            api_version=self._api_version,
            azure_deployment=value,
        )

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
        """Generate embeddings using Azure OpenAI API."""
        inputs = [request.input] if isinstance(request.input, str) else request.input

        kwargs = {"model": self._deployment_name, "input": inputs}

        if request.dimensions:
            kwargs["dimensions"] = request.dimensions

        response = await self.client.embeddings.create(**kwargs)

        embeddings = [item.embedding for item in response.data]

        return EmbeddingResponse(
            embeddings=embeddings,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            if response.usage
            else None,
        )
