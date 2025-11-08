"""
AI Engine for multi-provider AI interactions
"""

import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import json
from pathlib import Path

from .config import ConfigManager
from .tools import ToolRegistry
from .provider_endpoints import GenericAPIClient, get_all_providers, get_provider_config


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
            return response.text
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
                if chunk.text:
                    yield chunk.text
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
            from llama_cpp import Llama
            import os

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
                f"✅ GGUF model loaded successfully on {self.device} ({n_threads} threads)"
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
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

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

            print(f"✅ Model loaded successfully on {self.device}")

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

        # Generate response and process with tools
        response = await ai_provider.generate_response(
            messages=messages,
            model=model,
            max_tokens=max_tokens or 16384,  # Use large default if None
            temperature=config.get("temperature", 0.7),
        )

        # Process response with tools
        async for chunk in self._process_response_with_tools(
            response, project_path, messages, ai_provider, model, config
        ):
            yield chunk

    def _parse_alternative_tool_calls(self, response: str):
        """Parse tool calls from alternative formats (e.g., GPT-OSS with special tokens)"""
        import re
        import json

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
        import re
        import json

        # Limit recursion to prevent infinite loops
        MAX_RECURSION_DEPTH = 5  # Increased from 2 to allow more continuation
        if recursion_depth >= MAX_RECURSION_DEPTH:
            # Silently stop recursion without warning
            yield response
            yield "\n\n⚠️ **Maximum continuation depth reached. Please continue manually if needed.**\n"
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

        # Process all tool calls first, collect results
        tool_results = []
        should_end_response = False

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
                        tool_results.append(
                            {
                                "type": "control",
                                "display": f"\n✅ **Response Completed**\n",
                            }
                        )
                    continue

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
                        output = (
                            result.data.get("stdout", "")
                            if isinstance(result.data, dict)
                            else str(result.data)
                        )
                        tool_results.append(
                            {
                                "type": "command",
                                "command": command,
                                "output": output,
                                "display": f"\n✅ **Tool Used:** command_runner\n⚡ **Command:** {command}\n📄 **Output:**\n```\n{output}\n```\n",
                            }
                        )
                    else:
                        tool_results.append(
                            {
                                "type": "error",
                                "display": f"\n❌ **Command Error:** {result.error}\n",
                            }
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

                            tool_results.append(
                                {
                                    "type": "file_read",
                                    "file_path": file_path,
                                    "content": content,  # Full content for AI processing
                                    "display": f"\n✅ **Tool Used:** file_operations\n📄 **Operation:** {operation} on {file_path}{line_info}\n📄 **Result:**\n```\n{display_content}\n```\n",
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
                            tool_results.append(
                                {
                                    "type": "file_op",
                                    "display": f"\n✅ **Tool Used:** file_operations\n📄 **Operation:** {operation} on {file_path}{line_info}\n",
                                }
                            )
                        else:
                            tool_results.append(
                                {
                                    "type": "file_op",
                                    "display": f"\n✅ **Tool Used:** file_operations\n📄 **Operation:** {operation} on {file_path}\n",
                                }
                            )
                    else:
                        tool_results.append(
                            {
                                "type": "error",
                                "display": f"\n❌ **File Error:** {result.error}\n",
                            }
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
                            result_text = f"\n✅ **Tool Used:** web_search\n🔍 **Query:** {query}\n\n**Search Results:**\n"
                            for idx, item in enumerate(search_results[:5], 1):
                                result_text += (
                                    f"\n{idx}. **{item.get('title', 'No title')}**\n"
                                )
                                result_text += (
                                    f"   {item.get('snippet', 'No description')}\n"
                                )
                                result_text += f"   🔗 {item.get('url', 'No URL')}\n"

                            tool_results.append(
                                {
                                    "type": "web_search",
                                    "query": query,
                                    "results": search_results,
                                    "display": result_text,
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

                            result_text = (
                                f"\n✅ **Tool Used:** web_search (fetch_url_content)\n"
                            )
                            result_text += f"🌐 **URL:** {url}\n"
                            result_text += f"📄 **Title:** {title}\n"
                            result_text += f"📝 **Content Type:** {content_type}\n\n"
                            result_text += (
                                f"**Content:**\n```\n{display_content}\n```\n"
                            )

                            tool_results.append(
                                {
                                    "type": "web_fetch",
                                    "url": url,
                                    "content": content,  # Full content for AI processing
                                    "display": result_text,
                                }
                            )

                        elif operation == "parse_documentation":
                            url = args.get("url", "unknown")
                            doc_data = result.data if result.data else {}
                            result_text = f"\n✅ **Tool Used:** web_search (parse_documentation)\n"
                            result_text += f"🌐 **URL:** {url}\n"
                            result_text += (
                                f"📄 **Title:** {doc_data.get('title', 'No title')}\n"
                            )
                            result_text += f"📚 **Type:** {doc_data.get('doc_type', 'unknown')}\n\n"

                            sections = doc_data.get("sections", [])
                            if sections:
                                result_text += "**Sections:**\n"
                                for section in sections[:5]:
                                    result_text += (
                                        f"\n• {section.get('title', 'Untitled')}\n"
                                    )

                            tool_results.append(
                                {
                                    "type": "web_docs",
                                    "url": url,
                                    "doc_data": doc_data,
                                    "display": result_text,
                                }
                            )

                        elif operation == "get_api_docs":
                            api_name = args.get("api_name", "unknown")
                            api_data = result.data if result.data else {}
                            if api_data.get("found", True):
                                result_text = (
                                    f"\n✅ **Tool Used:** web_search (get_api_docs)\n"
                                )
                                result_text += f"📚 **API:** {api_name}\n"
                                result_text += f"📄 **Title:** {api_data.get('title', 'API Documentation')}\n"
                            else:
                                result_text = (
                                    f"\n⚠️ **Tool Used:** web_search (get_api_docs)\n"
                                )
                                result_text += f"📚 **API:** {api_name}\n"
                                result_text += f"❌ {api_data.get('message', 'Documentation not found')}\n"

                            tool_results.append(
                                {
                                    "type": "web_api_docs",
                                    "api_name": api_name,
                                    "api_data": api_data,
                                    "display": result_text,
                                }
                            )
                        else:
                            tool_results.append(
                                {
                                    "type": "web_search",
                                    "display": f"\n✅ **Tool Used:** web_search ({operation})\n",
                                }
                            )
                    else:
                        tool_results.append(
                            {
                                "type": "error",
                                "display": f"\n❌ **Web Search Error:** {result.error}\n",
                            }
                        )

            except json.JSONDecodeError as e:
                tool_results.append(
                    {
                        "type": "error",
                        "display": f"\n❌ **JSON Parse Error:** {str(e)}\n",
                    }
                )
            except Exception as e:
                tool_results.append(
                    {"type": "error", "display": f"\n❌ **Tool Error:** {str(e)}\n"}
                )

        # Now yield the response with tool results integrated
        if tool_results:
            # Show the initial part of the response (before first tool call)
            first_tool_pos = response.find("```json")
            if first_tool_pos > 0:
                yield response[:first_tool_pos]

            # Show all tool results
            for tool_result in tool_results:
                yield tool_result["display"]

            # Check if we should end the response (end_response tool was called)
            if should_end_response:
                return

            # Always generate a continuation response after tool execution
            # This ensures the AI completes its thought after executing tools
            needs_continuation = True

            if needs_continuation and recursion_depth < MAX_RECURSION_DEPTH:
                # Generate a final response that incorporates all tool results
                tool_context = ""
                has_file_read = False
                has_file_write = False
                has_web_search = False

                for tool_result in tool_results:
                    if tool_result["type"] == "command":
                        tool_context += f"Command '{tool_result['command']}' output: {tool_result['output']}\n"
                    elif tool_result["type"] == "file_read":
                        has_file_read = True
                        tool_context += f"File '{tool_result['file_path']}' contains: {tool_result['content']}\n"
                    elif tool_result["type"] == "file_op":
                        has_file_write = True
                        tool_context += f"File operation completed successfully\n"
                    elif tool_result["type"] == "web_search":
                        has_web_search = True
                        results = tool_result.get("results", [])
                        tool_context += f"Web search for '{tool_result.get('query', 'unknown')}' returned {len(results)} results\n"
                    elif tool_result["type"] == "web_fetch":
                        has_web_search = True
                        tool_context += f"Fetched content from '{tool_result.get('url', 'unknown')}': {tool_result.get('content', '')}\n"
                    elif tool_result["type"] == "web_docs":
                        has_web_search = True
                        doc_data = tool_result.get("doc_data", {})
                        tool_context += f"Documentation from '{tool_result.get('url', 'unknown')}': {doc_data.get('content', '')}\n"
                    elif tool_result["type"] == "web_api_docs":
                        has_web_search = True
                        api_data = tool_result.get("api_data", {})
                        tool_context += f"API documentation for '{tool_result.get('api_name', 'unknown')}': {api_data.get('content', '')}\n"

                # Build continuation prompt based on what tools were executed
                if has_web_search:
                    # For web search results, provide context and ask AI to continue
                    final_prompt = f"""Based on the web search/fetch results below, complete the user's request.

Tool Results:
{tool_context}

Now:
- Summarize the key information from the results
- Answer the user's question based on the fetched content
- If implementing something, use the information to create accurate code
- Provide any additional context or recommendations

When COMPLETELY DONE, call the end_response tool.

Complete the request:"""
                elif has_file_read:
                    # For file reads, allow the AI to continue with modifications if needed
                    final_prompt = f"""Based on the file content below, complete the user's request.

Tool Results:
{tool_context}

If the user asked you to MODIFY/ADD features to the file:
- Use write_file_lines to modify ONLY the specific sections that need changes
- DO NOT use write_file with the entire file content - it will FAIL for large files
- Make the changes in small, targeted sections

If the user only asked to READ/ANALYZE, provide your analysis.

When COMPLETELY DONE, call the end_response tool.

Complete the request:"""
                elif has_file_write:
                    # For file writes/creates, continue if there's more work
                    final_prompt = f"""The tool operations have been completed.

Tool Results:
{tool_context}

If there are MORE files to modify or MORE changes needed to complete the user's request:
- Continue with the remaining modifications
- Use write_file_lines for targeted changes

If EVERYTHING is complete:
- Provide a brief summary
- Call the end_response tool

Continue:"""
                else:
                    # For commands or other operations
                    final_prompt = f"""Based on the tool execution results below, continue your response to the user.

Tool Results:
{tool_context}

Complete any remaining work, then call end_response when done.

Continue your response:"""

                final_messages = messages + [
                    {"role": "assistant", "content": "I'll continue with the results."},
                    {"role": "user", "content": final_prompt},
                ]

                # Use appropriate tokens for continuation
                # Use unlimited tokens to ensure completion
                max_tokens = config.get("max_tokens", None)
                if max_tokens == 0 or max_tokens == -1:
                    max_tokens = None
                continuation_max_tokens = max_tokens or 16384

                final_response = await ai_provider.generate_response(
                    messages=final_messages,
                    model=model,
                    max_tokens=continuation_max_tokens,
                    temperature=config.get("temperature", 0.7),
                )

                # For file write continuations, strip out any tool calls to prevent loops
                if has_file_write and self._contains_tool_calls(final_response):
                    # Remove tool calls from the response
                    import re

                    json_pattern = r"```json\s*\n.*?\n```"
                    cleaned_response = re.sub(
                        json_pattern, "", final_response, flags=re.DOTALL
                    )
                    yield f"\n{cleaned_response.strip()}"
                elif self._contains_tool_calls(final_response):
                    # For other cases, allow recursive processing but with depth limit
                    async for chunk in self._process_response_with_tools(
                        final_response,
                        project_path,
                        final_messages,
                        ai_provider,
                        model,
                        config,
                        recursion_depth + 1,
                    ):
                        yield chunk
                else:
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
                        yield f"\n✅ **Tool Used:** command_runner\n⚡ **Command:** {command}\n📄 **Output:**\n```\n{output}\n```\n"
                    else:
                        yield f"\n❌ **Command Error:** {result.error}\n"

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
                            yield f"\n✅ **Tool Used:** file_operations\n📄 **Operation:** {operation} on {file_path}\n📄 **Result:**\n```\n{content}\n```\n"
                        else:
                            yield f"\n✅ **Tool Used:** file_operations\n📄 **Operation:** {operation} on {file_path}\n"
                    else:
                        yield f"\n❌ **File Error:** {result.error}\n"

            except json.JSONDecodeError as e:
                yield f"\n❌ **JSON Parse Error:** {str(e)}\n"
            except Exception as e:
                yield f"\n❌ **Tool Error:** {str(e)}\n"

    def _build_system_prompt(self, project_path: str = None) -> str:
        """Build system prompt for the AI"""
        
        # Load user-defined rules FIRST (highest priority)
        from .rules import RulesManager
        rules_manager = RulesManager()
        rules_text = rules_manager.get_rules_for_ai(project_path)
        
        prompt = ""
        
        # Add rules at the very beginning if they exist
        if rules_text:
            prompt += "="*80 + "\n"
            prompt += "USER-DEFINED RULES (HIGHEST PRIORITY - MUST FOLLOW ABOVE ALL ELSE):\n"
            prompt += "="*80 + "\n"
            prompt += rules_text + "\n"
            prompt += "="*80 + "\n"
            prompt += "These rules OVERRIDE all other instructions. Follow them strictly.\n"
            prompt += "="*80 + "\n\n"
        
        prompt += """You are Cognautic, an advanced AI coding assistant running inside the Cognautic CLI.

IMPORTANT: You are operating within the Cognautic CLI environment. You can ONLY use the tools provided below. Do NOT suggest using external tools, IDEs, or commands that are not available in this CLI.

Most Important Instruction:
Before starting any project, always perform a web search about the project or topic you’re working on.

:Documentation Requirement:

Collect the key findings and relevant information.

Create one or more Markdown (.md) files summarizing your research.

Store these files inside an MD folder in the current project directory.

These information files will serve as background documentation to guide project development.

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
- ALWAYS USE end_response TOOL: When you have completed ALL tasks, ALWAYS call the end_response tool to prevent unnecessary continuation
- NEVER RE-READ SAME FILE: If a file was truncated in the output, use read_file_lines to read the specific truncated section, DO NOT re-read the entire file

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

For commands (always explore first):

```json
{
  "tool_code": "command_runner",
  "args": {
    "command": "ls -la"
  }
}
```

```json
{
  "tool_code": "command_runner",
  "args": {
    "command": "pwd"
  }
}
```

For web search (when you need external information):

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
- file_operations: Create, read, write, delete files and directories
- command_runner: Execute shell commands
- web_search: Search the web for information
- code_analysis: Analyze code files
- response_control: Control response continuation (use end_response to stop auto-continuation)

RESPONSE CONTINUATION (CRITICAL - ALWAYS USE end_response):
- By default, after executing tools, the AI will automatically continue to complete the task
- YOU MUST ALWAYS use the response_control tool when you finish ALL work:
```json
{
  "tool_code": "response_control",
  "args": {
    "operation": "end_response"
  }
}
```
- WHEN TO USE end_response (ALWAYS use it in these cases):
  * After creating/modifying ALL requested files
  * After completing ALL steps of a multi-step task
  * After providing final explanation or summary
  * Basically: ALWAYS use it when you're done with everything
- Do NOT use end_response ONLY if:
  * The task is incomplete
  * You're waiting for user input
  * You need to execute more tools
- IMPORTANT: Forgetting to use end_response causes the user to manually type "continue" - ALWAYS use it!

REMEMBER:
1. Use tools to actually perform actions, don't just provide code examples!
2. Complete ENTIRE requests in ONE response - create all necessary files and functionality!
3. Don't stop after one file - build complete, functional projects!
4. NEVER promise to do something without including the tool calls to actually do it!
5. For very long file content, the system will automatically handle it - just provide the full content
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
        import re
        import json

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
                                f"✅ **Tool Used:** command_runner\n⚡ **Command Executed:** {command}"
                            )
                        else:
                            results.append(
                                f"❌ **Tool Error:** command_runner - {result.error}"
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
                            # Format file operation results concisely
                            if operation == "create_file":
                                file_path = args.get("file_path", "unknown")
                                results.append(
                                    f"✅ **Tool Used:** file_operations\n📄 **File Created:** {file_path}"
                                )
                            elif operation == "write_file":
                                file_path = args.get("file_path", "unknown")
                                results.append(
                                    f"✅ **Tool Used:** file_operations\n📝 **File Edited:** {file_path}"
                                )
                            elif operation == "list_directory":
                                dir_path = args.get("dir_path", "unknown")
                                file_count = (
                                    len(result.data)
                                    if isinstance(result.data, list)
                                    else 0
                                )
                                results.append(
                                    f"✅ **Tool Used:** file_operations\n📁 **Directory Listed:** {dir_path} ({file_count} items)"
                                )
                            else:
                                results.append(
                                    f"✅ **Tool Used:** file_operations ({operation})"
                                )
                        else:
                            results.append(
                                f"❌ **Tool Error:** file_operations - {result.error}"
                            )

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
                            result_text = f"✅ **Tool Used:** web_search\n🔍 **Query:** {query}\n\n**Search Results:**\n"
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

                            result_text = (
                                f"✅ **Tool Used:** web_search (fetch_url_content)\n"
                            )
                            result_text += f"🌐 **URL:** {url}\n"
                            result_text += f"📄 **Title:** {title}\n"
                            result_text += f"📝 **Content Type:** {content_type}\n\n"
                            result_text += f"**Content:**\n{content}"
                            results.append(result_text)

                        elif operation == "parse_documentation":
                            url = args.get("url", "unknown")
                            doc_data = result.data if result.data else {}
                            result_text = (
                                f"✅ **Tool Used:** web_search (parse_documentation)\n"
                            )
                            result_text += f"🌐 **URL:** {url}\n"
                            result_text += (
                                f"📄 **Title:** {doc_data.get('title', 'No title')}\n"
                            )
                            result_text += f"📚 **Type:** {doc_data.get('doc_type', 'unknown')}\n\n"

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
                                result_text = (
                                    f"✅ **Tool Used:** web_search (get_api_docs)\n"
                                )
                                result_text += f"📚 **API:** {api_name}\n"
                                result_text += f"📄 **Title:** {api_data.get('title', 'API Documentation')}\n"
                                results.append(result_text)
                            else:
                                result_text = (
                                    f"⚠️ **Tool Used:** web_search (get_api_docs)\n"
                                )
                                result_text += f"📚 **API:** {api_name}\n"
                                result_text += f"❌ {api_data.get('message', 'Documentation not found')}\n"
                                results.append(result_text)
                        else:
                            results.append(
                                f"✅ **Tool Used:** web_search ({operation})"
                            )
                    else:
                        results.append(
                            f"❌ **Tool Error:** web_search - {result.error}"
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
