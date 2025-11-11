import importlib
from typing import Dict, Optional, Union

from bae_mem.configs.embeddings.base import BaseEmbedderConfig
from bae_mem.configs.llms.anthropic import AnthropicConfig
from bae_mem.configs.llms.azure import AzureOpenAIConfig
from bae_mem.configs.llms.base import BaseLlmConfig
from bae_mem.configs.llms.deepseek import DeepSeekConfig
from bae_mem.configs.llms.lmstudio import LMStudioConfig
from bae_mem.configs.llms.ollama import OllamaConfig
from bae_mem.configs.llms.openai import OpenAIConfig
from bae_mem.configs.llms.vllm import VllmConfig
from bae_mem.configs.rerankers.base import BaseRerankerConfig
from bae_mem.configs.rerankers.cohere import CohereRerankerConfig
from bae_mem.configs.rerankers.sentence_transformer import SentenceTransformerRerankerConfig
from bae_mem.configs.rerankers.zero_entropy import ZeroEntropyRerankerConfig
from bae_mem.configs.rerankers.llm import LLMRerankerConfig
from bae_mem.configs.rerankers.huggingface import HuggingFaceRerankerConfig
from bae_mem.embeddings.mock import MockEmbeddings


def load_class(class_type):
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class LlmFactory:
    """
    Factory for creating LLM instances with appropriate configurations.
    Supports both old-style BaseLlmConfig and new provider-specific configs.
    """

    # Provider mappings with their config classes
    provider_to_class = {
        "ollama": ("bae_mem.llms.ollama.OllamaLLM", OllamaConfig),
        "openai": ("bae_mem.llms.openai.OpenAILLM", OpenAIConfig),
        "groq": ("bae_mem.llms.groq.GroqLLM", BaseLlmConfig),
        "together": ("bae_mem.llms.together.TogetherLLM", BaseLlmConfig),
        "aws_bedrock": ("bae_mem.llms.aws_bedrock.AWSBedrockLLM", BaseLlmConfig),
        "litellm": ("bae_mem.llms.litellm.LiteLLM", BaseLlmConfig),
        "azure_openai": ("bae_mem.llms.azure_openai.AzureOpenAILLM", AzureOpenAIConfig),
        "openai_structured": ("bae_mem.llms.openai_structured.OpenAIStructuredLLM", OpenAIConfig),
        "anthropic": ("bae_mem.llms.anthropic.AnthropicLLM", AnthropicConfig),
        "azure_openai_structured": ("bae_mem.llms.azure_openai_structured.AzureOpenAIStructuredLLM", AzureOpenAIConfig),
        "gemini": ("bae_mem.llms.gemini.GeminiLLM", BaseLlmConfig),
        "deepseek": ("bae_mem.llms.deepseek.DeepSeekLLM", DeepSeekConfig),
        "xai": ("bae_mem.llms.xai.XAILLM", BaseLlmConfig),
        "sarvam": ("bae_mem.llms.sarvam.SarvamLLM", BaseLlmConfig),
        "lmstudio": ("bae_mem.llms.lmstudio.LMStudioLLM", LMStudioConfig),
        "vllm": ("bae_mem.llms.vllm.VllmLLM", VllmConfig),
        "langchain": ("bae_mem.llms.langchain.LangchainLLM", BaseLlmConfig),
    }

    @classmethod
    def create(cls, provider_name: str, config: Optional[Union[BaseLlmConfig, Dict]] = None, **kwargs):
        """
        Create an LLM instance with the appropriate configuration.

        Args:
            provider_name (str): The provider name (e.g., 'openai', 'anthropic')
            config: Configuration object or dict. If None, will create default config
            **kwargs: Additional configuration parameters

        Returns:
            Configured LLM instance

        Raises:
            ValueError: If provider is not supported
        """
        if provider_name not in cls.provider_to_class:
            raise ValueError(f"Unsupported Llm provider: {provider_name}")

        class_type, config_class = cls.provider_to_class[provider_name]
        llm_class = load_class(class_type)

        # Handle configuration
        if config is None:
            # Create default config with kwargs
            config = config_class(**kwargs)
        elif isinstance(config, dict):
            # Merge dict config with kwargs
            config.update(kwargs)
            config = config_class(**config)
        elif isinstance(config, BaseLlmConfig):
            # Convert base config to provider-specific config if needed
            if config_class != BaseLlmConfig:
                # Convert to provider-specific config
                config_dict = {
                    "model": config.model,
                    "temperature": config.temperature,
                    "api_key": config.api_key,
                    "max_tokens": config.max_tokens,
                    "top_p": config.top_p,
                    "top_k": config.top_k,
                    "enable_vision": config.enable_vision,
                    "vision_details": config.vision_details,
                    "http_client_proxies": config.http_client,
                }
                config_dict.update(kwargs)
                config = config_class(**config_dict)
            else:
                # Use base config as-is
                pass
        else:
            # Assume it's already the correct config type
            pass

        return llm_class(config)

    @classmethod
    def register_provider(cls, name: str, class_path: str, config_class=None):
        """
        Register a new provider.

        Args:
            name (str): Provider name
            class_path (str): Full path to LLM class
            config_class: Configuration class for the provider (defaults to BaseLlmConfig)
        """
        if config_class is None:
            config_class = BaseLlmConfig
        cls.provider_to_class[name] = (class_path, config_class)

    @classmethod
    def get_supported_providers(cls) -> list:
        """
        Get list of supported providers.

        Returns:
            list: List of supported provider names
        """
        return list(cls.provider_to_class.keys())


