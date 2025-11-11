"""
LiteLLM Service

This service provides a wrapper around LiteLLM for agent execution.
"""

import os
from typing import Dict, List, Optional, Any
import litellm
from litellm import completion
import logging

from control_plane_api.app.config import settings

logger = logging.getLogger(__name__)


class LiteLLMService:
    """Service for interacting with LiteLLM"""

    def __init__(self):
        """Initialize LiteLLM service with configuration"""
        # Set LiteLLM configuration
        if settings.litellm_api_key:
            os.environ["LITELLM_API_KEY"] = settings.litellm_api_key
        litellm.api_base = settings.litellm_api_base
        litellm.drop_params = True  # Drop unsupported params instead of failing

        # Configure timeout
        litellm.request_timeout = settings.litellm_timeout

        logger.info(f"LiteLLM Service initialized with base URL: {settings.litellm_api_base}")


    def execute_agent(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute an agent with LiteLLM

        Args:
            prompt: The user prompt
            model: Model identifier (defaults to configured default)
            system_prompt: System prompt for the agent
            temperature: Temperature for response generation
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            **kwargs: Additional parameters to pass to LiteLLM

        Returns:
            Dict containing the response and metadata
        """
        try:
            # Use default model if not specified
            if not model:
                model = settings.litellm_default_model

            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Prepare completion parameters
            # For custom proxies, use openai/ prefix to force OpenAI-compatible mode
            # This tells LiteLLM to use the base_url as an OpenAI-compatible endpoint
            completion_params = {
                "model": f"openai/{model}",  # Use openai/ prefix for custom proxy
                "messages": messages,
                "temperature": temperature,
                "api_key": settings.litellm_api_key or "dummy-key",  # Fallback for when key is not set
                "base_url": settings.litellm_api_base,
            }

            if max_tokens:
                completion_params["max_tokens"] = max_tokens
            if top_p:
                completion_params["top_p"] = top_p

            # Add any additional kwargs
            completion_params.update(kwargs)

            logger.info(f"Executing agent with model: {model} (using openai/{model})")

            # Make the completion request
            response = completion(**completion_params)

            # Extract response content
            result = {
                "success": True,
                "response": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
            }

            logger.info(f"Agent execution successful. Tokens used: {result['usage']['total_tokens']}")
            return result

        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model": model or settings.litellm_default_model,
            }

    def execute_agent_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        **kwargs: Any,
    ):
        """
        Execute an agent with streaming response

        Args:
            prompt: The user prompt
            model: Model identifier (defaults to configured default)
            system_prompt: System prompt for the agent
            temperature: Temperature for response generation
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            **kwargs: Additional parameters to pass to LiteLLM

        Yields:
            Response chunks as they arrive
        """
        try:
            # Use default model if not specified
            if not model:
                model = settings.litellm_default_model

            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Prepare completion parameters
            # For custom proxies, use openai/ prefix to force OpenAI-compatible mode
            # This tells LiteLLM to use the base_url as an OpenAI-compatible endpoint
            completion_params = {
                "model": f"openai/{model}",  # Use openai/ prefix for custom proxy
                "messages": messages,
                "temperature": temperature,
                "stream": True,
                "api_key": settings.litellm_api_key or "dummy-key",  # Fallback for when key is not set
                "base_url": settings.litellm_api_base,
            }

            if max_tokens:
                completion_params["max_tokens"] = max_tokens
            if top_p:
                completion_params["top_p"] = top_p

            # Add any additional kwargs
            completion_params.update(kwargs)

            logger.info(f"Executing agent (streaming) with model: {model} (using openai/{model})")

            # Make the streaming completion request
            response = completion(**completion_params)

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error executing agent (streaming): {str(e)}")
            yield f"Error: {str(e)}"


# Singleton instance
litellm_service = LiteLLMService()
