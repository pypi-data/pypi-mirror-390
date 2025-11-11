"""
Runtime validation logic shared between API and worker.

This module provides validation without depending on worker-specific types,
making it safe to import from both the API layer and worker layer.
"""

from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass
import re


@dataclass
class ModelRequirement:
    """Model requirement specification for a runtime."""

    # Patterns that model IDs must match (any match is valid)
    model_id_patterns: List[str]

    # Model providers that are supported (e.g., "anthropic", "openai")
    supported_providers: Set[str]

    # Specific model families supported (e.g., "claude", "gpt")
    supported_families: Set[str]

    # Human-readable description
    description: str = ""

    # Examples of valid model IDs
    examples: List[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []

    def validate(self, model_id: Optional[str]) -> tuple[bool, Optional[str]]:
        """
        Validate a model ID against this requirement.

        Args:
            model_id: Model ID to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not model_id:
            return False, "Model ID is required for this runtime"

        # Check pattern matching
        for pattern in self.model_id_patterns:
            if re.search(pattern, model_id, re.IGNORECASE):
                return True, None

        # Check provider/family
        model_lower = model_id.lower()

        # Check if any supported family is in the model ID
        for family in self.supported_families:
            if family.lower() in model_lower:
                return True, None

        # Provide helpful error message
        examples_str = ", ".join(self.examples) if self.examples else "N/A"
        return False, (
            f"Model '{model_id}' is not compatible with this runtime. "
            f"Expected models matching: {', '.join(self.model_id_patterns)}. "
            f"Supported families: {', '.join(self.supported_families)}. "
            f"Examples: {examples_str}"
        )


@dataclass
class RuntimeRequirements:
    """Requirements specification for a runtime."""

    runtime_type: str

    # Model requirements
    model_requirement: ModelRequirement

    # Required fields in agent/team config
    required_config_fields: List[str] = None

    # Optional but recommended fields
    recommended_config_fields: List[str] = None

    # Maximum conversation history length
    max_history_length: Optional[int] = None

    # Whether system prompt is required
    requires_system_prompt: bool = False

    # Whether tools/skills are required
    requires_tools: bool = False

    def __post_init__(self):
        if self.required_config_fields is None:
            self.required_config_fields = []
        if self.recommended_config_fields is None:
            self.recommended_config_fields = []

    def validate_model(self, model_id: Optional[str]) -> tuple[bool, Optional[str]]:
        """Validate model compatibility."""
        return self.model_requirement.validate(model_id)

    def validate_config(self, config: Optional[Dict[str, Any]]) -> List[str]:
        """
        Validate agent/team configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not config:
            if self.required_config_fields:
                errors.append(
                    f"Configuration is required for this runtime. "
                    f"Required fields: {', '.join(self.required_config_fields)}"
                )
            return errors

        # Check required fields
        for field in self.required_config_fields:
            if field not in config or config[field] is None:
                errors.append(f"Required field '{field}' is missing in configuration")

        return errors


# ==================== Runtime Requirements Definitions ====================

# Agno/Default Runtime - Flexible, supports most models
DEFAULT_RUNTIME_REQUIREMENTS = RuntimeRequirements(
    runtime_type="default",
    model_requirement=ModelRequirement(
        model_id_patterns=[
            r".*",  # Accept all models
        ],
        supported_providers={"openai", "anthropic", "azure", "google", "mistral", "cohere"},
        supported_families={"gpt", "claude", "gemini", "mistral", "command"},
        description="Default runtime supports most LiteLLM-compatible models",
        examples=[
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-sonnet-4",
            "gemini-pro",
            "mistral-large",
        ],
    ),
    max_history_length=100,  # Reasonable default
    requires_system_prompt=False,
    requires_tools=False,
)

# Claude Code Runtime - Requires Claude models
CLAUDE_CODE_RUNTIME_REQUIREMENTS = RuntimeRequirements(
    runtime_type="claude_code",
    model_requirement=ModelRequirement(
        model_id_patterns=[
            r"claude",  # Must contain "claude"
            r"kubiya/claude",  # LiteLLM proxy format
            r"anthropic\.claude",  # Alternative format
        ],
        supported_providers={"anthropic"},
        supported_families={"claude"},
        description=(
            "Claude Code runtime requires Anthropic Claude models. "
            "This runtime leverages Claude's advanced capabilities including "
            "extended context, tool use, and code understanding."
        ),
        examples=[
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
            "claude-sonnet-4",
            "claude-opus-4",
            "kubiya/claude-sonnet-4",
            "kubiya/claude-opus-4",
        ],
    ),
    max_history_length=200,  # Claude handles longer contexts well
    requires_system_prompt=False,  # Optional but recommended
    requires_tools=False,  # Claude Code adds tools automatically
    recommended_config_fields=["timeout", "max_tokens"],
)


# Registry of runtime requirements
RUNTIME_REQUIREMENTS: Dict[str, RuntimeRequirements] = {
    "default": DEFAULT_RUNTIME_REQUIREMENTS,
    "claude_code": CLAUDE_CODE_RUNTIME_REQUIREMENTS,
}


# ==================== Validation Functions ====================

def validate_agent_for_runtime(
    runtime_type: str,
    model_id: Optional[str],
    agent_config: Optional[Dict[str, Any]] = None,
    system_prompt: Optional[str] = None,
) -> tuple[bool, List[str]]:
    """
    Validate agent configuration for a runtime.

    Args:
        runtime_type: Runtime type string (e.g., "default", "claude_code")
        model_id: Model ID to validate
        agent_config: Agent configuration dict
        system_prompt: System prompt

    Returns:
        Tuple of (is_valid, error_messages)
    """
    requirements = RUNTIME_REQUIREMENTS.get(runtime_type)
    if not requirements:
        # No requirements registered - allow by default
        return True, []

    errors = []

    # Validate model
    is_valid, error = requirements.validate_model(model_id)
    if not is_valid:
        errors.append(error)

    # Validate config
    config_errors = requirements.validate_config(agent_config)
    errors.extend(config_errors)

    # Validate system prompt if required
    if requirements.requires_system_prompt and not system_prompt:
        errors.append("System prompt is required for this runtime")

    return len(errors) == 0, errors


def get_runtime_requirements_info(runtime_type: str) -> Dict[str, Any]:
    """
    Get human-readable requirements info for a runtime.

    Args:
        runtime_type: Runtime type string

    Returns:
        Dict with requirements information
    """
    requirements = RUNTIME_REQUIREMENTS.get(runtime_type)
    if not requirements:
        return {
            "runtime_type": runtime_type,
            "model_requirement": "No specific requirements",
            "flexible": True,
        }

    return {
        "runtime_type": runtime_type,
        "model_requirement": {
            "description": requirements.model_requirement.description,
            "supported_providers": list(requirements.model_requirement.supported_providers),
            "supported_families": list(requirements.model_requirement.supported_families),
            "examples": requirements.model_requirement.examples,
        },
        "required_config_fields": requirements.required_config_fields,
        "recommended_config_fields": requirements.recommended_config_fields,
        "max_history_length": requirements.max_history_length,
        "requires_system_prompt": requirements.requires_system_prompt,
        "requires_tools": requirements.requires_tools,
    }


def list_all_runtime_requirements() -> Dict[str, Dict[str, Any]]:
    """
    Get requirements for all registered runtimes.

    Returns:
        Dict mapping runtime type to requirements info
    """
    return {
        runtime_type: get_runtime_requirements_info(runtime_type)
        for runtime_type in RUNTIME_REQUIREMENTS.keys()
    }
