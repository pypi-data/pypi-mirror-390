"""
Skills Module

This module manages all available skills (OS-level capabilities) that can be
assigned to agents and teams. Each skill corresponds to a capability that agents
can use during execution (file system, shell, Docker, Python, etc.).

Skills are defined as Python classes that provide:
- Metadata (name, description, icon)
- Default configuration
- Validation logic
- Instantiation logic for the underlying framework
"""

from .base import SkillDefinition, SkillType, SkillCategory, SkillRequirements, SkillVariant
from .registry import skill_registry, get_skill, get_all_skills, register_skill

# Import all skill definitions to auto-register them
from .file_system import FileSystemSkill
from .shell import ShellSkill
from .docker import DockerSkill
from .python import PythonSkill
from .file_generation import FileGenerationSkill
from .data_visualization import DataVisualizationSkill
from .workflow_executor import WorkflowExecutorSkill

__all__ = [
    "SkillDefinition",
    "SkillType",
    "SkillCategory",
    "SkillRequirements",
    "SkillVariant",
    "skill_registry",
    "get_skill",
    "get_all_skills",
    "register_skill",
    "FileSystemSkill",
    "ShellSkill",
    "DockerSkill",
    "PythonSkill",
    "FileGenerationSkill",
    "DataVisualizationSkill",
    "WorkflowExecutorSkill",
]
