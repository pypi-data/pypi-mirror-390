"""Simple auto instrumentation for AI libraries."""

import importlib
import logging
import os
from typing import Optional, Protocol

from opentelemetry.instrumentation.dependencies import DependencyConflictError
from pydantic import BaseModel

logger = logging.getLogger("brizz.instrumentation")

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_DISABLE_TRACKING"] = "true"


class InstrumentationConfig(BaseModel):
    module_name: str
    instrumentation_class: str

    class Config:
        frozen = True


class Instrumentation(Protocol):
    def __call__(self) -> None:
        """Call the instrumentation to apply it."""
        ...

    def instrument(self) -> None:
        """Instrument the library."""
        ...

    def uninstrument(self) -> None:
        """Uninstrument the library."""
        ...


class InstrumentationRegistry:
    """Simple registry for auto-instrumenting AI libraries with singleton pattern."""

    _instance: Optional["InstrumentationRegistry"] = None
    _initialized: bool = False

    # All supported instrumentations with their package names
    SUPPORTED_INSTRUMENTATIONS: list[InstrumentationConfig] = [
        InstrumentationConfig(
            module_name="openinference.instrumentation.openai", instrumentation_class="OpenAIInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.anthropic", instrumentation_class="AnthropicInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.cohere", instrumentation_class="CohereInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.langchain", instrumentation_class="LangchainInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.llamaindex", instrumentation_class="LlamaIndexInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.bedrock", instrumentation_class="BedrockInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.vertexai", instrumentation_class="VertexAIInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.alephalpha", instrumentation_class="AlephAlphaInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.chromadb", instrumentation_class="ChromaInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.crewai", instrumentation_class="CrewAIInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.google_generativeai",
            instrumentation_class="GoogleGenerativeAiInstrumentor",
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.groq", instrumentation_class="GroqInstrumentor"
        ),
        # TODO: disable for now due to circular import issues - RND-820
        # InstrumentationConfig(
        #     module_name="opentelemetry.instrumentation.haystack", instrumentation_class="HaystackInstrumentor"
        # ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.lancedb", instrumentation_class="LanceInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.logging", instrumentation_class="LoggingInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.marqo", instrumentation_class="MarqoInstrumentor"
        ),
        InstrumentationConfig(module_name="opentelemetry.instrumentation.mcp", instrumentation_class="McpInstrumentor"),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.milvus", instrumentation_class="MilvusInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.mistralai", instrumentation_class="MistralAiInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.ollama", instrumentation_class="OllamaInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.pinecone", instrumentation_class="PineconeInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.qdrant", instrumentation_class="QdrantInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.redis", instrumentation_class="RedisInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.replicate", instrumentation_class="ReplicateInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.requests", instrumentation_class="RequestsInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.httpx", instrumentation_class="HTTPXClientInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.urllib", instrumentation_class="URLLibInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.aiohttp_client",
            instrumentation_class="AioHttpClientInstrumentor",
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.sagemaker", instrumentation_class="SageMakerInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.sqlalchemy", instrumentation_class="SQLAlchemyInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.threading", instrumentation_class="ThreadingInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.together", instrumentation_class="TogetherAiInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.transformers", instrumentation_class="TransformersInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.urllib3", instrumentation_class="URLLib3Instrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.watsonx", instrumentation_class="WatsonxInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.weaviate", instrumentation_class="WeaviateInstrumentor"
        ),
    ]

    def __new__(cls) -> "InstrumentationRegistry":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once
        if not self._initialized:
            self._instrumented: set[InstrumentationConfig] = set()
            InstrumentationRegistry._initialized = True

    @classmethod
    def get_instance(cls) -> "InstrumentationRegistry":
        """Get the singleton instance of InstrumentationRegistry.

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def auto_instrument_all(self) -> None:
        """Auto-instrument all available AI libraries."""
        instrumented_count = 0

        logger.debug(f"Checking {len(self.SUPPORTED_INSTRUMENTATIONS)} instrumentation packages")

        for instrumentation_config in self.SUPPORTED_INSTRUMENTATIONS:
            if self._auto_instrument_package(instrumentation_config):
                self._instrumented.add(instrumentation_config)
                instrumented_count += 1

        if instrumented_count > 0:
            library_names = [config.module_name for config in self._instrumented]
            logger.info(f"Auto-instrumented {instrumented_count} libraries: {', '.join(library_names)}")
        else:
            logger.error("No libraries found for instrumentation")

    def _auto_instrument_package(self, instrumentation_config: InstrumentationConfig) -> bool:
        """Auto-instrument a single package.

        Args:
            instrumentation_config: Configuration for the instrumentation package

        Returns:
            True if instrumentation succeeded, False otherwise
        """
        try:
            module = importlib.import_module(instrumentation_config.module_name)
        except ImportError:
            logger.debug(f"Failed to auto-instrument {instrumentation_config.module_name}", exc_info=True)
            return False
        try:
            instrumentation_class = getattr(module, instrumentation_config.instrumentation_class)
            instrumentation: Instrumentation = instrumentation_class()
            instrumentation.instrument(raise_exception_on_conflict=True)  # type: ignore
            return True
        except DependencyConflictError as e:
            if 'but found: "None"' in str(e):
                # This usually means the library is not installed - ignore
                logger.debug(
                    f"Failed to auto-instrument {instrumentation_config.module_name}: {e}",
                    exc_info=True,
                    extra={"instrumentation_config": instrumentation_config.model_dump()},
                )
            else:
                logger.error(
                    f"Dependency conflict for {instrumentation_config.module_name}: {e}",
                    exc_info=True,
                    extra={"instrumentation_config": instrumentation_config.model_dump()},
                )
            return False
        except Exception as e:
            logger.debug(
                f"Failed to auto-instrument {instrumentation_config.module_name}: {e}",
                exc_info=True,
                extra={"instrumentation_config": instrumentation_config.model_dump()},
            )
            return False

    def get_instrumented_count(self) -> int:
        """Get the number of instrumented libraries.

        Returns:
            Number of instrumented libraries
        """
        return len(self._instrumented)


def auto_instrument() -> None:
    """Auto-instrument all available AI libraries.

    This is the main entry point for auto instrumentation.
    It will automatically detect and instrument all supported AI libraries.
    """
    registry = InstrumentationRegistry.get_instance()
    registry.auto_instrument_all()
