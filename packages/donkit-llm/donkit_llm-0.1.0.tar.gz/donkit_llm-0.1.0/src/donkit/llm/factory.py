from typing import Literal

from .claude_model import ClaudeModel, ClaudeVertexModel
from .model_abstract import LLMModelAbstract
from .openai_model import (
    AzureOpenAIEmbeddingModel,
    AzureOpenAIModel,
    OpenAIEmbeddingModel,
    OpenAIModel,
)
from .vertex_model import VertexAIModel, VertexEmbeddingModel


class ModelFactory:
    """Factory for creating LLM model instances."""

    @staticmethod
    def create_openai_model(
        model_name: str,
        api_key: str,
        base_url: str | None = None,
        organization: str | None = None,
    ) -> OpenAIModel:
        return OpenAIModel(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            organization=organization,
        )

    @staticmethod
    def create_azure_openai_model(
        model_name: str,
        api_key: str,
        azure_endpoint: str,
        api_version: str = "2024-08-01-preview",
        deployment_name: str | None = None,
    ) -> AzureOpenAIModel:
        return AzureOpenAIModel(
            model_name=deployment_name or model_name,
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            deployment_name=deployment_name,
        )

    @staticmethod
    def create_embedding_model(
        provider: Literal["openai", "azure_openai", "vertex"],
        model_name: str | None = None,
        api_key: str | None = None,
        **kwargs,
    ) -> LLMModelAbstract:
        if provider == "openai":
            return OpenAIEmbeddingModel(
                model_name=model_name or "text-embedding-3-small",
                api_key=api_key,
                base_url=kwargs.get("base_url"),
            )
        elif provider == "azure_openai":
            return AzureOpenAIEmbeddingModel(
                model_name=model_name or "text-embedding-ada-002",
                api_key=api_key,
                azure_endpoint=kwargs["azure_endpoint"],
                deployment_name=kwargs.get("deployment_name")
                or model_name
                or "text-embedding-ada-002",
                api_version=kwargs.get("api_version", "2024-08-01-preview"),
            )
        elif provider == "vertex":
            return VertexEmbeddingModel(
                project_id=kwargs["project_id"],
                model_name=model_name or "text-multilingual-embedding-002",
                location=kwargs.get("location", "us-central1"),
                credentials=kwargs.get("credentials"),
                output_dimensionality=kwargs.get("output_dimensionality"),
                batch_size=kwargs.get("batch_size", 100),
                task_type=kwargs.get("task_type", "RETRIEVAL_DOCUMENT"),
            )
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    @staticmethod
    def create_claude_model(
        model_name: str,
        api_key: str,
        base_url: str | None = None,
    ) -> ClaudeModel:
        return ClaudeModel(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )

    @staticmethod
    def create_claude_vertex_model(
        model_name: str,
        project_id: str,
        location: str = "us-east5",
    ) -> ClaudeVertexModel:
        return ClaudeVertexModel(
            model_name=model_name,
            project_id=project_id,
            location=location,
        )

    @staticmethod
    def create_vertex_model(
        model_name: str,
        project_id: str,
        location: str = "us-central1",
        credentials: dict | None = None,
    ) -> VertexAIModel:
        return VertexAIModel(
            model_name=model_name,
            project_id=project_id,
            location=location,
            credentials=credentials,
        )

    @staticmethod
    def create_model(
        provider: Literal[
            "openai", "azure_openai", "claude", "claude_vertex", "vertex"
        ],
        model_name: str,
        credentials: dict,
    ) -> LLMModelAbstract:
        if provider == "openai":
            return ModelFactory.create_openai_model(
                model_name=model_name,
                api_key=credentials["api_key"],
                base_url=credentials.get("base_url"),
                organization=credentials.get("organization"),
            )
        elif provider == "azure_openai":
            return ModelFactory.create_azure_openai_model(
                model_name=model_name,
                api_key=credentials["api_key"],
                azure_endpoint=credentials["azure_endpoint"],
                api_version=credentials.get("api_version", "2024-08-01-preview"),
                deployment_name=credentials.get("deployment_name"),
            )
        elif provider == "claude":
            return ModelFactory.create_claude_model(
                model_name=model_name,
                api_key=credentials["api_key"],
                base_url=credentials.get("base_url"),
            )
        elif provider == "claude_vertex":
            return ModelFactory.create_claude_vertex_model(
                model_name=model_name,
                project_id=credentials["project_id"],
                location=credentials.get("location", "us-east5"),
            )
        elif provider == "vertex":
            return ModelFactory.create_vertex_model(
                model_name=model_name,
                project_id=credentials["project_id"],
                location=credentials.get("location", "us-central1"),
                credentials=credentials.get("credentials"),
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
