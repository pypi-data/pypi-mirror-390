"""
Shell Skill

Provides shell command execution capabilities with configurable restrictions.
"""
from typing import Dict, Any, List
from .base import SkillDefinition, SkillType, SkillCategory, SkillVariant
from .registry import register_skill


class ShellSkill(SkillDefinition):
    """Shell command execution skill"""

    @property
    def type(self) -> SkillType:
        return SkillType.SHELL

    @property
    def name(self) -> str:
        return "Shell"

    @property
    def description(self) -> str:
        return "Execute shell commands on the local system with configurable restrictions"

    @property
    def icon(self) -> str:
        return "Terminal"

    def get_variants(self) -> List[SkillVariant]:
        return [
            SkillVariant(
                id="shell_safe_commands",
                name="Shell - Safe Commands",
                description="Execute read-only shell commands on the local system (ls, cat, grep, ps)",
                category=SkillCategory.COMMON,
                badge="Safe",
                icon="Terminal",
                configuration={
                    "allowed_commands": ["ls", "cat", "grep", "find", "ps", "top", "pwd", "echo", "head", "tail"],
                    "timeout": 30,
                },
                is_default=True,
            ),
            SkillVariant(
                id="shell_full_access",
                name="Shell - Full Access",
                description="Unrestricted shell access to execute any command on local system",
                category=SkillCategory.ADVANCED,
                badge="Advanced",
                icon="Terminal",
                configuration={
                    "timeout": 300,
                },
                is_default=False,
            ),
            SkillVariant(
                id="shell_read_only",
                name="Shell - Read Only",
                description="Maximum security: only non-destructive read commands allowed",
                category=SkillCategory.SECURITY,
                badge="Secure",
                icon="ShieldCheck",
                configuration={
                    "allowed_commands": ["ls", "cat", "head", "tail", "grep", "find", "pwd"],
                    "blocked_commands": ["rm", "mv", "cp", "chmod", "chown", "kill"],
                    "timeout": 15,
                },
                is_default=False,
            ),
        ]

    def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate shell configuration"""
        validated = {
            "timeout": min(config.get("timeout", 30), 600),  # Max 10 minutes
        }

        # Add allowed_commands if specified
        if "allowed_commands" in config:
            validated["allowed_commands"] = list(config["allowed_commands"])

        # Add blocked_commands if specified
        if "blocked_commands" in config:
            validated["blocked_commands"] = list(config["blocked_commands"])

        # Add working_directory if specified
        if "working_directory" in config:
            validated["working_directory"] = str(config["working_directory"])

        return validated

    def get_default_configuration(self) -> Dict[str, Any]:
        """Default: safe commands only"""
        return {
            "allowed_commands": ["ls", "cat", "grep", "find", "ps", "top", "pwd", "echo", "head", "tail"],
            "timeout": 30,
        }


# Auto-register this skill
register_skill(ShellSkill())
