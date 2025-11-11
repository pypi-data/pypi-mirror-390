"""
Policy Service - Business logic for policy management and enforcement.

This service provides:
- Policy CRUD operations with enforcer service integration
- Policy association management (linking policies to entities)
- Policy inheritance resolution (environment > team > agent)
- Policy evaluation with pre-hook support
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import structlog
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.policy_enforcer_client import (
    PolicyEnforcerClient,
    Policy,
    PolicyCreate,
    PolicyUpdate,
    EvaluationResult,
    PolicyNotFoundError,
    PolicyValidationError,
)

logger = structlog.get_logger()

# Entity types for policy associations
EntityType = Literal["agent", "team", "environment"]

# Priority levels for inheritance
PRIORITY_LEVELS = {
    "environment": 300,
    "team": 200,
    "agent": 100,
}


class PolicyAssociationCreate(BaseModel):
    """Schema for creating a policy association"""
    policy_id: str = Field(..., description="Policy UUID from enforcer service")
    policy_name: str = Field(..., description="Policy name (cached)")
    entity_type: EntityType = Field(..., description="Entity type")
    entity_id: str = Field(..., description="Entity UUID")
    enabled: bool = Field(default=True, description="Whether association is active")
    priority: Optional[int] = Field(None, description="Custom priority (overrides default)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PolicyAssociationUpdate(BaseModel):
    """Schema for updating a policy association"""
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class PolicyAssociationResponse(BaseModel):
    """Response model for policy associations"""
    id: str
    organization_id: str
    policy_id: str
    policy_name: str
    entity_type: str
    entity_id: str
    enabled: bool
    priority: int
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    created_by: Optional[str] = None


class ResolvedPolicy(BaseModel):
    """Policy with inheritance information"""
    policy_id: str
    policy_name: str
    source_type: str  # Where the policy comes from
    source_id: str
    priority: int
    enabled: bool
    metadata: Dict[str, Any]
    policy_details: Optional[Dict[str, Any]] = None  # Full policy from enforcer


class PolicyService:
    """Service for managing policies and their associations"""

    def __init__(self, organization_id: str, enforcer_client: Optional[PolicyEnforcerClient] = None):
        """
        Initialize policy service.

        Args:
            organization_id: Organization ID for multi-tenancy
            enforcer_client: Optional policy enforcer client (if None, policy features disabled)
        """
        self.organization_id = organization_id
        self.enforcer_client = enforcer_client
        self.supabase = get_supabase()

    @property
    def is_enabled(self) -> bool:
        """Check if policy enforcement is enabled"""
        return self.enforcer_client is not None

    # ============================================================================
    # Policy CRUD Operations (Proxy to Enforcer Service)
    # ============================================================================

    async def create_policy(self, policy: PolicyCreate) -> Policy:
        """
        Create a new policy in the enforcer service.

        Args:
            policy: Policy creation data

        Returns:
            Created Policy object

        Raises:
            RuntimeError: If enforcer client is not configured
            PolicyValidationError: If policy is invalid
        """
        if not self.enforcer_client:
            raise RuntimeError("Policy enforcer is not configured")

        logger.info(
            "creating_policy",
            organization_id=self.organization_id,
            policy_name=policy.name,
        )

        return await self.enforcer_client.policies.create(policy)

    async def get_policy(self, policy_id: str) -> Policy:
        """
        Get a policy from the enforcer service.

        Args:
            policy_id: Policy UUID

        Returns:
            Policy object

        Raises:
            PolicyNotFoundError: If policy doesn't exist
        """
        if not self.enforcer_client:
            raise RuntimeError("Policy enforcer is not configured")

        return await self.enforcer_client.policies.get(policy_id)

    async def list_policies(
        self,
        page: int = 1,
        limit: int = 20,
        enabled: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[Policy]:
        """
        List policies from the enforcer service.

        Args:
            page: Page number
            limit: Items per page
            enabled: Filter by enabled status
            search: Search term

        Returns:
            List of policies
        """
        if not self.enforcer_client:
            return []

        response = await self.enforcer_client.policies.list(
            page=page,
            limit=limit,
            enabled=enabled,
            search=search,
        )
        return response.policies

    async def update_policy(self, policy_id: str, update: PolicyUpdate) -> Policy:
        """
        Update a policy in the enforcer service.

        Args:
            policy_id: Policy UUID
            update: Update data

        Returns:
            Updated Policy object
        """
        if not self.enforcer_client:
            raise RuntimeError("Policy enforcer is not configured")

        return await self.enforcer_client.policies.update(policy_id, update)

    async def delete_policy(self, policy_id: str) -> None:
        """
        Delete a policy from the enforcer service and remove all associations.

        Args:
            policy_id: Policy UUID
        """
        if not self.enforcer_client:
            raise RuntimeError("Policy enforcer is not configured")

        # Delete from enforcer service
        await self.enforcer_client.policies.delete(policy_id)

        # Delete all associations
        self.supabase.table("policy_associations").delete().eq(
            "organization_id", self.organization_id
        ).eq("policy_id", policy_id).execute()

        logger.info(
            "policy_deleted_with_associations",
            policy_id=policy_id,
            organization_id=self.organization_id,
        )

    # ============================================================================
    # Policy Association Management
    # ============================================================================

    async def create_association(
        self,
        association: PolicyAssociationCreate,
        created_by: Optional[str] = None,
    ) -> PolicyAssociationResponse:
        """
        Create a policy association (link policy to entity).

        Args:
            association: Association data
            created_by: Email of creator

        Returns:
            Created association

        Raises:
            PolicyNotFoundError: If policy doesn't exist
        """
        if not self.enforcer_client:
            raise RuntimeError("Policy enforcer is not configured")

        # Verify policy exists
        await self.get_policy(association.policy_id)

        # Determine priority (use provided or default based on entity type)
        priority = association.priority or PRIORITY_LEVELS.get(association.entity_type, 100)

        # Create association
        data = {
            "organization_id": self.organization_id,
            "policy_id": association.policy_id,
            "policy_name": association.policy_name,
            "entity_type": association.entity_type,
            "entity_id": association.entity_id,
            "enabled": association.enabled,
            "priority": priority,
            "metadata": association.metadata,
            "created_by": created_by,
        }

        result = self.supabase.table("policy_associations").insert(data).execute()

        logger.info(
            "policy_association_created",
            policy_id=association.policy_id,
            entity_type=association.entity_type,
            entity_id=association.entity_id[:8],
        )

        return PolicyAssociationResponse(**result.data[0])

    def get_association(self, association_id: str) -> Optional[PolicyAssociationResponse]:
        """Get a policy association by ID"""
        result = (
            self.supabase.table("policy_associations")
            .select("*")
            .eq("organization_id", self.organization_id)
            .eq("id", association_id)
            .execute()
        )

        if result.data:
            return PolicyAssociationResponse(**result.data[0])
        return None

    def list_associations(
        self,
        entity_type: Optional[EntityType] = None,
        entity_id: Optional[str] = None,
        policy_id: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> List[PolicyAssociationResponse]:
        """
        List policy associations with filtering.

        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            policy_id: Filter by policy ID
            enabled: Filter by enabled status

        Returns:
            List of associations
        """
        query = (
            self.supabase.table("policy_associations")
            .select("*")
            .eq("organization_id", self.organization_id)
        )

        if entity_type:
            query = query.eq("entity_type", entity_type)
        if entity_id:
            query = query.eq("entity_id", entity_id)
        if policy_id:
            query = query.eq("policy_id", policy_id)
        if enabled is not None:
            query = query.eq("enabled", enabled)

        result = query.order("priority", desc=True).execute()

        return [PolicyAssociationResponse(**item) for item in result.data]

    def update_association(
        self,
        association_id: str,
        update: PolicyAssociationUpdate,
    ) -> Optional[PolicyAssociationResponse]:
        """Update a policy association"""
        data = update.dict(exclude_none=True)

        result = (
            self.supabase.table("policy_associations")
            .update(data)
            .eq("organization_id", self.organization_id)
            .eq("id", association_id)
            .execute()
        )

        if result.data:
            logger.info("policy_association_updated", association_id=association_id)
            return PolicyAssociationResponse(**result.data[0])
        return None

    def delete_association(self, association_id: str) -> bool:
        """Delete a policy association"""
        result = (
            self.supabase.table("policy_associations")
            .delete()
            .eq("organization_id", self.organization_id)
            .eq("id", association_id)
            .execute()
        )

        if result.data:
            logger.info("policy_association_deleted", association_id=association_id)
            return True
        return False

    # ============================================================================
    # Policy Inheritance Resolution
    # ============================================================================

    async def resolve_entity_policies(
        self,
        entity_type: EntityType,
        entity_id: str,
        include_details: bool = False,
    ) -> List[ResolvedPolicy]:
        """
        Resolve all policies applicable to an entity considering inheritance.

        Inheritance order: environment > team > agent
        Higher priority wins when same policy is defined at multiple levels.

        Args:
            entity_type: Entity type
            entity_id: Entity UUID
            include_details: Whether to fetch full policy details from enforcer

        Returns:
            List of resolved policies with inheritance information
        """
        # Call PostgreSQL function for efficient resolution
        result = self.supabase.rpc(
            "resolve_entity_policies",
            {
                "p_entity_type": entity_type,
                "p_entity_id": entity_id,
                "p_organization_id": self.organization_id,
            },
        ).execute()

        policies = [ResolvedPolicy(**item) for item in result.data]

        # Optionally fetch full policy details from enforcer
        if include_details and self.enforcer_client:
            for policy in policies:
                try:
                    details = await self.enforcer_client.policies.get(policy.policy_id)
                    policy.policy_details = details.dict()
                except PolicyNotFoundError:
                    logger.warning(
                        "policy_not_found_in_enforcer",
                        policy_id=policy.policy_id,
                    )

        logger.info(
            "policies_resolved",
            entity_type=entity_type,
            entity_id=entity_id[:8],
            policy_count=len(policies),
        )

        return policies

    # ============================================================================
    # Policy Evaluation
    # ============================================================================

    async def evaluate_policies(
        self,
        entity_type: EntityType,
        entity_id: str,
        input_data: Dict[str, Any],
    ) -> Dict[str, EvaluationResult]:
        """
        Evaluate all policies for an entity against input data.

        Args:
            entity_type: Entity type
            entity_id: Entity UUID
            input_data: Input data for evaluation

        Returns:
            Dict mapping policy_id to EvaluationResult
        """
        if not self.enforcer_client:
            return {}

        # Resolve policies
        policies = await self.resolve_entity_policies(entity_type, entity_id)

        # Evaluate each policy
        results = {}
        for policy in policies:
            try:
                result = await self.enforcer_client.evaluation.evaluate(
                    input_data=input_data,
                    policy_id=policy.policy_id,
                )
                results[policy.policy_id] = result
            except Exception as e:
                logger.warning(
                    "policy_evaluation_failed",
                    policy_id=policy.policy_id,
                    error=str(e),
                )

        return results

    async def check_entity_authorization(
        self,
        entity_type: EntityType,
        entity_id: str,
        action: str,
        resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> tuple[bool, List[str]]:
        """
        Check if an entity is authorized to perform an action.

        Args:
            entity_type: Entity type
            entity_id: Entity UUID
            action: Action to check (e.g., "execute", "create", "delete")
            resource: Optional resource identifier
            context: Additional context for evaluation

        Returns:
            Tuple of (is_authorized, violations)
        """
        if not self.enforcer_client:
            # If enforcer is disabled, allow by default
            return True, []

        # Construct input for policy evaluation
        input_data = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "organization_id": self.organization_id,
        }

        if resource:
            input_data["resource"] = resource
        if context:
            input_data.update(context)

        # Evaluate all policies
        eval_results = await self.evaluate_policies(entity_type, entity_id, input_data)

        # Check if all policies allow the action
        is_authorized = True
        all_violations = []

        for policy_id, result in eval_results.items():
            if not result.allow:
                is_authorized = False
                all_violations.extend(result.violations)

        logger.info(
            "authorization_check",
            entity_type=entity_type,
            entity_id=entity_id[:8],
            action=action,
            authorized=is_authorized,
            violation_count=len(all_violations),
        )

        return is_authorized, all_violations
