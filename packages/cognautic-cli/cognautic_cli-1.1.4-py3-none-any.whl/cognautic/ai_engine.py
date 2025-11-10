"""
AI Engine for multi-provider AI interactions
"""

import asyncio
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from .auto_continuation import AutoContinuationManager
from .config import ConfigManager
from .provider_endpoints import GenericAPIClient, get_all_providers, get_provider_config
from .tools import ToolRegistry


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def generate_response(
        self, messages: List[Dict], model: str = None, **kwargs
    ) -> str:
        """Generate response from the AI provider"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass


class GenericProvider(AIProvider):
    """Generic provider that can work with any API endpoint"""

    def __init__(self, api_key: str, provider_name: str):
        super().__init__(api_key)
        self.provider_name = provider_name
        self.client = GenericAPIClient(provider_name, api_key)

    async def generate_response(
        self, messages: List[Dict], model: str = None, **kwargs
    ) -> str:
        try:
            response = await self.client.chat_completion(messages, model, **kwargs)

            # Extract text from different response formats
            if self.provider_name == "google":
                if "candidates" in response and response["candidates"]:
                    candidate = response["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        return candidate["content"]["parts"][0]["text"]
                return "No response generated"

            elif self.provider_name == "anthropic":
                if "content" in response and response["content"]:
                    return response["content"][0]["text"]
                return "No response generated"

            else:
                # OpenAI-compatible format
                if "choices" in response and response["choices"]:
                    return response["choices"][0]["message"]["content"]
                return "No response generated"

        except Exception as e:
            raise Exception(f"{self.provider_name.title()} API error: {str(e)}")

    def get_available_models(self) -> List[str]:
        """Get list of available models - returns generic list since we support any model"""
        return [f"{self.provider_name}-model-1", f"{self.provider_name}-model-2"]


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import openai

            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")

    async def generate_response(
        self, messages: List[Dict], model: str = "gpt-4", **kwargs
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def get_available_models(self) -> List[str]:
        return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"]


class AnthropicProvider(AIProvider):
    """Anthropic provider implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import anthropic

            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Anthropic library not installed. Run: pip install anthropic"
            )

    async def generate_response(
        self, messages: List[Dict], model: str = "claude-3-sonnet-20240229", **kwargs
    ) -> str:
        try:
            # Convert messages format for Anthropic
            system_message = ""
            user_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)

            response = await self.client.messages.create(
                model=model,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7),
                system=system_message,
                messages=user_messages,
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def get_available_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]