class EmbedderFactory:
    provider_to_class = {
        "openai": "bae_mem.embeddings.openai.OpenAIEmbedding",
        "ollama": "bae_mem.embeddings.ollama.OllamaEmbedding",
        "huggingface": "bae_mem.embeddings.huggingface.HuggingFaceEmbedding",
        "azure_openai": "bae_mem.embeddings.azure_openai.AzureOpenAIEmbedding",
        "gemini": "bae_mem.embeddings.gemini.GoogleGenAIEmbedding",
        "vertexai": "bae_mem.embeddings.vertexai.VertexAIEmbedding",
        "together": "bae_mem.embeddings.together.TogetherEmbedding",
        "lmstudio": "bae_mem.embeddings.lmstudio.LMStudioEmbedding",
        "langchain": "bae_mem.embeddings.langchain.LangchainEmbedding",
        "aws_bedrock": "bae_mem.embeddings.aws_bedrock.AWSBedrockEmbedding",
    }

    @classmethod
    def create(cls, provider_name, config, vector_config: Optional[dict]):
        if provider_name == "upstash_vector" and vector_config and vector_config.enable_embeddings:
            return MockEmbeddings()
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            embedder_instance = load_class(class_type)
            base_config = BaseEmbedderConfig(**config)
            return embedder_instance(base_config)
        else:
            raise ValueError(f"Unsupported Embedder provider: {provider_name}")


class VectorStoreFactory:
    provider_to_class = {
        "qdrant": "bae_mem.vector_stores.qdrant.Qdrant",
        "chroma": "bae_mem.vector_stores.chroma.ChromaDB",
        "pgvector": "bae_mem.vector_stores.pgvector.PGVector",
        "milvus": "bae_mem.vector_stores.milvus.MilvusDB",
        "upstash_vector": "bae_mem.vector_stores.upstash_vector.UpstashVector",
        "azure_ai_search": "bae_mem.vector_stores.azure_ai_search.AzureAISearch",
        "azure_mysql": "bae_mem.vector_stores.azure_mysql.AzureMySQL",
        "pinecone": "bae_mem.vector_stores.pinecone.PineconeDB",
        "mongodb": "bae_mem.vector_stores.mongodb.MongoDB",
        "redis": "bae_mem.vector_stores.redis.RedisDB",
        "valkey": "bae_mem.vector_stores.valkey.ValkeyDB",
        "databricks": "bae_mem.vector_stores.databricks.Databricks",
        "elasticsearch": "bae_mem.vector_stores.elasticsearch.ElasticsearchDB",
        "vertex_ai_vector_search": "bae_mem.vector_stores.vertex_ai_vector_search.GoogleMatchingEngine",
        "opensearch": "bae_mem.vector_stores.opensearch.OpenSearchDB",
        "supabase": "bae_mem.vector_stores.supabase.Supabase",
        "weaviate": "bae_mem.vector_stores.weaviate.Weaviate",
        "faiss": "bae_mem.vector_stores.faiss.FAISS",
        "langchain": "bae_mem.vector_stores.langchain.Langchain",
        "s3_vectors": "bae_mem.vector_stores.s3_vectors.S3Vectors",
        "baidu": "bae_mem.vector_stores.baidu.BaiduDB",
        "neptune": "bae_mem.vector_stores.neptune_analytics.NeptuneAnalyticsVector",
    }

    @classmethod
    def create(cls, provider_name, config):
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            if not isinstance(config, dict):
                config = config.model_dump()
            vector_store_instance = load_class(class_type)
            return vector_store_instance(**config)
        else:
            raise ValueError(f"Unsupported VectorStore provider: {provider_name}")

    @classmethod
    def reset(cls, instance):
        instance.reset()
        return instance


