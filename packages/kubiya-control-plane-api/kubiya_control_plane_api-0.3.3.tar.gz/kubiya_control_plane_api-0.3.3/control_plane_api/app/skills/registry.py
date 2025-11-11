"""
Skill Registry

Central registry for all available skills. Skills self-register
when their modules are imported.
"""
from typing import Dict, List, Optional
from .base import SkillDefinition, SkillType
import logging

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry for all available skill definitions"""

    def __init__(self):
        self._skills: Dict[SkillType, SkillDefinition] = {}

    def register(self, skill: SkillDefinition):
        """Register a skill definition"""
        if skill.type in self._skills:
            logger.warning(f"Skill {skill.type} is already registered, overwriting")

        self._skills[skill.type] = skill
        logger.info(f"Registered skill: {skill.type} - {skill.name}")

    def get(self, skill_type: SkillType) -> Optional[SkillDefinition]:
        """Get a skill definition by type"""
        return self._skills.get(skill_type)

    def get_all(self) -> List[SkillDefinition]:
        """Get all registered skills"""
        return list(self._skills.values())

    def get_by_name(self, name: str) -> Optional[SkillDefinition]:
        """Get a skill by name"""
        for skill in self._skills.values():
            if skill.name.lower() == name.lower():
                return skill
        return None

    def list_types(self) -> List[SkillType]:
        """List all registered skill types"""
        return list(self._skills.keys())


# Global registry instance
skill_registry = SkillRegistry()


def register_skill(skill: SkillDefinition):
    """Decorator or function to register a skill"""
    skill_registry.register(skill)
    return skill


def get_skill(skill_type: SkillType) -> Optional[SkillDefinition]:
    """Get a skill definition by type"""
    return skill_registry.get(skill_type)


def get_all_skills() -> List[SkillDefinition]:
    """Get all registered skills"""
    return skill_registry.get_all()