class GoogleProvider(AIProvider):
    """Google provider implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            self.genai = genai
        except ImportError:
            raise ImportError(
                "Google Generative AI library not installed. Run: pip install google-generativeai"
            )

    async def generate_response(
        self, messages: List[Dict], model: str = "gemini-pro", **kwargs
    ) -> str:
        try:
            model_instance = self.genai.GenerativeModel(model)

            # Convert messages to Google format
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n"
                elif msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"

            response = await model_instance.generate_content_async(
                prompt,
                generation_config=self.genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", 4096),
                    temperature=kwargs.get("temperature", 0.7),
                ),
            )
            try:
                return response.text
            except ValueError as ve:
                if "Invalid operation: The `response.text` quick accessor" in str(ve):
                    # Handle response with no valid parts
                    if hasattr(response, "candidates") and response.candidates:
                        # Try to get text from the candidate parts
                        for candidate in response.candidates:
                            if hasattr(candidate, "content") and hasattr(
                                candidate.content, "parts"
                            ):
                                for part in candidate.content.parts:
                                    if hasattr(part, "text") and part.text:
                                        return part.text
                    return (
                        "No response generated"  # Return empty string if no text found
                    )
                else:
                    raise ve
        except Exception as e:
            raise Exception(f"Google API error: {str(e)}")

    async def generate_response_stream(
        self, messages: List[Dict], model: str = "gemini-pro", **kwargs
    ):
        """Generate streaming response"""
        try:
            model_instance = self.genai.GenerativeModel(model)

            # Convert messages to Google format
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n"
                elif msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"

            response = model_instance.generate_content(
                prompt,
                generation_config=self.genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", 4096),
                    temperature=kwargs.get("temperature", 0.7),
                ),
                stream=True,
            )

            for chunk in response:
                try:
                    if hasattr(chunk, "text") and chunk.text:
                        yield chunk.text
                    elif hasattr(chunk, "parts") and chunk.parts:
                        # Handle response with parts but no direct text
                        for part in chunk.parts:
                            if hasattr(part, "text") and part.text:
                                yield part.text
                except ValueError as ve:
                    # Handle the case where chunk.text is accessed but no valid parts exist
                    if "Invalid operation: The `response.text` quick accessor" in str(
                        ve
                    ):
                        continue
                    else:
                        # Re-raise other ValueErrors
                        raise ve
        except Exception as e:
            raise Exception(f"Google API error: {str(e)}")

    def get_available_models(self) -> List[str]:
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro", "gemini-pro-vision"]


class TogetherProvider(AIProvider):
    """Together AI provider implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import together

            self.client = together.AsyncTogether(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Together library not installed. Run: pip install together"
            )

    async def generate_response(
        self,
        messages: List[Dict],
        model: str = "meta-llama/Llama-2-70b-chat-hf",
        **kwargs,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Together API error: {str(e)}")

    def get_available_models(self) -> List[str]:
        return [
            "meta-llama/Llama-2-70b-chat-hf",
            "meta-llama/Llama-2-13b-chat-hf",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
        ]


class OpenRouterProvider(AIProvider):
    """OpenRouter provider implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import openai

            self.client = openai.AsyncOpenAI(
                api_key=api_key, base_url="https://openrouter.ai/api/v1"
            )
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")

    async def generate_response(
        self, messages: List[Dict], model: str = "anthropic/claude-3-sonnet", **kwargs
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def get_available_models(self) -> List[str]:
        return [
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "openai/gpt-4-turbo",
            "meta-llama/llama-3-70b-instruct",
        ]


class LocalModelProvider(AIProvider):
    """Local model provider for both Hugging Face and GGUF models"""

    def __init__(self, model_path: str):
        super().__init__(api_key="local")  # No API key needed for local models
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.device = None
        self.is_gguf = model_path.endswith(".gguf")
        self.n_ctx = 2048  # Will be set during model loading
        self._load_model()

    def _load_model(self):
        """Load the local model (Hugging Face or GGUF)"""
        if self.is_gguf:
            self._load_gguf_model()
        else:
            self._load_hf_model()

    def _load_gguf_model(self):
        """Load a GGUF quantized model using llama-cpp-python"""
        try:
            import os

            from llama_cpp import Llama

            print(f"Loading GGUF model from {self.model_path}...")

            # Get optimal thread count (use all available cores)
            n_threads = os.cpu_count() or 4

            # Try to load model metadata to get optimal context size
            try:
                # Load with minimal context first to read metadata
                temp_model = Llama(model_path=self.model_path, n_ctx=512, verbose=False)
                # Get model's training context (if available)
                model_metadata = temp_model.metadata
                n_ctx_train = (
                    model_metadata.get("n_ctx_train", 2048)
                    if hasattr(temp_model, "metadata")
                    else 2048
                )
                del temp_model

                # Use smaller of: training context or 4096 (for performance)
                self.n_ctx = min(n_ctx_train, 4096) if n_ctx_train > 0 else 2048
            except:
                # Fallback to 2048 if metadata reading fails
                self.n_ctx = 2048

            print(f"Using context window: {self.n_ctx} tokens")

            # Load model with optimal context
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,  # Auto-detected context window
                n_threads=n_threads,  # Use all CPU threads
                n_gpu_layers=0,  # 0 for CPU, increase for GPU
                n_batch=512,  # Batch size for prompt processing
                verbose=False,
            )
            self.device = "cpu"
            print(
                f"SUCCESS: GGUF model loaded successfully on {self.device} ({n_threads} threads)"
            )

        except ImportError:
            raise ImportError(
                "llama-cpp-python not installed. For GGUF models, run:\n"
                "  pip install llama-cpp-python\n"
                "Or for GPU support:\n"
                '  CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python'
            )
        except Exception as e:
            raise Exception(f"Failed to load GGUF model: {str(e)}")

    def _load_hf_model(self):
        """Load a Hugging Face transformers model"""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            # Determine device
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"

            print(f"Loading local model from {self.model_path} on {self.device}...")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

            # Load model with appropriate settings
            if self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map="auto",
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True,
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path, torch_dtype=torch.float32
                )
                self.model.to(self.device)

            print(f"SUCCESS: Model loaded successfully on {self.device}")

        except ImportError:
            raise ImportError(
                "Transformers and PyTorch not installed. Run: pip install transformers torch accelerate"
            )
        except Exception as e:
            raise Exception(f"Failed to load local model: {str(e)}")

    async def generate_response(
        self, messages: List[Dict], model: str = None, **kwargs
    ) -> str:
        """Generate response from the local model"""
        if self.is_gguf:
            return await self._generate_gguf_response(messages, **kwargs)
        else:
            return await self._generate_hf_response(messages, **kwargs)

    async def _generate_gguf_response(self, messages: List[Dict], **kwargs) -> str:
        """Generate response using GGUF model"""
        try:
            # Truncate messages if needed to fit context window
            max_tokens = kwargs.get("max_tokens", 256)  # Reduced for faster response
            temperature = kwargs.get("temperature", 0.7)

            # Use actual context window size with safety margin
            # Reserve space for: response (max_tokens) + safety buffer (200)
            available_context = self.n_ctx - max_tokens - 200

            # Estimate tokens more conservatively (1 token ≈ 3 characters for safety)
            max_prompt_chars = available_context * 3

            # Truncate messages to fit
            truncated_messages = self._truncate_messages(messages, max_prompt_chars)

            # Convert messages to prompt
            prompt = self._messages_to_prompt(truncated_messages)

            # Double-check prompt length (rough token estimate)
            estimated_prompt_tokens = len(prompt) // 3
            if estimated_prompt_tokens + max_tokens > self.n_ctx:
                # Emergency truncation - keep only last message
                truncated_messages = messages[-1:] if messages else []
                prompt = self._messages_to_prompt(truncated_messages)

            # Generate response with optimized settings
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                repeat_penalty=1.1,
                echo=False,  # Don't echo the prompt
                stop=["User:", "System:", "\n\n"],  # Stop tokens
            )

            # Extract text from response
            if isinstance(response, dict) and "choices" in response:
                return response["choices"][0]["text"].strip()
            return str(response).strip()

        except Exception as e:
            raise Exception(f"GGUF model generation error: {str(e)}")

    async def _generate_hf_response(self, messages: List[Dict], **kwargs) -> str:
        """Generate response using Hugging Face model"""
        try:
            import torch

            # Convert messages to a single prompt
            prompt = self._messages_to_prompt(messages)

            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            # Generate response
            max_tokens = kwargs.get("max_tokens", 2048)
            temperature = kwargs.get("temperature", 0.7)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove the prompt from the response
            if response.startswith(prompt):
                response = response[len(prompt) :].strip()

            return response

        except Exception as e:
            raise Exception(f"Local model generation error: {str(e)}")

    def _truncate_messages(self, messages: List[Dict], max_chars: int) -> List[Dict]:
        """Truncate messages to fit within character limit"""
        # Always keep system message if present
        system_msgs = [m for m in messages if m["role"] == "system"]
        other_msgs = [m for m in messages if m["role"] != "system"]

        # Estimate current size
        total_chars = sum(len(m["content"]) for m in messages)

        if total_chars <= max_chars:
            return messages

        # Keep system message and recent messages
        result = system_msgs.copy()
        current_chars = sum(len(m["content"]) for m in system_msgs)

        # Add messages from most recent backwards
        for msg in reversed(other_msgs):
            msg_chars = len(msg["content"])
            if current_chars + msg_chars <= max_chars:
                result.insert(len(system_msgs), msg)
                current_chars += msg_chars
            else:
                break

        return result

    def _messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert message format to a prompt string"""
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"

        # Add final assistant prompt
        prompt += "Assistant: "
        return prompt

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return [self.model_path]


class AIEngine:
    """Main AI engine that manages providers and handles requests"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.tool_registry = ToolRegistry()
        self.providers = {}
        self.local_model_provider = None  # Track local model separately
        self.auto_continuation = AutoContinuationManager(max_iterations=50)
        # Give AI engine unrestricted permissions
        from .tools.base import PermissionLevel

        self.tool_registry.set_permission_level(
            "ai_engine", PermissionLevel.UNRESTRICTED
        )
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available AI providers"""
        # Get all supported providers from endpoints
        all_providers = get_all_providers()

        # Legacy provider classes for backward compatibility
        legacy_provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider,
            "together": TogetherProvider,
            "openrouter": OpenRouterProvider,
        }

        for provider_name in all_providers:
            api_key = self.config_manager.get_api_key(provider_name)
            if api_key:
                try:
                    # Use legacy provider if available, otherwise use generic provider
                    if provider_name in legacy_provider_classes:
                        self.providers[provider_name] = legacy_provider_classes[
                            provider_name
                        ](api_key)
                    else:
                        self.providers[provider_name] = GenericProvider(
                            api_key, provider_name
                        )
                except Exception as e:
                    print(f"Warning: Could not initialize {provider_name}: {e}")

        # Don't auto-load local model at startup - only load when explicitly requested
        # This prevents unnecessary loading and error messages when not using local provider

    def load_local_model(self, model_path: str):
        """Load a local Hugging Face model"""
        try:
            self.local_model_provider = LocalModelProvider(model_path)
            self.providers["local"] = self.local_model_provider
            self.config_manager.set_config("local_model_path", model_path)
            return True
        except Exception as e:
            raise Exception(f"Failed to load local model: {str(e)}")

    def unload_local_model(self):
        """Unload the local model and free memory"""
        if "local" in self.providers:
            del self.providers["local"]
        self.local_model_provider = None
        self.config_manager.delete_config("local_model_path")

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())

    def get_provider_models(self, provider: str) -> List[str]:
        """Get available models for a provider"""
        if provider in self.providers:
            return self.providers[provider].get_available_models()
        return []

    async def process_message(
        self,
        message: str,
        provider: str = None,
        model: str = None,
        project_path: str = None,
        context: List[Dict] = None,
        conversation_history: List[Dict] = None,
    ) -> str:
        """Process a user message and generate AI response"""

        # Use default provider if not specified
        if not provider:
            provider = self.config_manager.get_config_value("default_provider")

        if provider not in self.providers:
            raise Exception(
                f"Provider '{provider}' not available. Available: {list(self.providers.keys())}"
            )

        # Build message context
        messages = []

        # Add system message
        system_prompt = self._build_system_prompt(project_path)
        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history if provided (for context)
        if conversation_history:
            messages.extend(conversation_history)

        # Add context if provided (for additional context)
        if context:
            messages.extend(context)

        # Add current user message
        messages.append({"role": "user", "content": message})

        # Get AI response
        ai_provider = self.providers[provider]

        # Use default model if not specified
        if not model:
            available_models = ai_provider.get_available_models()
            if provider == "google":
                model = (
                    available_models[0] if available_models else "gemini-1.5-flash"
                )  # Use newer model
            else:
                model = available_models[0] if available_models else None

        config = self.config_manager.get_config()
        # Use unlimited tokens (or max available for the model)
        max_tokens = config.get("max_tokens", None)  # None = unlimited
        if max_tokens == 0 or max_tokens == -1:
            max_tokens = None  # Treat 0 or -1 as unlimited

        response = await ai_provider.generate_response(
            messages=messages,
            model=model,
            max_tokens=max_tokens or 16384,  # Use large default if None
            temperature=config.get("temperature", 0.7),
        )

        # Check if response contains tool calls
        has_tools = self._contains_tool_calls(response)
        if has_tools:
            response = await self._execute_tools(response, project_path)

        return response

    async def process_message_stream(
        self,
        message: str,
        provider: str = None,
        model: str = None,
        project_path: str = None,
        context: List[Dict] = None,
        conversation_history: List[Dict] = None,
    ):
        """Process a user message and generate streaming AI response"""

        # Reset auto-continuation counter for new message
        self.auto_continuation.reset()

        # Use default provider if not specified
        if not provider:
            provider = self.config_manager.get_config_value("default_provider")

        if provider not in self.providers:
            raise Exception(
                f"Provider '{provider}' not available. Available: {list(self.providers.keys())}"
            )

        # No file tagging - use message as-is
        processed_message = message

        # Build message context
        messages = []

        # Add system message
        system_prompt = self._build_system_prompt(project_path)
        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history if provided (for context)
        if conversation_history:
            messages.extend(conversation_history)

        # Add context if provided (for additional context)
        if context:
            messages.extend(context)

        # Add current user message
        messages.append({"role": "user", "content": processed_message})

        # Get AI response
        ai_provider = self.providers[provider]

        # Use default model if not specified
        if not model:
            available_models = ai_provider.get_available_models()
            if provider == "google":
                model = (
                    available_models[0] if available_models else "gemini-1.5-flash"
                )  # Use newer model
            else:
                model = available_models[0] if available_models else None

        config = self.config_manager.get_config()

        # Use unlimited tokens (or max available for the model)
        max_tokens = config.get("max_tokens", None)  # None = unlimited
        if max_tokens == 0 or max_tokens == -1:
            max_tokens = None  # Treat 0 or -1 as unlimited

        # Stream response with real-time tool detection and execution
        async for chunk in self._stream_with_live_tools(
            ai_provider, messages, model, max_tokens, config, project_path
        ):
            yield chunk

    async def _stream_with_live_tools(
        self,
        ai_provider,
        messages: list,
        model: str,
        max_tokens: int,
        config: dict,
        project_path: str,
        recursion_depth: int = 0,
    ):
        """Stream AI response with real-time tool detection and execution"""
        import json
        import re

        # Prevent infinite recursion
        MAX_RECURSION_DEPTH = 10
        if recursion_depth >= MAX_RECURSION_DEPTH:
            yield "\n**WARNING:** Maximum continuation depth reached.\n"
            return

        # Buffer to accumulate streaming response
        buffer = ""
        yielded_length = 0
        in_json_block = False
        json_block_start = -1
        has_executed_tools = False
        tool_results = []

        # Check if provider supports streaming
        if not hasattr(ai_provider, "generate_response_stream"):
            # Fall back to non-streaming
            response = await ai_provider.generate_response(
                messages=messages,
                model=model,
                max_tokens=max_tokens or 16384,
                temperature=config.get("temperature", 0.7),
            )
            async for chunk in self._process_response_with_tools(
                response, project_path, messages, ai_provider, model, config
            ):
                yield chunk
            return

        # Stream the response
        try:
            async for chunk in ai_provider.generate_response_stream(
                messages=messages,
                model=model,
                max_tokens=max_tokens or 16384,
                temperature=config.get("temperature", 0.7),
            ):
                if not chunk:
                    continue

                buffer += chunk

                # Check for JSON block markers
                if not in_json_block:
                    # Look for start of JSON block
                    json_start_match = re.search(
                        r"```json\s*\n", buffer[yielded_length:]
                    )
                    if json_start_match:
                        # Found start of JSON block
                        in_json_block = True
                        json_block_start = yielded_length + json_start_match.start()

                        # Yield everything BEFORE the JSON block
                        if json_block_start > yielded_length:
                            text_to_yield = buffer[yielded_length:json_block_start]
                            text_to_yield = self._clean_model_syntax(text_to_yield)
                            if text_to_yield.strip():
                                yield text_to_yield
                        yielded_length = json_block_start
                    else:
                        # No JSON block yet, yield new content (keep small buffer)
                        if len(buffer) > yielded_length + 10:
                            text_to_yield = buffer[yielded_length:-10]
                            text_to_yield = self._clean_model_syntax(text_to_yield)
                            if text_to_yield:
                                yield text_to_yield
                            yielded_length = len(buffer) - 10
                else:
                    # Inside JSON block, look for the end
                    json_end_match = re.search(r"\n```", buffer[json_block_start:])
                    if json_end_match:
                        # Found end of JSON block
                        json_block_end = json_block_start + json_end_match.end()

                        # Extract the complete JSON block
                        json_block = buffer[json_block_start:json_block_end]

                        # Parse and execute the tool call immediately
                        json_pattern = r"```json\s*\n(.*?)\n```"
                        match = re.search(json_pattern, json_block, re.DOTALL)
                        if match:
                            try:
                                tool_call = json.loads(match.group(1).strip())

                                # Execute tool and yield result immediately
                                async for tool_result in self._execute_single_tool_live(
                                    tool_call, project_path, tool_results
                                ):
                                    yield tool_result

                                has_executed_tools = True

                            except json.JSONDecodeError as je:
                                yield f"\n**WARNING:** JSON Parse Warning: {str(je)}\n"

                        # Update state
                        in_json_block = False
                        yielded_length = json_block_end
                        json_block_start = -1

            # Yield any remaining content
            if yielded_length < len(buffer):
                remaining = buffer[yielded_length:]
                if not in_json_block:
                    remaining = self._clean_model_syntax(remaining)
                    if remaining.strip():
                        yield remaining

            # Check if end_response was called
            has_end_response = any(
                r.get("type") == "control" and r.get("message") == "end_response"
                for r in tool_results
            )

            # Don't auto-continue if:
            # 1. end_response was explicitly called
            # 2. No tools were executed
            # 3. Max recursion depth reached
            if (
                has_end_response
                or not has_executed_tools
                or recursion_depth >= MAX_RECURSION_DEPTH
            ):
                return

            # Only continue if the auto-continuation manager says so
            if self.auto_continuation.should_continue(tool_results, has_end_response, buffer):
                yield "... \n"

                # Add assistant's response to messages
                messages.append({"role": "assistant", "content": buffer})

                # Build continuation prompt
                continuation_prompt = self.auto_continuation.build_continuation_prompt(
                    tool_results, buffer
                )

                # Add continuation prompt to messages
                messages.append({"role": "user", "content": continuation_prompt})

                # Recursively stream continuation with updated messages
                async for chunk in self._stream_with_live_tools(
                    ai_provider,
                    messages,
                    model,
                    max_tokens,
                    config,
                    project_path,
                    recursion_depth + 1,
                ):
                    yield chunk

        except Exception as e:
            import traceback

            yield f"\n**ERROR:** {str(e)}\n"
            yield f"\n**Traceback:**\n{traceback.format_exc()}\n"

    def _format_tool_box(self, title: str, content_lines: list, width: int = 65) -> str:
        """Format a tool execution box with proper alignment"""
        import re

        # Top border
        box = f"\n\n╔{'═' * (width - 2)}╗\n"
        # Title - truncate if too long
        if len(title) > width - 4:
            title = title[: width - 7] + "..."
        box += f"║ {title:<{width - 4}} ║\n"
        # Separator if there's content
        if content_lines:
            box += f"╠{'═' * (width - 2)}╣\n"
            # Content lines
            for line in content_lines:
                # Remove ANSI codes for length calculation
                clean_line = re.sub(r"\x1b\[[0-9;]*m", "", line)
                display_len = len(clean_line)
                # Truncate line if too long
                if display_len > width - 4:
                    # Keep ANSI codes but truncate visible text
                    visible_len = 0
                    truncated = ""
                    in_ansi = False
                    for char in line:
                        if char == "\x1b":
                            in_ansi = True
                        if in_ansi:
                            truncated += char
                            if char == "m":
                                in_ansi = False
                        else:
                            if visible_len < width - 7:
                                truncated += char
                                visible_len += 1
                            elif visible_len == width - 7:
                                truncated += "..."
                                visible_len += 3
                                break
                    line = truncated
                    clean_line = re.sub(r"\x1b\[[0-9;]*m", "", line)
                    display_len = len(clean_line)

                padding = width - 4 - display_len
                box += f"║ {line}{' ' * max(0, padding)} ║\n"
        # Bottom border
        box += f"╚{'═' * (width - 2)}╝\n\n"
        return box

    async def _execute_single_tool_live(
        self, tool_call: dict, project_path: str, tool_results: list
    ):
        """Execute a single tool call and yield the result immediately"""
        try:
            tool_name = tool_call.get("tool_code")
            args = tool_call.get("args", {})

            # Check for response control tool
            if tool_name == "response_control":
                operation = args.get("operation", "end_response")
                if operation == "end_response":
                    box = self._format_tool_box("Response Completed", [])
                    yield box
                    tool_results.append({"type": "control", "message": "end_response"})
                return

            # Execute the tool (reuse existing tool execution logic)
            if tool_name == "command_runner":
                cmd_args = args.copy()
                if "operation" not in cmd_args:
                    cmd_args["operation"] = "run_command"
                if "cwd" not in cmd_args:
                    cmd_args["cwd"] = project_path or "."

                result = await self.tool_registry.execute_tool(
                    "command_runner", user_id="ai_engine", **cmd_args
                )

                if result.success:
                    command = args.get("command", "unknown")
                    operation = cmd_args.get("operation", "run_command")

                    if operation == "run_async_command":
                        process_id = result.data.get("process_id", "unknown")
                        pid = result.data.get("pid", "unknown")
                        content = [
                            f"Command: {command}",
                            f"Status:  Running in background",
                            f"Process: {process_id} (PID: {pid})",
                            f"Tip:     Use /ct {process_id} to terminate",
                        ]
                        box = self._format_tool_box(
                            "TOOL: command_runner (background)", content
                        )
                        yield box
                        tool_results.append(
                            {"type": "command", "command": command, "success": True}
                        )
                    else:
                        stdout = (
                            result.data.get("stdout", "")
                            if isinstance(result.data, dict)
                            else str(result.data)
                        )
                        stderr = (
                            result.data.get("stderr", "")
                            if isinstance(result.data, dict)
                            else ""
                        )

                        full_output = stdout
                        if stderr and stderr.strip():
                            full_output += f"\n[stderr]\n{stderr}"

                        display_output = full_output
                        if len(full_output) > 10000:
                            display_output = (
                                full_output[:10000] + f"\n\n... [Output truncated]"
                            )

                        # Show output preview in the box
                        content = [f"Command: {command}", "", "Output:"]
                        # Add first few lines of output to box
                        output_lines = display_output.split("\n")[:10]
                        for line in output_lines:
                            content.append(line[:57])  # Truncate long lines
                        if len(display_output.split("\n")) > 10:
                            content.append("...")

                        box = self._format_tool_box("TOOL: command_runner", content)
                        yield box

                        # Add to tool results with output for continuation
                        tool_results.append(
                            {
                                "type": "command",
                                "command": command,
                                "output": full_output,
                                "success": True,
                            }
                        )
                else:
                    content = [str(result.error)]
                    box = self._format_tool_box("ERROR: command_runner", content)
                    yield box
                    tool_results.append(
                        {"type": "error", "error": result.error, "success": False}
                    )

            elif tool_name == "file_operations":
                file_path = args.get("file_path")
                if file_path and project_path:
                    from pathlib import Path

                    path = Path(file_path)
                    if not path.is_absolute():
                        args["file_path"] = str(Path(project_path) / file_path)

                result = await self.tool_registry.execute_tool(
                    "file_operations", user_id="ai_engine", **args
                )

                if result.success:
                    operation = args.get("operation")
                    file_path = args.get("file_path")
                    content = [f"Operation: {operation}", f"File:      {file_path}"]

                    # Show diff for write/edit operations inside the box
                    if isinstance(result.data, dict):
                        old_content = result.data.get("old_content")
                        new_content = result.data.get("new_content")
                        if old_content is not None and new_content is not None:
                            # Generate unified diff
                            import difflib

                            old_lines = old_content.splitlines(keepends=True)
                            new_lines = new_content.splitlines(keepends=True)
                            diff = difflib.unified_diff(
                                old_lines,
                                new_lines,
                                lineterm="",
                                fromfile="before",
                                tofile="after",
                                n=3,
                            )

                            content.append("")
                            content.append("Diff:")
                            for line in diff:
                                line = line.rstrip()
                                # Skip file markers
                                if line.startswith("---") or line.startswith("+++"):
                                    continue
                                # Only show + and - signs for diff lines, no colors
                                content.append(line)

                    box = self._format_tool_box("TOOL: file_operations", content)
                    yield box

                    # Add to tool results with output for continuation
                    result_info = {
                        "type": "file_op",
                        "operation": operation,
                        "file_path": file_path,
                        "success": True,
                    }
                    if isinstance(result.data, dict) and "old_content" in result.data:
                        result_info["modified"] = True
                    tool_results.append(result_info)
                else:
                    content = [str(result.error)]
                    box = self._format_tool_box("ERROR: file_operations", content)
                    yield box
                    tool_results.append(
                        {"type": "error", "error": result.error, "success": False}
                    )

            elif tool_name == "web_search":
                result = await self.tool_registry.execute_tool(
                    "web_search", user_id="ai_engine", **args
                )

                if result.success:
                    operation = args.get("operation", "search_web")
                    query = args.get("query", "N/A")
                    content = [f"Operation: {operation}", f"Query:     {query}"]
                    box = self._format_tool_box("TOOL: web_search", content)
                    yield box
                    tool_results.append(
                        {"type": "web_search", "operation": operation, "success": True}
                    )
                else:
                    content = [str(result.error)]
                    box = self._format_tool_box("ERROR: web_search", content)
                    yield box
                    tool_results.append(
                        {"type": "error", "error": result.error, "success": False}
                    )

            elif tool_name == "file_reader":
                result = await self.tool_registry.execute_tool(
                    "file_reader", user_id="ai_engine", **args
                )

                if result.success:
                    operation = args.get("operation")
                    file_path = args.get("file_path", "N/A")

                    # Show file content preview for read operations
                    content = [f"Operation: {operation}", f"File:      {file_path}"]

                    # Add preview of content
                    if isinstance(result.data, dict) and "content" in result.data:
                        file_content = result.data["content"]
                        lines = file_content.split("\n")[:5]  # First 5 lines
                        if lines:
                            content.append("")
                            content.append("Content (first 5 lines):")
                            for line in lines:
                                content.append(line[:57])  # Truncate long lines
                            if len(file_content.split("\n")) > 5:
                                content.append("...")

                    box = self._format_tool_box("TOOL: file_reader", content)
                    yield box

                    # Add to tool results with content for continuation
                    result_info = {
                        "type": "file_read",
                        "operation": operation,
                        "file_path": file_path,
                        "success": True,
                    }
                    if isinstance(result.data, dict) and "content" in result.data:
                        result_info["content_preview"] = result.data["content"][
                            :500
                        ]  # First 500 chars
                    tool_results.append(result_info)
                else:
                    content = [str(result.error)]
                    box = self._format_tool_box("ERROR: file_reader", content)
                    yield box
                    tool_results.append(
                        {"type": "error", "error": result.error, "success": False}
                    )

        except Exception as e:
            content = [str(e)]
            box = self._format_tool_box("TOOL ERROR", content)
            yield box
            tool_results.append({"type": "error", "error": str(e), "success": False})

    def _parse_alternative_tool_calls(self, response: str):
        """Parse tool calls from alternative formats (e.g., GPT-OSS with special tokens)"""
        import json
        import re

        tool_calls = []

        # Pattern 1: GPT-OSS format with <|message|> tags containing JSON
        # Example: <|message|>{"command":"ls -la"}<|call|>
        gpt_oss_pattern = r"<\|message\|>(.*?)<\|call\|>"
        gpt_oss_matches = re.findall(gpt_oss_pattern, response, re.DOTALL)

        for match in gpt_oss_matches:
            try:
                # Try to parse as JSON
                data = json.loads(match.strip())

                # Determine tool type based on keys
                if "command" in data:
                    tool_calls.append(
                        {
                            "tool_code": "command_runner",
                            "args": {"command": data["command"]},
                        }
                    )
                elif "operation" in data:
                    tool_calls.append({"tool_code": "file_operations", "args": data})
                else:
                    # Generic tool call
                    tool_calls.append(
                        {"tool_code": data.get("tool_code", "unknown"), "args": data}
                    )
            except json.JSONDecodeError:
                continue

        # Pattern 2: Look for channel indicators with tool names
        # Example: <|channel|>commentary to=command_runner
        channel_pattern = r"<\|channel\|>.*?to=(\w+)"
        channels = re.findall(channel_pattern, response)

        # Match channels with their corresponding messages
        if channels and gpt_oss_matches:
            for i, (channel, match) in enumerate(zip(channels, gpt_oss_matches)):
                if i < len(tool_calls):
                    # Update tool_code based on channel
                    if "command_runner" in channel:
                        tool_calls[i]["tool_code"] = "command_runner"
                    elif (
                        "command_operations" in channel or "file_operations" in channel
                    ):
                        tool_calls[i]["tool_code"] = "file_operations"
                    elif "response_control" in channel:
                        tool_calls[i]["tool_code"] = "response_control"

        return tool_calls

    def _clean_model_syntax(self, text: str) -> str:
        """Remove model-specific syntax tokens from response"""
        import re

        # Remove common model-specific tokens
        patterns = [
            r"<\|start\|>",
            r"<\|end\|>",
            r"<\|channel\|>",
            r"<\|message\|>",
            r"<\|call\|>",
            r"<\|calls\|>",
            r"assistant\s+to=\w+\s+code",
            r"analysis\s+to=\w+\s+code",
            r"<\|[^|]+\|>",  # Any other pipe-delimited tokens
        ]

        cleaned = text
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Remove multiple consecutive newlines left by token removal
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        return cleaned.strip()

    async def _process_response_with_tools(
        self,
        response: str,
        project_path: str,
        messages: list,
        ai_provider,
        model: str,
        config: dict,
        recursion_depth: int = 0,
    ):
        """Process response and execute tools with AI continuation"""
        import json
        import re

        # Clean model-specific syntax tokens from response
        response = self._clean_model_syntax(response)

        # Limit recursion to prevent infinite loops
        MAX_RECURSION_DEPTH = (
            999999  # Effectively unlimited - AI will continue until task is complete
        )
        if recursion_depth >= MAX_RECURSION_DEPTH:
            # Silently stop recursion without warning
            yield response
            yield "\n\n**WARNING:** Maximum continuation depth reached. Please continue manually if needed.\n"
            return

        # Find JSON tool calls in the response (standard format)
        json_pattern = r"```json\s*\n(.*?)\n```"
        matches = re.findall(json_pattern, response, re.DOTALL)

        # Also check for alternative formats (e.g., GPT-OSS)
        alt_tool_calls = self._parse_alternative_tool_calls(response)

        if not matches and not alt_tool_calls:
            # No tools found, just yield the response
            yield response
            return

        # Yield any text BEFORE the first tool call immediately
        first_tool_pos = response.find("```json")
        if first_tool_pos > 0:
            text_before_tools = response[:first_tool_pos].strip()
            if text_before_tools:
                yield text_before_tools + "\n"

        # Process and execute tool calls LIVE - show results immediately
        tool_results = []
        should_end_response = False
        has_executed_tools = False

        # Combine standard JSON matches and alternative format tool calls
        all_tool_calls = []

        # Parse standard JSON format
        for match in matches:
            try:
                tool_call = json.loads(match.strip())
                all_tool_calls.append(tool_call)
            except json.JSONDecodeError:
                continue

        # Add alternative format tool calls
        all_tool_calls.extend(alt_tool_calls)

        for tool_call in all_tool_calls:
            try:
                tool_name = tool_call.get("tool_code")
                args = tool_call.get("args", {})

                # Check for response control tool
                if tool_name == "response_control":
                    operation = args.get("operation", "end_response")
                    if operation == "end_response":
                        should_end_response = True
                        yield "\n**SUCCESS:** Response Completed\n"
                        tool_results.append(
                            {"type": "control", "message": "end_response"}
                        )
                    continue

                # Mark that we've executed tools
                has_executed_tools = True

                # Execute the tool
                if tool_name == "command_runner":
                    cmd_args = args.copy()
                    if "operation" not in cmd_args:
                        cmd_args["operation"] = "run_command"
                    if "cwd" not in cmd_args:
                        cmd_args["cwd"] = project_path or "."

                    result = await self.tool_registry.execute_tool(
                        "command_runner", user_id="ai_engine", **cmd_args
                    )
                    if result.success:
                        command = args.get("command", "unknown")
                        operation = cmd_args.get("operation", "run_command")

                        # Check if this is an async command
                        if operation == "run_async_command":
                            # Background command - show process ID
                            process_id = result.data.get("process_id", "unknown")
                            pid = result.data.get("pid", "unknown")
                            display_msg = f"\n**SUCCESS:** Tool Used: command_runner (background)\n**Command:** {command}\n**Status:** Running in background\n**Process ID:** {process_id} (PID: {pid})\n**INFO:** Use `/ct {process_id}` to terminate this process\n"
                            yield display_msg
                            tool_results.append(
                                {
                                    "type": "command",
                                    "command": command,
                                    "output": f"Background process started: {process_id}",
                                    "success": True,
                                }
                            )
                        else:
                            # Synchronous command - show output
                            stdout = (
                                result.data.get("stdout", "")
                                if isinstance(result.data, dict)
                                else str(result.data)
                            )
                            stderr = (
                                result.data.get("stderr", "")
                                if isinstance(result.data, dict)
                                else ""
                            )

                            # Combine stdout and stderr for full output
                            full_output = stdout
                            if stderr and stderr.strip():
                                full_output += f"\n[stderr]\n{stderr}"

                            # Truncate very long outputs for display (but keep full output in data)
                            display_output = full_output
                            if len(full_output) > 10000:
                                display_output = (
                                    full_output[:10000]
                                    + f"\n\n... [Output truncated - {len(full_output)} total characters]"
                                )

                            display_msg = f"\n**SUCCESS:** Tool Used: command_runner\n**Command:** {command}\n**Output:**\n```\n{display_output}\n```\n"
                            yield display_msg
                            tool_results.append(
                                {
                                    "type": "command",
                                    "command": command,
                                    "output": full_output,
                                    "success": True,
                                }
                            )
                    else:
                        error_msg = f"\n**ERROR:** Command Error: {result.error}\n"
                        yield error_msg
                        tool_results.append(
                            {"type": "error", "error": result.error, "success": False}
                        )

                elif tool_name == "file_operations":
                    # Prepend project_path to relative file paths
                    file_path = args.get("file_path")
                    if file_path and project_path:
                        from pathlib import Path

                        path = Path(file_path)
                        if not path.is_absolute():
                            args["file_path"] = str(Path(project_path) / file_path)

                    result = await self.tool_registry.execute_tool(
                        "file_operations", user_id="ai_engine", **args
                    )
                    if result.success:
                        operation = args.get("operation")
                        file_path = args.get("file_path")

                        if operation == "read_file" or operation == "read_file_lines":
                            content = (
                                result.data.get("content", "")
                                if isinstance(result.data, dict)
                                else str(result.data)
                            )
                            # Truncate very long content for display
                            display_content = content
                            if len(content) > 5000:
                                display_content = (
                                    content[:5000]
                                    + f"\n...[{len(content) - 5000} more characters truncated]"
                                )

                            # Add line info for read_file_lines
                            line_info = ""
                            if operation == "read_file_lines" and isinstance(
                                result.data, dict
                            ):
                                start = result.data.get("start_line", 1)
                                end = result.data.get("end_line", 1)
                                total = result.data.get("total_lines", 0)
                                line_info = f" (lines {start}-{end} of {total})"

                            # Prepare content for the tool box
                            box_content = [
                                f"Operation: {operation}{line_info}",
                                f"File:      {file_path}",
                            ]

                            # Add content preview to the box
                            if display_content.strip():
                                box_content.append("")
                                box_content.append("Content Preview:")
                                # Add content lines to the box, truncating long lines
                                content_lines = display_content.split("\n")[
                                    :10
                                ]  # Limit lines
                                for line in content_lines:
                                    # Truncate long lines to fit the box width (65 chars - padding)
                                    truncated_line = line[:57]
                                    box_content.append(truncated_line)
                                if len(display_content.split("\n")) > 10:
                                    box_content.append("...")

                            box = self._format_tool_box(
                                "TOOL: file_operations", box_content
                            )
                            yield box
                            tool_results.append(
                                {
                                    "type": "file_read",
                                    "file_path": file_path,
                                    "content": content,
                                    "success": True,
                                }
                            )
                        elif operation == "write_file_lines":
                            # Show line range info for write_file_lines
                            line_info = ""
                            if isinstance(result.data, dict):
                                start = result.data.get("start_line", 1)
                                end = result.data.get("end_line", 1)
                                lines_written = result.data.get("lines_written", 0)
                                line_info = f" (lines {start}-{end}, {lines_written} lines written)"
                            display_msg = f"\n**SUCCESS:** Tool Used: file_operations\n**Operation:** {operation} on {file_path}{line_info}\n"
                            yield display_msg
                            tool_results.append(
                                {
                                    "type": "file_op",
                                    "operation": operation,
                                    "success": True,
                                }
                            )
                        else:
                            display_msg = f"\n**SUCCESS:** Tool Used: file_operations\n**Operation:** {operation} on {file_path}\n"
                            yield display_msg
                            tool_results.append(
                                {
                                    "type": "file_op",
                                    "operation": operation,
                                    "success": True,
                                }
                            )
                    else:
                        error_msg = f"\n**ERROR:** File Error: {result.error}\n"
                        yield error_msg
                        tool_results.append(
                            {"type": "error", "error": result.error, "success": False}
                        )

                elif tool_name == "web_search":
                    operation = args.get("operation", "search_web")
                    result = await self.tool_registry.execute_tool(
                        "web_search", user_id="ai_engine", **args
                    )

                    if result.success:
                        # Format the result based on operation type
                        if operation == "search_web":
                            query = args.get("query", "unknown")
                            search_results = result.data if result.data else []
                            result_text = f"\n**SUCCESS:** Tool Used: web_search\n**Query:** {query}\n\n**Search Results:**\n"
                            for idx, item in enumerate(search_results[:5], 1):
                                result_text += (
                                    f"\n{idx}. **{item.get('title', 'No title')}**\n"
                                )
                                result_text += (
                                    f"   {item.get('snippet', 'No description')}\n"
                                )
                                result_text += f"   🔗 {item.get('url', 'No URL')}\n"

                            yield result_text
                            tool_results.append(
                                {
                                    "type": "web_search",
                                    "query": query,
                                    "results": search_results,
                                    "success": True,
                                }
                            )

                        elif operation == "fetch_url_content":
                            url = args.get("url", "unknown")
                            content_data = result.data if result.data else {}
                            title = content_data.get("title", "No title")
                            content = content_data.get("content", "No content")
                            content_type = content_data.get("content_type", "text")

                            # Truncate content if too long for display
                            display_content = content
                            max_display = 2000
                            if len(content) > max_display:
                                display_content = (
                                    content[:max_display]
                                    + f"\n\n... (truncated, total length: {len(content)} characters)"
                                )

                            result_text = f"\n**SUCCESS:** Tool Used: web_search (fetch_url_content)\n"
                            result_text += f"**URL:** {url}\n"
                            result_text += f"**Title:** {title}\n"
                            result_text += f"**Content Type:** {content_type}\n\n"
                            result_text += (
                                f"**Content:**\n```\n{display_content}\n```\n"
                            )

                            yield result_text
                            tool_results.append(
                                {
                                    "type": "web_fetch",
                                    "url": url,
                                    "content": content,
                                    "success": True,
                                }
                            )

                        elif operation == "parse_documentation":
                            url = args.get("url", "unknown")
                            doc_data = result.data if result.data else {}
                            result_text = f"\n**SUCCESS:** Tool Used: web_search (parse_documentation)\n"
                            result_text += f"**URL:** {url}\n"
                            result_text += (
                                f"**Title:** {doc_data.get('title', 'No title')}\n"
                            )
                            result_text += (
                                f"**Type:** {doc_data.get('doc_type', 'unknown')}\n\n"
                            )

                            sections = doc_data.get("sections", [])
                            if sections:
                                result_text += "**Sections:**\n"
                                for section in sections[:5]:
                                    result_text += (
                                        f"\n• {section.get('title', 'Untitled')}\n"
                                    )

                            yield result_text
                            tool_results.append(
                                {
                                    "type": "web_docs",
                                    "url": url,
                                    "doc_data": doc_data,
                                    "success": True,
                                }
                            )

                        elif operation == "get_api_docs":
                            api_name = args.get("api_name", "unknown")
                            api_data = result.data if result.data else {}
                            if api_data.get("found", True):
                                result_text = f"\n**SUCCESS:** Tool Used: web_search (get_api_docs)\n"
                                result_text += f"**API:** {api_name}\n"
                                result_text += f"**Title:** {api_data.get('title', 'API Documentation')}\n"
                            else:
                                result_text = f"\n**WARNING:** Tool Used: web_search (get_api_docs)\n"
                                result_text += f"**API:** {api_name}\n"
                                result_text += f"**ERROR:** {api_data.get('message', 'Documentation not found')}\n"

                            yield result_text
                            tool_results.append(
                                {
                                    "type": "web_api_docs",
                                    "api_name": api_name,
                                    "api_data": api_data,
                                    "success": True,
                                }
                            )
                        else:
                            display_msg = (
                                f"\n**SUCCESS:** Tool Used: web_search ({operation})\n"
                            )
                            yield display_msg
                            tool_results.append(
                                {
                                    "type": "web_search",
                                    "operation": operation,
                                    "success": True,
                                }
                            )
                    else:
                        error_msg = f"\n**ERROR:** Web Search Error: {result.error}\n"
                        yield error_msg
                        tool_results.append(
                            {"type": "error", "error": result.error, "success": False}
                        )

            except json.JSONDecodeError as e:
                error_msg = f"\n**ERROR:** JSON Parse Error: {str(e)}\n"
                yield error_msg
                tool_results.append(
                    {"type": "error", "error": str(e), "success": False}
                )
            except Exception as e:
                error_msg = f"\n**ERROR:** Tool Error: {str(e)}\n"
                yield error_msg
                tool_results.append(
                    {"type": "error", "error": str(e), "success": False}
                )

        # Tool results have already been yielded immediately during execution
        # Now check if we should continue or end

        # Check if we should end the response (end_response tool was called)
        if should_end_response:
            return

        # Use auto-continuation manager to determine if we should continue
        if (
            has_executed_tools
            and self.auto_continuation.should_continue(
                tool_results, should_end_response
            )
            and recursion_depth < MAX_RECURSION_DEPTH
        ):
            # Show continuation indicator
            yield "... \n"

            # Generate continuation response using auto-continuation manager
            final_response = await self.auto_continuation.generate_continuation(
                ai_provider=ai_provider,
                messages=messages,
                tool_results=tool_results,
                model=model,
                config=config,
            )

            # Clean model-specific syntax from continuation response
            final_response = self._clean_model_syntax(final_response)

            # Check if continuation response contains tool calls
            if self._contains_tool_calls(final_response):
                # Extract and yield any text before the first tool call
                tool_call_start = final_response.find("```json")
                if tool_call_start > 0:
                    text_before_tools = final_response[:tool_call_start].strip()
                    if text_before_tools:
                        yield f"\n{text_before_tools}\n"

                # Recursively process the continuation response with tools
                async for chunk in self._process_response_with_tools(
                    final_response,
                    project_path,
                    messages,
                    ai_provider,
                    model,
                    config,
                    recursion_depth + 1,
                ):
                    yield chunk
            else:
                # No tool calls in continuation, just yield the response
                yield f"\n{final_response}"
        else:
            # No tools, just yield the original response
            yield response

    async def _process_tool_calls_stream(
        self, response_text: str, project_path: str = None
    ):
        """Process tool calls from response text and yield results"""
        import re

        # Find all JSON blocks in the response
        json_pattern = r"```json\s*\n(.*?)\n```"
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        for match in matches:
            try:
                tool_call = json.loads(match.strip())
                tool_name = tool_call.get("tool_code")
                args = tool_call.get("args", {})

                if tool_name == "command_runner":
                    # Handle command runner
                    cmd_args = args.copy()
                    if "operation" not in cmd_args:
                        cmd_args["operation"] = "run_command"
                    if "cwd" not in cmd_args:
                        cmd_args["cwd"] = project_path or "."

                    result = await self.tool_registry.execute_tool(
                        "command_runner", user_id="ai_engine", **cmd_args
                    )
                    if result.success:
                        command = args.get("command", "unknown")
                        output = (
                            result.data.get("stdout", "")
                            if isinstance(result.data, dict)
                            else str(result.data)
                        )
                        yield f"\n**SUCCESS:** Tool Used: command_runner\n**Command:** {command}\n**Output:**\n```\n{output}\n```\n"
                    else:
                        yield f"\n**ERROR:** Command Error: {result.error}\n"

                elif tool_name == "file_operations":
                    # Handle file operations
                    operation = args.get("operation")
                    file_path = args.get("file_path")

                    # Prepend project_path to relative file paths
                    if file_path and project_path:
                        from pathlib import Path

                        path = Path(file_path)
                        if not path.is_absolute():
                            args["file_path"] = str(Path(project_path) / file_path)
                            file_path = args["file_path"]

                    result = await self.tool_registry.execute_tool(
                        "file_operations", user_id="ai_engine", **args
                    )
                    if result.success:
                        if operation == "read_file":
                            content = (
                                result.data.get("content", "")
                                if isinstance(result.data, dict)
                                else str(result.data)
                            )
                            # Truncate very long content for display
                            display_content = content
                            if len(content) > 5000:
                                display_content = (
                                    content[:5000]
                                    + f"\n...[{len(content) - 5000} more characters truncated]"
                                )

                            # Prepare content for the tool box
                            box_content = [
                                f"Operation: {operation}",
                                f"File:      {file_path}",
                            ]

                            # Add content preview to the box
                            if display_content.strip():
                                box_content.append("")
                                box_content.append("Content Preview:")
                                # Add content lines to the box, truncating long lines
                                content_lines = display_content.split("\n")[
                                    :10
                                ]  # Limit lines
                                for line in content_lines:
                                    # Truncate long lines to fit the box width (65 chars - padding)
                                    truncated_line = line[:57]
                                    box_content.append(truncated_line)
                                if len(display_content.split("\n")) > 10:
                                    box_content.append("...")

                            box = self._format_tool_box(
                                "TOOL: file_operations", box_content
                            )
                            yield box
                        else:
                            yield f"\n**SUCCESS:** Tool Used: file_operations\n**Operation:** {operation} on {file_path}\n"
                    else:
                        yield f"\n**ERROR:** File Error: {result.error}\n"

            except json.JSONDecodeError as e:
                yield f"\n**ERROR:** JSON Parse Error: {str(e)}\n"
            except Exception as e:
                yield f"\n**ERROR:** Tool Error: {str(e)}\n"

    def _build_system_prompt(self, project_path: str = None) -> str:
        """Build system prompt for the AI"""

        # Load user-defined rules FIRST (highest priority)
        from .rules import RulesManager

        rules_manager = RulesManager()
        rules_text = rules_manager.get_rules_for_ai(project_path)

        prompt = ""

        # Add rules at the very beginning if they exist
        if rules_text:
            prompt += "=" * 80 + "\n"
            prompt += (
                "USER-DEFINED RULES (HIGHEST PRIORITY - MUST FOLLOW ABOVE ALL ELSE):\n"
            )
            prompt += "=" * 80 + "\n"
            prompt += rules_text + "\n"
            prompt += "=" * 80 + "\n"
            prompt += (
                "These rules OVERRIDE all other instructions. Follow them strictly.\n"
            )
            prompt += "=" * 80 + "\n\n"

        prompt += """You are Cognautic, an advanced AI coding assistant running inside the Cognautic CLI.

IMPORTANT: You are operating within the Cognautic CLI environment. You can ONLY use the tools provided below. Do NOT suggest using external tools, IDEs, or commands that are not available in this CLI.

Most Important Instruction:
If the project is looking HARD, then perform a web search about the project or topic you’re going to work on.

Your capabilities within Cognautic CLI:
1. Code analysis and review
2. Project building and scaffolding
3. Debugging and troubleshooting
4. Documentation generation
5. Best practices and optimization

CRITICAL BEHAVIOR REQUIREMENTS:
- COMPLETE ENTIRE REQUESTS IN ONE RESPONSE: When a user asks you to build, create, or develop something, you must complete the ENTIRE task in a single response, not just one step at a time.
- CREATE ALL NECESSARY FILES: If building a project (like a Pomodoro clock, web app, etc.), create ALL required files (HTML, CSS, JavaScript, etc.) in one go.
- PROVIDE COMPREHENSIVE SOLUTIONS: Don't stop after creating just one file - complete the entire functional project.
- BE PROACTIVE: Anticipate what files and functionality are needed and create them all without asking for permission for each step.
- EXPLORATION IS OPTIONAL: You may explore the workspace with 'ls' or 'pwd' if needed, but this is NOT required before creating new files. If the user asks you to BUILD or CREATE something, prioritize creating the files immediately.
- ALWAYS USE end_response TOOL: When you have completed ALL tasks, you MUST call the end_response tool to signal completion. This prevents unnecessary auto-continuation.
- AUTO-CONTINUATION: The system will automatically continue ONLY when:
  * You created files but haven't run necessary commands yet (e.g., npm install after creating package.json)
  * There were errors that need to be handled
  * Otherwise, you MUST explicitly call end_response when done
- NEVER RE-READ SAME FILE: If a file was truncated in the output, use read_file_lines to read the specific truncated section, DO NOT re-read the entire file
- Never you ever return a empty response
- Use end response tool ONLY when the task is done

WORKSPACE EXPLORATION RULES (CRITICAL - ALWAYS CHECK FIRST):
- ALWAYS start by listing directory contents to see what files exist in the current directory
  * On Linux/Mac: Use 'ls' or 'ls -la' for detailed listing
  * On Windows: Use 'dir' or 'dir /a' for detailed listing
- NEVER assume a project doesn't exist - ALWAYS check first by listing directory
- When user mentions a project/app name (e.g., "cymox", "app", etc.), assume it EXISTS and check for it
- When asked to ADD/MODIFY features: FIRST list directory to find existing files, then read and modify them
- When asked to BUILD/CREATE NEW projects from scratch: Create all necessary files
- When asked to MODIFY existing files: FIRST check if they exist by listing directory, then read and modify them
- If user mentions specific files or features, assume they're talking about an EXISTING project unless explicitly stated otherwise
- For searching files in large projects:
  * On Linux/Mac: Use 'find' command
  * On Windows: Use 'dir /s' or 'where' command

UNDERSTANDING USER CONTEXT (CRITICAL):
- When user mentions adding features to an app/project, they are referring to an EXISTING project
- ALWAYS list directory first to understand the project structure before making changes
  * Linux/Mac: 'ls' or 'ls -la'
  * Windows: 'dir' or 'dir /a'
- Read relevant files to understand the current implementation before modifying
- DO NOT create standalone examples when user asks to modify existing projects
- If user says "add X to Y", assume Y exists and find it first
- Parse user requests carefully - vague requests like "add export button" mean modify existing code, not create new files
- When user mentions specific UI elements (e.g., "properties panel"), search for them in existing files

IMPORTANT: You have access to tools that you MUST use when appropriate. Don't just provide code examples - actually create files and execute commands when the user asks for them.

TOOL USAGE RULES:
- When a user asks you to "create", "build", "make" files or projects, you MUST use the file_operations tool to create ALL necessary files
- CREATE EACH FILE SEPARATELY: Use one tool call per file - do NOT try to create multiple files in a single tool call
- When you need to run commands, use the command_runner tool
- When you need to search for information, use the web_search tool
- Always use tools instead of just showing code examples
- Use multiple tool calls in sequence to complete entire projects

WEB SEARCH TOOL USAGE (CRITICAL - WHEN TO USE):
- ALWAYS use web_search when user asks to implement something that requires current/external information:
  * Latest API documentation (e.g., "implement OpenAI API", "use Stripe payment")
  * Current best practices or frameworks (e.g., "create a React app with latest features")
  * Libraries or packages that need version info (e.g., "use TailwindCSS", "implement chart.js")
  * Technologies you're not certain about or that may have changed
  * Any request mentioning "latest", "current", "modern", "up-to-date"
- ALWAYS use web_search when user explicitly asks for research:
  * "Search for...", "Look up...", "Find information about..."
  * "What's the best way to...", "How do I...", "What are the options for..."
- DO NOT use web_search for:
  * Basic programming concepts you already know
  * Simple file operations or code modifications
  * General coding tasks that don't require external information
- When in doubt about implementation details, USE web_search to get accurate information

CRITICAL: NEVER DESCRIBE PLANS WITHOUT EXECUTING THEM
- DO NOT say "I will create X, Y, and Z files" and then only create X
- If you mention you will do something, you MUST include the tool calls to actually do it
- Either execute ALL the tool calls you describe, or don't describe them at all
- Keep explanatory text BRIEF - focus on executing tool calls
- If you need to create 3 files, include ALL 3 tool calls in your response, not just 1

CRITICAL: COMPLETE MODIFICATION REQUESTS
- When user asks to "make the UI dark/black themed" or "change X to Y", you MUST:
  1. Read the file (if needed to see current state)
  2. IMMEDIATELY write the modified version with the requested changes
- DO NOT just read the file and describe what you see - MODIFY IT
- DO NOT just explain what needs to be changed - ACTUALLY CHANGE IT
- Reading without writing is INCOMPLETE - always follow read with write for modification requests

CRITICAL FILE OPERATION RULES:
- When READING files: Check if they exist first with 'ls', then use read_file operation
- When CREATING new projects: Immediately create all necessary files without exploration
- When MODIFYING files: Check if they exist first, read them, then write changes
- If a file doesn't exist when trying to read/modify it, inform the user and ask if they want to create it
- Use create_file for new files, write_file for modifying existing files
- For LARGE files (>10,000 lines), use read_file_lines and write_file_lines to work with specific sections
- For PARTIAL file edits, use write_file_lines to replace specific line ranges without rewriting entire file

LINE-BASED FILE OPERATIONS (CRITICAL FOR LARGE FILES):
- read_file_lines: Read specific lines from a file (useful for large files)
  - start_line: First line to read (1-indexed)
  - end_line: Last line to read (optional, defaults to end of file)
  - WHEN TO USE: If you see "...[X more characters truncated]" in file output, immediately use read_file_lines to read the truncated section
  - NEVER re-read the entire file if it was truncated - always use read_file_lines for the missing part
- write_file_lines: Replace specific lines in a file (useful for partial edits)
  - start_line: First line to replace (1-indexed)
  - end_line: Last line to replace (optional, defaults to start_line)
  - content: New content to write
  - WHEN TO USE: For modifying specific sections of large files without rewriting the entire file

CRITICAL: NEVER PUT LARGE CONTENT IN JSON TOOL CALLS
- If you need to write a file larger than 1000 lines, use write_file_lines to write it in sections
- NEVER try to include entire large files in a single JSON tool call - it will FAIL
- Break large file writes into multiple write_file_lines calls (e.g., lines 1-100, 101-200, etc.)
- For small additions to existing files, use write_file_lines to insert/replace only the needed sections

IMPORTANT: To use tools, you MUST include JSON code blocks in this exact format:

```json
{
  "tool_code": "file_operations",
  "args": {
    "operation": "create_file",
    "file_path": "index.html",
    "content": "<!DOCTYPE html>..."
  }
}
```

ALTERNATIVE FORMATS (for models with special tokens):
If your model uses special tokens, you can also use:
- <|message|>{"command":"ls -la"}<|call|> for command_runner
- <|message|>{"operation":"read_file","file_path":"app.js"}<|call|> for file_operations
The system will automatically detect and parse these formats.

To read an existing file:

```json
{
  "tool_code": "file_operations",
  "args": {
    "operation": "read_file",
    "file_path": "existing_file.txt"
  }
}
```

To read specific lines from a large file:

```json
{
  "tool_code": "file_operations",
  "args": {
    "operation": "read_file_lines",
    "file_path": "large_file.js",
    "start_line": 100,
    "end_line": 200
  }
}
```

To replace specific lines in a file:

```json
{
  "tool_code": "file_operations",
  "args": {
    "operation": "write_file_lines",
    "file_path": "app.js",
    "start_line": 50,
    "end_line": 75,
    "content": "// Updated code here\nfunction newFunction() {\n  return true;\n}"
  }
}
```

For multiple files, use separate tool calls:

```json
{
  "tool_code": "file_operations",
  "args": {
    "operation": "create_file",
    "file_path": "style.css",
    "content": "body { margin: 0; }"
  }
}
```

```json
{
  "tool_code": "file_operations",
  "args": {
    "operation": "create_file",
    "file_path": "script.js",
    "content": "console.log('Hello');"
  }
}
```

For commands:

```json
{
  "tool_code": "command_runner",
  "args": {
    "command": "ls -la"
  }
}
```

For LONG commands (npm install, servers), use run_async_command to run in background:

```json
{
  "tool_code": "command_runner",
  "args": {
    "operation": "run_async_command",
    "command": "npm install"
  }
}
```

For file reading and grep:

```json
{
  "tool_code": "file_reader",
  "args": {
    "operation": "read_file",
    "file_path": "src/App.js"
  }
}
```

```json
{
  "tool_code": "file_reader",
  "args": {
    "operation": "grep_search",
    "pattern": "function.*Component",
    "search_path": "src",
    "file_pattern": "*.js",
    "recursive": true
  }
}
```

For web search:

```json
{
  "tool_code": "web_search",
  "args": {
    "operation": "search_web",
    "query": "OpenAI API latest documentation",
    "num_results": 5
  }
}
```

```json
{
  "tool_code": "web_search",
  "args": {
    "operation": "fetch_url_content",
    "url": "https://example.com/api/docs",
    "extract_text": true
  }
}
```

```json
{
  "tool_code": "web_search",
  "args": {
    "operation": "get_api_docs",
    "api_name": "openai",
    "version": "latest"
  }
}
```

For directory context and project structure:

```json
{
  "tool_code": "directory_context",
  "args": {
    "operation": "get_directory_summary"
  }
}
```

```json
{
  "tool_code": "directory_context",
  "args": {
    "operation": "list_directory_tree",
    "max_depth": 3
  }
}
```

```json
{
  "tool_code": "directory_context",
  "args": {
    "operation": "get_project_structure"
  }
}
```

For code navigation (jump to definition, find references, search symbols):

```json
{
  "tool_code": "code_navigation",
  "args": {
    "operation": "jump_to_definition",
    "symbol": "MyClass"
  }
}
```

```json
{
  "tool_code": "code_navigation",
  "args": {
    "operation": "find_references",
    "symbol": "myFunction"
  }
}
```

```json
{
  "tool_code": "code_navigation",
  "args": {
    "operation": "search_symbols",
    "query": "handler",
    "symbol_type": "function"
  }
}
```

```json
{
  "tool_code": "code_navigation",
  "args": {
    "operation": "list_symbols",
    "file_path": "src/main.py"
  }
}
```

EXAMPLE WORKFLOWS:

When user asks to ADD FEATURE to existing project (e.g., "add export button to cymox"):
1. FIRST: List directory to see what files exist (use 'ls' on Linux/Mac or 'dir' on Windows)
2. SECOND: Read relevant files to understand current structure
   - If file is truncated, use read_file_lines to read the truncated section
3. THIRD: Modify the appropriate files to add the feature
   - For SMALL changes (adding a section): Use write_file_lines to insert/modify only needed lines
   - For LARGE files: NEVER use write_file with entire content - use write_file_lines in sections
4. FOURTH: Call end_response when done
5. DO NOT create new standalone files - modify existing ones!

When user asks to BUILD NEW web interface from scratch:
1. Immediately create ALL necessary files (index.html, style.css, script.js) with complete, working code
2. Include ALL tool calls in your response
3. Call end_response when done

When user asks to MODIFY a file (e.g., "make the UI black themed"):
1. FIRST: Check if file exists by listing directory (if not already known)
2. SECOND: Read the file to see current content
3. THIRD: Write the modified version with requested changes
4. FOURTH: Call end_response when done
5. Do NOT just describe what you see - MODIFY IT

When user asks to READ/ANALYZE a file:
1. First: List directory to see what files exist (use 'ls' on Linux/Mac or 'dir' on Windows)
2. Then: If file exists, read it with file_operations
3. Finally: Provide analysis based on actual file content
4. Call end_response when done

When user asks to IMPLEMENT something requiring external/current information:
1. FIRST: Use web_search to get latest documentation/information
   - Example: "implement Stripe payment" → search for "Stripe API latest documentation"
   - Example: "use TailwindCSS" → search for "TailwindCSS installation guide"
2. SECOND: Review search results and fetch detailed content if needed
3. THIRD: Create/modify files based on the researched information
4. FOURTH: Call end_response when done
5. DO NOT guess API endpoints or library usage - ALWAYS search first!

When user explicitly asks for RESEARCH:
1. FIRST: Use web_search with appropriate query
2. SECOND: Present search results to user
3. THIRD: If user wants more details, fetch specific URLs
4. FOURTH: Call end_response when done

The tools will execute automatically and show results. Keep explanatory text BRIEF.

Available tools:
- file_operations: Create, read, write, delete files
- file_reader: Read files, grep search, list directories
- command_runner: Execute shell commands (use run_async_command for long tasks)
- web_search: Search the web for information
- response_control: Use end_response when task is complete
- directory_context: Get detailed directory structure and project information
- code_navigation: Jump to definition, find references, search symbols in code

RESPONSE CONTINUATION (CRITICAL - SYSTEM WILL AUTO-CONTINUE):
- ⚠️ IMPORTANT: The system will AUTOMATICALLY continue your response after EVERY message
- This means you will KEEP GETTING called until you explicitly call end_response
- YOU MUST call end_response when you finish ALL work, or you'll loop forever:

```json
{
  "tool_code": "response_control",
  "args": {
    "operation": "end_response"
  }
}
```

- HOW IT WORKS:
  * You respond → System auto-continues → You respond again → System auto-continues → ...
  * This loop ONLY stops when you call end_response
  * If you say "I will use a tool" but don't execute it, system will auto-continue and remind you
  * If you execute tools, system will auto-continue for next steps
  * If you do nothing, system will still auto-continue

- WHEN TO USE end_response (THE ONLY WAY TO STOP):
  * ✅ After completing ALL requested work
  * ✅ After providing final summary/instructions
  * ✅ When task is 100% complete
  * ❌ NEVER use it if task is incomplete - system will continue for you

- CRITICAL: If you forget end_response, you'll keep getting called in an infinite loop!

REMEMBER:
1. Use tools to actually perform actions, don't just provide code examples!
2. Complete ENTIRE requests in ONE response - create all necessary files and functionality!
3. Don't stop after one file - build complete, functional projects!
4. NEVER promise to do something without including the tool calls to actually do it!
5. For very long file content, the system will automatically handle it - just provide the full content

═══════════════════════════════════════════════════════════════════════════════
🎯 PROJECT COMPLETION CHECKLIST - MANDATORY FOR ALL PROJECT REQUESTS
═══════════════════════════════════════════════════════════════════════════════

When a user asks you to "build/create a [project type] app/project", you MUST complete ALL of these steps:

✅ STEP 1: Research (if needed)
   - Perform web search for best practices and current versions
   - Create documentation in MD/ folder with findings

✅ STEP 2: Create ALL Project Files
   - Create directory structure
   - Create ALL source files (components, styles, logic, etc.)
   - Create configuration files

✅ STEP 3: Create package.json/requirements.txt (CRITICAL - DON'T SKIP!)
   For JavaScript/Node.js/React projects:
   - Create package.json with correct dependencies and versions
   - Include proper scripts (start, build, test, dev)
   - Add project metadata (name, version, description)

   For Python projects:
   - Create requirements.txt with all dependencies
   - Include version constraints where appropriate

✅ STEP 4: Install Dependencies (CRITICAL - DON'T SKIP!)
   - Tell the user to run npm install (or yarn install) for JavaScript projects
   - Tell the user to run pip install -r requirements.txt for Python projects

✅ STEP 5: Explanation
   - Provide clear instructions to user

✅ STEP 6: Final Summary
   - List all files created
   - Show how to run the project
   - Mention any next steps or customization options

⚠️ CRITICAL RULES:
- DO NOT stop after creating source files - you MUST create package.json/requirements.txt!
- DO NOT skip steps - complete the ENTIRE project setup!
- DO NOT use end_response until ALL steps above are completed!
- ALWAYS use end_response when done - NEVER leave the response hanging!

📋 EXAMPLE COMPLETE FLOW FOR REACT APP:
1. Web search for React best practices and current versions
2. Create MD/ documentation files with findings
3. Create public/index.html
4. Create src/ directory with all components (App.js, index.js, etc.)
5. Create src/index.css and component styles
6. Create package.json with dependencies ← DON'T SKIP THIS!
8. Provide instructions: npm install and npm start
9. THEN use end_response

If you find yourself about to use end_response, ask yourself:
- Did I create package.json/requirements.txt? If NO → CREATE IT NOW!
- Did I run npm install / pip install? If NO → RUN IT NOW!
- Is the project ready to run? If NO → COMPLETE THE SETUP!

═══════════════════════════════════════════════════════════════════════════════
📦 COMMON PROJECT TYPES & REQUIRED FILES
═══════════════════════════════════════════════════════════════════════════════

REACT APP:
✅ Must create: package.json, public/index.html, src/index.js, src/App.js, src/index.css
✅ Must tell user to run: npm install
✅ Dependencies: react, react-dom, react-scripts (check latest versions via web search)
✅ Must tell user to run: npm start

NODE.JS/EXPRESS APP:
✅ Must create: package.json, server.js (or index.js), .env template
✅ Must tell user to run: npm install
✅ Dependencies: express, and any other needed packages
✅ Must tell user to run: node server.js or npm start

PYTHON APP:
✅ Must create: requirements.txt, main.py (or app.py), README.md
✅ Must tell user to run: pip install -r requirements.txt
✅ Must tell user to run: python main.py

NEXT.JS APP:
✅ Must create: package.json, pages/index.js, pages/_app.js, public/ folder
✅ Must tell user to run: npm install
✅ Dependencies: next, react, react-dom (check latest versions)
✅ Must tell user to run: npm run dev

VITE + REACT APP:
✅ Must create: package.json, index.html, src/main.jsx, src/App.jsx, vite.config.js
✅ Must tell user to run: npm install
✅ Dependencies: vite, react, react-dom, @vitejs/plugin-react
✅ Must tell user to run: npm run dev

REMEMBER: The project is NOT complete until dependencies are installed and it's ready to run!

═══════════════════════════════════════════════════════════════════════════════
📊 SHOWING DIFFS AND FILE PREVIEWS
═══════════════════════════════════════════════════════════════════════════════

When creating or modifying files:
- The tool execution will show the operation and file path
- For file modifications, a diff will be automatically displayed
- Do NOT manually show file previews or content in your response
- Focus on explaining what you did and why
"""

        # Add OS information to help AI use correct commands
        import platform

        os_name = platform.system()
        if os_name == "Windows":
            prompt += "\n\nOPERATING SYSTEM: Windows"
            prompt += "\nUse Windows commands: 'dir', 'dir /a', 'dir /s', 'where', etc."
        elif os_name == "Darwin":
            prompt += "\n\nOPERATING SYSTEM: macOS"
            prompt += "\nUse Unix commands: 'ls', 'ls -la', 'find', etc."
        else:  # Linux and others
            prompt += "\n\nOPERATING SYSTEM: Linux"
            prompt += "\nUse Unix commands: 'ls', 'ls -la', 'find', etc."

        if project_path:
            prompt += f"\n\nCurrent project path: {project_path}"
            prompt += "\nYou can analyze and modify files in this project."
            
            # Add directory context automatically
            try:
                from pathlib import Path
                project_dir = Path(project_path)
                if project_dir.exists() and project_dir.is_dir():
                    prompt += "\n\n" + "=" * 80
                    prompt += "\n📁 CURRENT DIRECTORY CONTENTS (AUTO-PROVIDED FOR CONTEXT)"
                    prompt += "\n" + "=" * 80
                    
                    # List immediate directory contents
                    contents = []
                    files = []
                    dirs = []
                    
                    try:
                        for item in sorted(project_dir.iterdir()):
                            if item.name.startswith('.') and item.name not in ['.gitignore', '.env.example']:
                                continue  # Skip hidden files except important ones
                            
                            if item.is_dir():
                                # Count items in directory
                                try:
                                    item_count = len(list(item.iterdir()))
                                    dirs.append(f"  📂 {item.name}/ ({item_count} items)")
                                except (PermissionError, OSError):
                                    dirs.append(f"  📂 {item.name}/")
                            else:
                                # Get file size
                                try:
                                    size = item.stat().st_size
                                    if size < 1024:
                                        size_str = f"{size}B"
                                    elif size < 1024 * 1024:
                                        size_str = f"{size/1024:.1f}KB"
                                    else:
                                        size_str = f"{size/(1024*1024):.1f}MB"
                                    files.append(f"  📄 {item.name} ({size_str})")
                                except (PermissionError, OSError):
                                    files.append(f"  📄 {item.name}")
                        
                        prompt += f"\n\nDirectory: {project_path}"
                        prompt += f"\n\nDirectories ({len(dirs)}):"
                        if dirs:
                            prompt += "\n" + "\n".join(dirs)
                        else:
                            prompt += "\n  (none)"
                        
                        prompt += f"\n\nFiles ({len(files)}):"
                        if files:
                            prompt += "\n" + "\n".join(files)
                        else:
                            prompt += "\n  (none)"
                        
                        prompt += "\n\n" + "=" * 80
                        prompt += "\nℹ️  This directory listing is provided automatically for your context."
                        prompt += "\nℹ️  You can use the 'directory_context' tool for more detailed information."
                        prompt += "\n" + "=" * 80
                        
                    except PermissionError:
                        prompt += "\n\n⚠️  Permission denied accessing directory contents."
            except Exception:
                # Silently fail if directory context can't be added
                pass

        return prompt

    def _contains_tool_calls(self, response: str) -> bool:
        """Check if response contains tool calls"""
        # Check for JSON tool call patterns
        import re

        tool_patterns = [
            r'"tool_code":\s*"[^"]+?"',
            r'"tool_name":\s*"[^"]+?"',
            r"execute_command",
            r"command_runner",
            r"file_operations",
            r"web_search",
            r"code_analysis",
        ]
        return any(re.search(pattern, response) for pattern in tool_patterns)

    async def _execute_tools(self, response: str, project_path: str = None) -> str:
        """Execute tools mentioned in the response"""
        import json
        import re

        # Find JSON tool calls in the response
        json_pattern = r"```json\s*(\{[^`]+\})\s*```"
        matches = re.findall(json_pattern, response, re.DOTALL)

        if not matches:
            return response

        # Process each tool call
        results = []
        for match in matches:
            try:
                tool_call = json.loads(match)
                tool_name = tool_call.get("tool_code") or tool_call.get("tool_name")
                args = tool_call.get("args", {})

                if tool_name in ["execute_command", "command_runner"]:
                    command = args.get("command")
                    if command:
                        # Use command runner tool via registry
                        cmd_args = args.copy()
                        # Set default operation if not specified
                        if "operation" not in cmd_args:
                            cmd_args["operation"] = "run_command"
                        if "cwd" not in cmd_args:
                            cmd_args["cwd"] = project_path or "."
                        result = await self.tool_registry.execute_tool(
                            "command_runner", user_id="ai_engine", **cmd_args
                        )
                        if result.success:
                            command = args.get("command", "unknown")
                            results.append(
                                f"**SUCCESS:** Tool Used: command_runner\n**Command Executed:** {command}"
                            )
                        else:
                            results.append(
                                f"**ERROR:** Tool Error: command_runner - {result.error}"
                            )

                elif tool_name == "file_operations":
                    operation = args.get("operation")
                    if operation:
                        # Prepend project_path to relative file paths
                        file_path = args.get("file_path")
                        if file_path and project_path:
                            from pathlib import Path

                            path = Path(file_path)
                            if not path.is_absolute():
                                args["file_path"] = str(Path(project_path) / file_path)

                        # Use file operations tool - pass all args directly
                        result = await self.tool_registry.execute_tool(
                            "file_operations", user_id="ai_engine", **args
                        )
                        if result.success:
                            # File operations are shown via live tool execution
                            # No need to append results here for streaming mode
                            pass
                        else:
                            results.append(f"ERROR: file_operations - {result.error}")

                elif tool_name == "web_search":
                    operation = args.get("operation", "search_web")
                    # Use web search tool via registry
                    result = await self.tool_registry.execute_tool(
                        "web_search", user_id="ai_engine", **args
                    )
                    if result.success:
                        # Format the result based on operation type
                        if operation == "search_web":
                            query = args.get("query", "unknown")
                            search_results = result.data if result.data else []
                            result_text = f"**SUCCESS:** Tool Used: web_search\n**Query:** {query}\n\n**Search Results:**\n"
                            for idx, item in enumerate(search_results[:5], 1):
                                result_text += (
                                    f"\n{idx}. **{item.get('title', 'No title')}**\n"
                                )
                                result_text += (
                                    f"   {item.get('snippet', 'No description')}\n"
                                )
                                result_text += f"   🔗 {item.get('url', 'No URL')}\n"
                            results.append(result_text)

                        elif operation == "fetch_url_content":
                            url = args.get("url", "unknown")
                            content_data = result.data if result.data else {}
                            title = content_data.get("title", "No title")
                            content = content_data.get("content", "No content")
                            content_type = content_data.get("content_type", "text")

                            # Truncate content if too long
                            max_display = 2000
                            if len(content) > max_display:
                                content = (
                                    content[:max_display]
                                    + f"\n\n... (truncated, total length: {len(content)} characters)"
                                )

                            result_text = f"**SUCCESS:** Tool Used: web_search (fetch_url_content)\n"
                            result_text += f"**URL:** {url}\n"
                            result_text += f"**Title:** {title}\n"
                            result_text += f"**Content Type:** {content_type}\n\n"
                            result_text += f"**Content:**\n{content}"
                            results.append(result_text)

                        elif operation == "parse_documentation":
                            url = args.get("url", "unknown")
                            doc_data = result.data if result.data else {}
                            result_text = f"**SUCCESS:** Tool Used: web_search (parse_documentation)\n"
                            result_text += f"**URL:** {url}\n"
                            result_text += (
                                f"**Title:** {doc_data.get('title', 'No title')}\n"
                            )
                            result_text += (
                                f"**Type:** {doc_data.get('doc_type', 'unknown')}\n\n"
                            )

                            sections = doc_data.get("sections", [])
                            if sections:
                                result_text += "**Sections:**\n"
                                for section in sections[:5]:
                                    result_text += (
                                        f"\n• {section.get('title', 'Untitled')}\n"
                                    )
                            results.append(result_text)

                        elif operation == "get_api_docs":
                            api_name = args.get("api_name", "unknown")
                            api_data = result.data if result.data else {}
                            if api_data.get("found", True):
                                result_text = f"**SUCCESS:** Tool Used: web_search (get_api_docs)\n"
                                result_text += f"**API:** {api_name}\n"
                                result_text += f"**Title:** {api_data.get('title', 'API Documentation')}\n"
                                results.append(result_text)
                            else:
                                result_text = f"**WARNING:** Tool Used: web_search (get_api_docs)\n"
                                result_text += f"**API:** {api_name}\n"
                                result_text += f"**ERROR:** {api_data.get('message', 'Documentation not found')}\n"
                                results.append(result_text)
                        else:
                            results.append(
                                f"**SUCCESS:** Tool Used: web_search ({operation})"
                            )
                    else:
                        results.append(
                            f"**ERROR:** Tool Error: web_search - {result.error}"
                        )

            except Exception as e:
                results.append(f"**Tool Error:** {str(e)}")

        # Replace the original response with just the tool results if tools were used
        if results:
            # Remove JSON tool calls from the response
            import re

            # Remove JSON code blocks - more aggressive pattern
            response = re.sub(r"```json.*?```", "", response, flags=re.DOTALL)
            # Remove any remaining code blocks
            response = re.sub(r"```.*?```", "", response, flags=re.DOTALL)
            # Remove leftover JSON-like patterns
            response = re.sub(r'\{[\s\S]*?"tool_code"[\s\S]*?\}', "", response)
            # Clean up extra whitespace
            response = re.sub(r"\n\s*\n\s*\n+", "\n\n", response)
            response = response.strip()

            # If response is mostly empty after removing code blocks, just show tool results
            if len(response.strip()) < 100:
                return "\n\n".join(results)
            else:
                return response + "\n\n" + "\n\n".join(results)

        return response

    async def build_project(
        self,
        description: str,
        language: str = None,
        framework: str = None,
        output_dir: str = None,
        interactive: bool = False,
    ) -> Dict[str, Any]:
        """Build a project based on description"""

        prompt = f"""Build a {language or "appropriate"} project with the following description:
{description}

Requirements:
- Framework: {framework or "most suitable"}
- Output directory: {output_dir or "current directory"}
- Interactive mode: {interactive}

Please create a complete, working project structure with:
1. Main application files
2. Configuration files
3. Dependencies/requirements
4. README with setup instructions
5. Basic tests if applicable

Provide step-by-step implementation."""

        response = await self.process_message(prompt)

        return {
            "status": "completed",
            "description": description,
            "output_path": output_dir or ".",
            "response": response,
        }

    async def analyze_project(
        self,
        project_path: str,
        output_format: str = "text",
        focus: str = None,
        include_suggestions: bool = False,
    ) -> Any:
        """Analyze a project and provide insights"""

        project_path = Path(project_path)

        # Gather project information
        project_info = self._gather_project_info(project_path)

        prompt = f"""Analyze the following project:

Path: {project_path}
Structure: {project_info["structure"]}
Languages: {project_info["languages"]}
Files: {len(project_info["files"])} files

Focus area: {focus or "general analysis"}
Include suggestions: {include_suggestions}
Output format: {output_format}

Provide a comprehensive analysis including:
1. Project overview and architecture
2. Code quality assessment
3. Dependencies and security
4. Performance considerations
5. Best practices compliance
"""

        if include_suggestions:
            prompt += "\n6. Specific improvement suggestions"

        response = await self.process_message(prompt, project_path=str(project_path))

        if output_format == "json":
            # Try to structure the response as JSON
            try:
                return {
                    "project_path": str(project_path),
                    "analysis": response,
                    "metadata": project_info,
                    "timestamp": str(asyncio.get_event_loop().time()),
                }
            except Exception:
                return {"analysis": response, "error": "Could not structure as JSON"}

        return response

    def _gather_project_info(self, project_path: Path) -> Dict[str, Any]:
        """Gather basic information about a project"""
        info = {"structure": [], "languages": set(), "files": []}

        try:
            for item in project_path.rglob("*"):
                if item.is_file() and not any(
                    part.startswith(".") for part in item.parts
                ):
                    relative_path = item.relative_to(project_path)
                    info["files"].append(str(relative_path))

                    # Detect language by extension
                    suffix = item.suffix.lower()
                    language_map = {
                        ".py": "Python",
                        ".js": "JavaScript",
                        ".ts": "TypeScript",
                        ".java": "Java",
                        ".cpp": "C++",
                        ".c": "C",
                        ".go": "Go",
                        ".rs": "Rust",
                        ".php": "PHP",
                        ".rb": "Ruby",
                    }

                    if suffix in language_map:
                        info["languages"].add(language_map[suffix])

        except Exception as e:
            info["error"] = str(e)

        info["languages"] = list(info["languages"])
        return info