class GraphStoreFactory:
    """
    Factory for creating MemoryGraph instances for different graph store providers.
    Usage: GraphStoreFactory.create(provider_name, config)
    """

    provider_to_class = {
        "memgraph": "bae_mem.memory.memgraph_memory.MemoryGraph",
        "neptune": "bae_mem.graphs.neptune.neptunegraph.MemoryGraph",
        "neptunedb": "bae_mem.graphs.neptune.neptunedb.MemoryGraph",
        "kuzu": "bae_mem.memory.kuzu_memory.MemoryGraph",
        "default": "bae_mem.memory.graph_memory.MemoryGraph",
    }

    @classmethod
    def create(cls, provider_name, config):
        class_type = cls.provider_to_class.get(provider_name, cls.provider_to_class["default"])
        try:
            GraphClass = load_class(class_type)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not import MemoryGraph for provider '{provider_name}': {e}")
        return GraphClass(config)


class RerankerFactory:
    """
    Factory for creating reranker instances with appropriate configurations.
    Supports provider-specific configs following the same pattern as other factories.
    """

    # Provider mappings with their config classes
    provider_to_class = {
        "cohere": ("bae_mem.reranker.cohere_reranker.CohereReranker", CohereRerankerConfig),
        "sentence_transformer": ("bae_mem.reranker.sentence_transformer_reranker.SentenceTransformerReranker", SentenceTransformerRerankerConfig),
        "zero_entropy": ("bae_mem.reranker.zero_entropy_reranker.ZeroEntropyReranker", ZeroEntropyRerankerConfig),
        "llm_reranker": ("bae_mem.reranker.llm_reranker.LLMReranker", LLMRerankerConfig),
        "huggingface": ("bae_mem.reranker.huggingface_reranker.HuggingFaceReranker", HuggingFaceRerankerConfig),
    }

    @classmethod
    def create(cls, provider_name: str, config: Optional[Union[BaseRerankerConfig, Dict]] = None, **kwargs):
        """
        Create a reranker instance based on the provider and configuration.

        Args:
            provider_name: The reranker provider (e.g., 'cohere', 'sentence_transformer')
            config: Configuration object or dictionary
            **kwargs: Additional configuration parameters

        Returns:
            Reranker instance configured for the specified provider

        Raises:
            ImportError: If the provider class cannot be imported
            ValueError: If the provider is not supported
        """
        if provider_name not in cls.provider_to_class:
            raise ValueError(f"Unsupported reranker provider: {provider_name}")

        class_path, config_class = cls.provider_to_class[provider_name]

        # Handle configuration
        if config is None:
            config = config_class(**kwargs)
        elif isinstance(config, dict):
            config = config_class(**config, **kwargs)
        elif not isinstance(config, BaseRerankerConfig):
            raise ValueError(f"Config must be a {config_class.__name__} instance or dict")

        # Import and create the reranker class
        try:
            reranker_class = load_class(class_path)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not import reranker for provider '{provider_name}': {e}")

        return reranker_class(config)
