"""
Task Planning Router - AI-powered task analysis and planning using Agno
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal, AsyncIterator
import structlog
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.reasoning import ReasoningTools
from agno.workflow import Workflow, Step
from agno.run.workflow import WorkflowRunOutput
import os
import traceback
import json
import asyncio

from control_plane_api.app.lib.litellm_pricing import get_litellm_pricing, get_model_display_name
from control_plane_api.app.lib.planning_tools import (
    AgentsContextTools,
    TeamsContextTools,
    EnvironmentsContextTools,
    ResourcesContextTools,
)

router = APIRouter()
logger = structlog.get_logger()


# Request/Response Models
class AgentInfo(BaseModel):
    """Information about an agent"""
    id: str
    name: str
    model_id: str
    description: Optional[str] = None

    @field_validator('description', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty string to None for optional fields"""
        if v == '':
            return None
        return v

    @field_validator('model_id', mode='before')
    @classmethod
    def default_model(cls, v):
        """Provide default model if empty"""
        if not v or v == '':
            return 'claude-sonnet-4'
        return v


class TeamInfo(BaseModel):
    """Information about a team"""
    id: str
    name: str
    agents: List[Dict] = []
    description: Optional[str] = None

    @field_validator('description', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty string to None for optional fields"""
        if v == '':
            return None
        return v


class EnvironmentInfo(BaseModel):
    """Information about an execution environment"""
    id: str
    name: str
    type: Optional[str] = "production"
    status: Optional[str] = "active"


class WorkerQueueInfo(BaseModel):
    """Information about a worker queue"""
    id: str
    name: str
    environment_id: Optional[str] = None
    active_workers: int = 0
    status: Optional[str] = "active"


class TaskPlanRequest(BaseModel):
    """Request to plan a task"""
    description: str = Field(..., description="Task description")
    priority: Literal['low', 'medium', 'high', 'critical'] = Field('medium', description="Task priority")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    agents: List[AgentInfo] = Field([], description="Available agents")
    teams: List[TeamInfo] = Field([], description="Available teams")
    environments: List[EnvironmentInfo] = Field([], description="Available execution environments")
    worker_queues: List[WorkerQueueInfo] = Field([], description="Available worker queues")
    refinement_feedback: Optional[str] = Field(None, description="User feedback for plan refinement")
    conversation_context: Optional[str] = Field(None, description="Conversation history for context")
    previous_plan: Optional[Dict] = Field(None, description="Previous plan for refinement")
    iteration: int = Field(1, description="Planning iteration number")


class ComplexityInfo(BaseModel):
    """Task complexity assessment"""
    story_points: int = Field(..., ge=1, le=21, description="Story points (1-21)")
    confidence: Literal['low', 'medium', 'high'] = Field(..., description="Confidence level")
    reasoning: str = Field(..., description="Reasoning for complexity assessment")


class AgentModelInfo(BaseModel):
    """Information about the model an agent will use"""
    model_id: str  # e.g., "claude-sonnet-4", "gpt-4o"
    estimated_input_tokens: int
    estimated_output_tokens: int
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    total_model_cost: float


class ToolUsageInfo(BaseModel):
    """Expected tool usage for an agent"""
    tool_name: str  # e.g., "aws_s3", "kubectl", "bash"
    estimated_calls: int
    cost_per_call: float
    total_tool_cost: float


class TeamBreakdownItem(BaseModel):
    """Breakdown of work for a specific team/agent"""
    team_id: Optional[str] = None
    team_name: str
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    responsibilities: List[str]
    estimated_time_hours: float
    model_info: Optional[AgentModelInfo] = None
    expected_tools: List[ToolUsageInfo] = []
    agent_cost: float = 0.0  # Total cost for this agent (model + tools)


class RecommendedExecution(BaseModel):
    """AI recommendation for which entity should execute the task"""
    entity_type: Literal['agent', 'team']
    entity_id: str
    entity_name: str
    reasoning: str
    recommended_environment_id: Optional[str] = None
    recommended_environment_name: Optional[str] = None
    recommended_worker_queue_id: Optional[str] = None
    recommended_worker_queue_name: Optional[str] = None
    execution_reasoning: Optional[str] = None


class LLMCostBreakdown(BaseModel):
    """Detailed LLM cost breakdown by model"""
    model_id: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    total_cost: float


class ToolCostBreakdown(BaseModel):
    """Tool execution cost breakdown"""
    category: str  # e.g., "AWS APIs", "Database Queries", "External APIs"
    tools: List[ToolUsageInfo]
    category_total: float


class RuntimeCostBreakdown(BaseModel):
    """Runtime and compute costs"""
    worker_execution_hours: float
    cost_per_hour: float
    total_cost: float


class CostBreakdownItem(BaseModel):
    """Individual cost breakdown item (legacy, kept for backwards compatibility)"""
    item: str
    cost: float


class HumanResourceCost(BaseModel):
    """Human resource cost breakdown by role"""
    role: str  # e.g., "Senior DevOps Engineer", "Security Engineer"
    hourly_rate: float  # e.g., 150.00
    estimated_hours: float  # e.g., 8.0
    total_cost: float  # e.g., 1200.00


class CostEstimate(BaseModel):
    """Enhanced cost estimation for the task"""
    estimated_cost_usd: float
    # Legacy breakdown (keep for backwards compatibility)
    breakdown: List[CostBreakdownItem] = []
    # New detailed breakdowns
    llm_costs: List[LLMCostBreakdown] = []
    tool_costs: List[ToolCostBreakdown] = []
    runtime_cost: Optional[RuntimeCostBreakdown] = None


class RealizedSavings(BaseModel):
    """Realized savings by using Kubiya orchestration platform"""
    # Without Kubiya (manual execution)
    without_kubiya_cost: float  # Total cost if done manually
    without_kubiya_hours: float  # Total time if done manually
    without_kubiya_resources: List[HumanResourceCost]  # Resource breakdown

    # With Kubiya (AI orchestration)
    with_kubiya_cost: float  # AI execution cost
    with_kubiya_hours: float  # AI execution time

    # Realized Savings
    money_saved: float  # Dollars saved
    time_saved_hours: float  # Hours saved
    time_saved_percentage: int  # Percentage of time saved

    # Summary
    savings_summary: str  # Compelling savings narrative


class TaskPlanResponse(BaseModel):
    """AI-generated task plan"""
    title: str
    summary: str
    complexity: ComplexityInfo
    team_breakdown: List[TeamBreakdownItem]
    recommended_execution: RecommendedExecution
    cost_estimate: CostEstimate
    realized_savings: RealizedSavings
    risks: List[str] = []
    prerequisites: List[str] = []
    success_criteria: List[str] = []
    # Optional fields for when AI needs clarification
    has_questions: bool = False
    questions: Optional[str] = None


def _infer_agent_specialty(name: str, description: Optional[str]) -> str:
    """
    Infer agent specialty from name and description for better context.
    """
    name_lower = name.lower()
    desc_lower = (description or "").lower()

    # Check for specific specialties
    if "devops" in name_lower or "devops" in desc_lower:
        return "Infrastructure, deployments, cloud operations, monitoring"
    elif "security" in name_lower or "ciso" in name_lower or "security" in desc_lower:
        return "Security audits, compliance, vulnerability scanning, IAM"
    elif "data" in name_lower or "analytics" in desc_lower:
        return "Data analysis, ETL, reporting, database operations"
    elif "backend" in name_lower or "api" in desc_lower:
        return "API development, backend services, database integration"
    elif "frontend" in name_lower or "ui" in desc_lower:
        return "UI development, React/Vue/Angular, responsive design"
    elif "full" in name_lower or "fullstack" in name_lower:
        return "End-to-end development, frontend + backend + infrastructure"
    elif "test" in name_lower or "qa" in desc_lower:
        return "Testing, quality assurance, test automation"
    else:
        return "General automation, scripting, API integration, cloud operations"


def create_planning_agent(organization_id: Optional[str] = None) -> Agent:
    """
    Create an Agno agent for task planning using LiteLLM with context tools

    Args:
        organization_id: Optional organization ID for filtering resources
    """
    # Get LiteLLM configuration
    litellm_api_url = (
        os.getenv("LITELLM_API_URL") or
        os.getenv("LITELLM_API_BASE") or
        "https://llm-proxy.kubiya.ai"
    ).strip()

    litellm_api_key = os.getenv("LITELLM_API_KEY", "").strip()

    if not litellm_api_key:
        raise ValueError("LITELLM_API_KEY environment variable not set")

    model = os.getenv("LITELLM_DEFAULT_MODEL", "kubiya/claude-sonnet-4").strip()

    # Get control plane URL for tools
    control_plane_url = os.getenv("CONTROL_PLANE_API_URL", "http://localhost:8000")

    logger.info(
        "creating_agno_planning_agent_with_tools",
        litellm_api_url=litellm_api_url,
        model=model,
        has_api_key=bool(litellm_api_key),
        control_plane_url=control_plane_url,
        organization_id=organization_id,
    )

    # Initialize context tools
    agents_tools = AgentsContextTools(base_url=control_plane_url, organization_id=organization_id)
    teams_tools = TeamsContextTools(base_url=control_plane_url, organization_id=organization_id)
    environments_tools = EnvironmentsContextTools(base_url=control_plane_url, organization_id=organization_id)
    resources_tools = ResourcesContextTools(base_url=control_plane_url, organization_id=organization_id)

    # Create fast planning agent optimized for speed
    planning_agent = Agent(
        name="Task Planning Agent",
        role="Expert project manager and task planner",
        model=LiteLLM(
            id=f"openai/{model}",
            api_base=litellm_api_url,
            api_key=litellm_api_key,
        ),
        output_schema=TaskPlanResponse,  # Use Pydantic model for structured output
        tools=[
            # Only essential context tools - no ReasoningTools for speed
            agents_tools,
            teams_tools,
            environments_tools,
            resources_tools,
        ],
        instructions=[
            "You are a fast, efficient task planning agent.",
            "",
            "**Use Tools:**",
            "- Call list_agents() for available agents",
            "- Call list_teams() for available teams",
            "- Call list_environments() for environments",
            "- Call list_worker_queues() for worker capacity",
            "",
            "**Plan Requirements:**",
            "- Choose the best agent/team based on capabilities",
            "- Consider resource availability and capacity",
            "- Provide realistic time and cost estimates",
            "- Match worker queues to environments when possible",
            "- Select queues with available capacity (active_workers > 0)",
        ],
        description="Fast task planner for AI agent teams",
        markdown=False,
        add_history_to_context=False,  # Disable for speed
        retries=2,  # Reduced retries
    )

    return planning_agent


@router.post("/tasks/plan")
async def plan_task(request: TaskPlanRequest):
    """
    Generate an AI-powered task plan using Agno workflow

    This endpoint:
    1. Analyzes the task description and context
    2. Assesses complexity (story points)
    3. Recommends which agent/team should execute
    4. Breaks down work by team
    5. Estimates costs and time savings
    6. Identifies risks and prerequisites
    """
    try:
        logger.info(
            "task_planning_requested",
            description=request.description[:100],
            priority=request.priority,
            agents_count=len(request.agents),
            teams_count=len(request.teams),
            iteration=request.iteration,
            has_conversation_context=bool(request.conversation_context and request.conversation_context.strip()),
            has_refinement_feedback=bool(request.refinement_feedback),
        )

        # Validate we have agents or teams
        if not request.agents and not request.teams:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one agent or team must be provided"
            )

        # Fetch LiteLLM pricing data for accurate cost estimation
        logger.info("fetching_litellm_pricing_data")
        pricing_data = await get_litellm_pricing()
        logger.info("litellm_pricing_data_fetched", models_available=len(pricing_data))

        # Create enhanced context for the AI
        agents_context = "\n".join([
            f"- **{a.name}** (ID: `{a.id}`)\n"
            f"  - **Model**: {a.model_id}\n"
            f"  - **Capabilities**: {a.description or 'General-purpose AI agent with code execution, API calls, and automation capabilities'}\n"
            f"  - **Best For**: {_infer_agent_specialty(a.name, a.description)}"
            for a in request.agents
        ])

        teams_context = "\n".join([
            f"- **{t.name}** (ID: `{t.id}`)\n"
            f"  - **Team Size**: {len(t.agents)} agents\n"
            f"  - **Description**: {t.description or 'Cross-functional team capable of handling complex multi-step tasks'}\n"
            f"  - **Team Members**: {', '.join([agent.get('name', 'Agent') for agent in t.agents[:3]])}{'...' if len(t.agents) > 3 else ''}\n"
            f"  - **Best For**: Multi-domain tasks requiring coordination, full-stack development, complex workflows"
            for t in request.teams
        ])

        # Add execution environments context
        environments_context = "\n".join([
            f"- **{e.name}** (ID: `{e.id}`)\n"
            f"  - **Type**: {e.type}\n"
            f"  - **Status**: {e.status}"
            for e in request.environments
        ]) if request.environments else "No execution environments specified"

        # Add worker queues context
        worker_queues_context = "\n".join([
            f"- **{q.name}** (ID: `{q.id}`)\n"
            f"  - **Environment**: {q.environment_id or 'Not specified'}\n"
            f"  - **Active Workers**: {q.active_workers}\n"
            f"  - **Status**: {q.status}\n"
            f"  - **Capacity**: {'Available' if q.active_workers > 0 and q.status == 'active' else 'Limited or Inactive'}"
            for q in request.worker_queues
        ]) if request.worker_queues else "No worker queues specified"

        # Add system capabilities context
        system_capabilities = """
**Available System Capabilities:**
- **Code Execution**: Python, Bash, JavaScript, and other languages
- **Cloud Integrations**: AWS (S3, EC2, Lambda, RDS, CloudWatch), Azure, GCP
- **APIs & Tools**: REST APIs, GraphQL, Kubernetes, Docker, Terraform
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Monitoring**: Datadog, Prometheus, Grafana, CloudWatch
- **Security**: IAM policies, security scanning, compliance checks
- **DevOps**: CI/CD pipelines, Infrastructure as Code, automation scripts
"""

        # Build pricing context from LiteLLM data for common models
        pricing_context = """
**Model Pricing Reference** (use these for accurate cost estimates):
- **Claude Sonnet 4**: $0.003/1K input, $0.015/1K output tokens
- **Claude 3.5 Sonnet**: $0.003/1K input, $0.015/1K output tokens
- **Claude 3 Opus**: $0.015/1K input, $0.075/1K output tokens
- **Claude 3 Haiku**: $0.00025/1K input, $0.00125/1K output tokens
- **GPT-4o**: $0.0025/1K input, $0.01/1K output tokens
- **GPT-4o Mini**: $0.00015/1K input, $0.0006/1K output tokens
- **GPT-4 Turbo**: $0.01/1K input, $0.03/1K output tokens
- **Gemini 2.0 Flash**: $0.0001/1K input, $0.0003/1K output tokens
- **Gemini 1.5 Pro**: $0.00125/1K input, $0.005/1K output tokens

**Tool Cost Estimates:**
- AWS API calls: $0.0004-0.001 per call
- Database queries: $0.0001 per query
- Kubernetes operations: Free (compute cost only)
- Bash/shell commands: Free (compute cost only)

**Runtime Costs:**
- Worker execution: $0.10/hour typical
"""

        # Check if this is a refinement or subsequent iteration
        is_refinement = request.iteration > 1 and request.refinement_feedback
        has_conversation_history = bool(request.conversation_context and request.conversation_context.strip())

        # After iteration 1, or if there's conversation history, be decisive
        should_be_decisive = request.iteration > 1 or has_conversation_history

        # Build the planning prompt
        planning_prompt = f"""
# Task Planning Request - Iteration #{request.iteration}

## Task Description
{request.description}

## Priority
{request.priority.upper()}

{"## Previous Conversation (USE THIS CONTEXT)" if has_conversation_history else ""}
{request.conversation_context if has_conversation_history else ""}

{"## User Feedback for Refinement" if request.refinement_feedback else ""}
{request.refinement_feedback if request.refinement_feedback else ""}

{"## Previous Plan (to be refined)" if request.previous_plan else ""}
{json.dumps(request.previous_plan, indent=2) if request.previous_plan else ""}

## Available Resources

### Agents
{agents_context if agents_context else "No individual agents available"}

### Teams
{teams_context if teams_context else "No teams available"}

### Execution Environments
{environments_context}

### Worker Queues
{worker_queues_context}

{system_capabilities}

{pricing_context}

## Your Task

{'**BE DECISIVE**: You have conversation history showing the user has already provided context. DO NOT ask more questions. Use the information provided in the conversation history above to create a reasonable plan. Make sensible assumptions where needed and proceed with planning.' if should_be_decisive else '**FIRST ITERATION**: Review if you have enough context. ONLY ask questions if you are missing CRITICAL information that makes planning impossible (like completely unknown technology stack or domain). If the task is reasonably clear, proceed with planning and make reasonable assumptions.'}

{'**IMPORTANT**: DO NOT ask questions. The user wants a plan now. Use the conversation history above.' if should_be_decisive else 'If you need CRITICAL information to proceed, respond with:'}
{'```json' if not should_be_decisive else ''}
{'{' if not should_be_decisive else ''}
{'  "has_questions": true,' if not should_be_decisive else ''}
{'  "questions": "List 1-2 CRITICAL questions (not nice-to-haves). Be very selective."' if not should_be_decisive else ''}
{'}' if not should_be_decisive else ''}
{'```' if not should_be_decisive else ''}

Otherwise, analyze this task and provide a comprehensive plan in the following JSON format:

{{
  "title": "Concise task title",
  "summary": "2-3 sentence summary of what needs to be done",
  "complexity": {{
    "story_points": 5,
    "confidence": "medium",
    "reasoning": "Explanation of complexity assessment"
  }},
  "team_breakdown": [
    {{
      "team_id": "team-uuid-or-null",
      "team_name": "Team Name or Agent Name",
      "agent_id": "agent-uuid-or-null",
      "agent_name": "Agent Name if individual agent",
      "responsibilities": ["Task 1", "Task 2"],
      "estimated_time_hours": 2.5
    }}
  ],
  "recommended_execution": {{
    "entity_type": "agent or team",
    "entity_id": "uuid-of-recommended-agent-or-team",
    "entity_name": "Name",
    "reasoning": "Why this entity is best suited for this task",
    "recommended_environment_id": "uuid-of-best-environment-or-null",
    "recommended_environment_name": "Environment Name or null",
    "recommended_worker_queue_id": "uuid-of-best-worker-queue-or-null",
    "recommended_worker_queue_name": "Worker Queue Name or null",
    "execution_reasoning": "Why this environment/queue is optimal for execution (consider capacity, type, status)"
  }},
  "cost_estimate": {{
    "estimated_cost_usd": 1.50,
    "breakdown": [
      {{"item": "API calls", "cost": 1.00}},
      {{"item": "Processing", "cost": 0.50}}
    ]
  }},
  "realized_savings": {{
    "without_kubiya_cost": 1440.0,
    "without_kubiya_hours": 10.0,
    "without_kubiya_resources": [
      {{
        "role": "Senior DevOps Engineer",
        "hourly_rate": 150.0,
        "estimated_hours": 8.0,
        "total_cost": 1200.0
      }},
      {{
        "role": "Security Engineer",
        "hourly_rate": 120.0,
        "estimated_hours": 2.0,
        "total_cost": 240.0
      }}
    ],
    "with_kubiya_cost": 3.75,
    "with_kubiya_hours": 4.0,
    "money_saved": 1436.25,
    "time_saved_hours": 6.0,
    "time_saved_percentage": 60,
    "savings_summary": "By using Kubiya's AI orchestration, you saved $1,436 and 6 hours. Manual execution would require 10 hours of skilled engineers ($1,440), but Kubiya completes it in 4 hours for just $3.75."
  }},
  "risks": ["Risk 1", "Risk 2"],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
  "success_criteria": ["Criterion 1", "Criterion 2"]
}}

**Important Guidelines:**
1. For `recommended_execution`, choose the MOST CAPABLE entity (agent or team) based on:
   - Task complexity
   - Agent/team capabilities and model
   - Description fit
   - Whether multiple agents are needed (prefer team) or single agent is sufficient
2. The recommended entity MUST be from the available agents/teams list above
3. For `recommended_environment_id` and `recommended_worker_queue_id`:
   - Choose the BEST environment based on task requirements (production vs staging vs development)
   - Choose a worker queue with AVAILABLE CAPACITY (active_workers > 0 and status = 'active')
   - Match worker queue to the selected environment if possible
   - Provide clear `execution_reasoning` explaining your environment/queue selection
   - If no suitable queue is available, still recommend one and note the capacity concern in reasoning
4. Use IDs exactly as provided from the lists above
4. **CRITICAL - Enhanced Cost Breakdown**:
   - **Team Breakdown**: For each agent/team member, include:
     - `model_info`: Specify the model they'll use (use the model_id from agent info)
       - Estimate input/output tokens based on task complexity
       - Use realistic pricing: Claude Sonnet 4 ($0.003/1K in, $0.015/1K out), GPT-4o ($0.0025/1K in, $0.01/1K out)
       - Calculate total_model_cost accurately
     - `expected_tools`: List tools they'll use with estimated call counts
       - AWS APIs: $0.0004-0.001 per call
       - Database queries: $0.0001 per query
       - Free tools (kubectl, bash): $0.0 per call
     - `agent_cost`: Sum of model_cost + tool_costs
   - **Cost Estimate**: Provide detailed breakdown:
     - `llm_costs`: Array of LLM costs by model (aggregate from team breakdown)
     - `tool_costs`: Categorized tool costs (AWS APIs, Database Queries, External APIs)
     - `runtime_cost`: Worker execution time × cost per hour ($0.10/hr typical)
     - Ensure `estimated_cost_usd` = sum of all LLM + tool + runtime costs
     - Legacy `breakdown` still required for backwards compatibility
5. **Realistic Token Estimates**:
   - Simple tasks (story points 1-3): 2-5K input, 1-2K output tokens per agent
   - Medium tasks (story points 5-8): 5-10K input, 2-5K output tokens per agent
   - Complex tasks (story points 13-21): 10-20K input, 5-10K output tokens per agent
6. **Tool Call Estimates**:
   - Consider what APIs/tools the agent will actually use for this specific task
   - Be realistic: Simple tasks might only need 5-10 API calls total
   - Complex deployments might need 50+ API calls across multiple tools
7. **CRITICAL - Realized Savings Calculation** (keep for backwards compatibility):
   - **WITHOUT KUBIYA**: Calculate what it would cost using manual human execution
     - Break down by SPECIFIC ROLES (e.g., "Senior DevOps Engineer", "Security Engineer")
     - Use realistic hourly rates: Senior ($120-200/hr), Mid-level ($80-120/hr), Junior ($50-80/hr)
     - Calculate without_kubiya_cost = sum of all human resource costs
     - Estimate without_kubiya_hours = total time if done manually
   - **WITH KUBIYA**: Calculate AI orchestration costs and time
     - with_kubiya_cost = estimated AI execution cost (API calls, compute)
     - with_kubiya_hours = estimated time for AI agents to complete
   - **REALIZED SAVINGS**:
     - money_saved = without_kubiya_cost - with_kubiya_cost
     - time_saved_hours = without_kubiya_hours - with_kubiya_hours
     - time_saved_percentage = (time_saved_hours / without_kubiya_hours) * 100
   - **COMPELLING NARRATIVE**: Create savings_summary that emphasizes the concrete savings:
     - "By using Kubiya, you saved $X and Y hours"
     - Show the contrast: "Without Kubiya: $X (Y hours)" vs "With Kubiya: $X (Y hours)"
6. Be specific and actionable in all fields
7. Output ONLY valid JSON, no markdown formatting
"""

        # Get organization ID from agents/teams if available
        organization_id = None
        if request.agents and len(request.agents) > 0:
            # Try to infer organization from first agent (you may want to pass this explicitly)
            organization_id = getattr(request.agents[0], "organization_id", None)
        elif request.teams and len(request.teams) > 0:
            organization_id = getattr(request.teams[0], "organization_id", None)

        # Create planning agent using LiteLLM with tools
        logger.info("creating_planning_agent_with_tools", organization_id=organization_id)
        planning_agent = create_planning_agent(organization_id=organization_id)
        logger.info("planning_agent_created", agent_name=planning_agent.name)

        # Run the agent with the planning prompt
        logger.info("executing_agent_run", prompt_length=len(planning_prompt))
        response = planning_agent.run(planning_prompt)
        logger.info("agent_run_completed", has_content=hasattr(response, 'content'))

        # With output_schema, response.content is already a TaskPlanResponse object
        if not isinstance(response.content, TaskPlanResponse):
            logger.error("unexpected_response_type", response_type=type(response.content).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent returned unexpected response type: {type(response.content).__name__}"
            )

        plan = response.content

        # Check if AI is asking questions (for first iteration)
        if plan.has_questions:
            logger.info("task_planner_asking_questions", iteration=request.iteration)
            return {
                "plan": plan,
                "has_questions": True,
                "questions": plan.questions
            }

        logger.info(
            "task_plan_generated",
            title=plan.title,
            complexity=plan.complexity.story_points,
            recommended_entity=plan.recommended_execution.entity_name,
            iteration=request.iteration,
            is_refinement=is_refinement,
        )

        return {"plan": plan}

    except json.JSONDecodeError as e:
        logger.error("json_parse_error", error=str(e), traceback=traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response: {str(e)}"
        )
    except ValueError as e:
        # Catch missing API key or other config errors
        logger.error("configuration_error", error=str(e), traceback=traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error("task_planning_error", error=str(e), error_type=type(e).__name__, traceback=traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task planning failed: {str(e)}"
        )


def format_sse_message(event: str, data: dict) -> str:
    """Format data as Server-Sent Event message"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def generate_task_plan_stream(request: TaskPlanRequest) -> AsyncIterator[str]:
    """
    Async generator that yields SSE events during task planning
    """
    try:
        # Yield initial progress
        yield format_sse_message("progress", {
            "stage": "initializing",
            "message": "🚀 Initializing AI Task Planner...",
            "progress": 10
        })

        await asyncio.sleep(0.1)  # Small delay for UX

        # Validate we have agents or teams
        if not request.agents and not request.teams:
            yield format_sse_message("error", {
                "message": "At least one agent or team must be provided"
            })
            return

        logger.info(
            "task_planning_requested_stream",
            description=request.description[:100],
            priority=request.priority,
            agents_count=len(request.agents),
            teams_count=len(request.teams),
            iteration=request.iteration,
        )

        # Fetch LiteLLM pricing data for accurate cost estimation
        logger.info("fetching_litellm_pricing_data_stream")
        pricing_data = await get_litellm_pricing()
        logger.info("litellm_pricing_data_fetched_stream", models_available=len(pricing_data))

        # Yield context gathering progress
        yield format_sse_message("progress", {
            "stage": "context",
            "message": "🌐 Gathering organizational context...",
            "progress": 20
        })

        await asyncio.sleep(0.2)

        # Create enhanced context for the AI (same as original endpoint)
        agents_context = "\n".join([
            f"- **{a.name}** (ID: `{a.id}`)\n"
            f"  - **Model**: {a.model_id}\n"
            f"  - **Capabilities**: {a.description or 'General-purpose AI agent with code execution, API calls, and automation capabilities'}\n"
            f"  - **Best For**: {_infer_agent_specialty(a.name, a.description)}"
            for a in request.agents
        ])

        teams_context = "\n".join([
            f"- **{t.name}** (ID: `{t.id}`)\n"
            f"  - **Team Size**: {len(t.agents)} agents\n"
            f"  - **Description**: {t.description or 'Cross-functional team capable of handling complex multi-step tasks'}\n"
            f"  - **Team Members**: {', '.join([agent.get('name', 'Agent') for agent in t.agents[:3]])}{'...' if len(t.agents) > 3 else ''}\n"
            f"  - **Best For**: Multi-domain tasks requiring coordination, full-stack development, complex workflows"
            for t in request.teams
        ])

        # Add execution environments context
        environments_context = "\n".join([
            f"- **{e.name}** (ID: `{e.id}`)\n"
            f"  - **Type**: {e.type}\n"
            f"  - **Status**: {e.status}"
            for e in request.environments
        ]) if request.environments else "No execution environments specified"

        # Add worker queues context
        worker_queues_context = "\n".join([
            f"- **{q.name}** (ID: `{q.id}`)\n"
            f"  - **Environment**: {q.environment_id or 'Not specified'}\n"
            f"  - **Active Workers**: {q.active_workers}\n"
            f"  - **Status**: {q.status}\n"
            f"  - **Capacity**: {'Available' if q.active_workers > 0 and q.status == 'active' else 'Limited or Inactive'}"
            for q in request.worker_queues
        ]) if request.worker_queues else "No worker queues specified"

        # Add system capabilities context
        system_capabilities = """
**Available System Capabilities:**
- **Code Execution**: Python, Bash, JavaScript, and other languages
- **Cloud Integrations**: AWS (S3, EC2, Lambda, RDS, CloudWatch), Azure, GCP
- **APIs & Tools**: REST APIs, GraphQL, Kubernetes, Docker, Terraform
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Monitoring**: Datadog, Prometheus, Grafana, CloudWatch
- **Security**: IAM policies, security scanning, compliance checks
- **DevOps**: CI/CD pipelines, Infrastructure as Code, automation scripts
"""

        # Build pricing context from LiteLLM data for common models
        pricing_context = """
**Model Pricing Reference** (use these for accurate cost estimates):
- **Claude Sonnet 4**: $0.003/1K input, $0.015/1K output tokens
- **Claude 3.5 Sonnet**: $0.003/1K input, $0.015/1K output tokens
- **Claude 3 Opus**: $0.015/1K input, $0.075/1K output tokens
- **Claude 3 Haiku**: $0.00025/1K input, $0.00125/1K output tokens
- **GPT-4o**: $0.0025/1K input, $0.01/1K output tokens
- **GPT-4o Mini**: $0.00015/1K input, $0.0006/1K output tokens
- **GPT-4 Turbo**: $0.01/1K input, $0.03/1K output tokens
- **Gemini 2.0 Flash**: $0.0001/1K input, $0.0003/1K output tokens
- **Gemini 1.5 Pro**: $0.00125/1K input, $0.005/1K output tokens

**Tool Cost Estimates:**
- AWS API calls: $0.0004-0.001 per call
- Database queries: $0.0001 per query
- Kubernetes operations: Free (compute cost only)
- Bash/shell commands: Free (compute cost only)

**Runtime Costs:**
- Worker execution: $0.10/hour typical
"""

        # Yield team analysis progress
        yield format_sse_message("progress", {
            "stage": "analyzing_teams",
            "message": f"👥 Finding best teams ({len(request.agents)} agents, {len(request.teams)} teams)...",
            "progress": 35
        })

        await asyncio.sleep(0.2)

        # Check if this is a refinement or subsequent iteration
        is_refinement = request.iteration > 1 and request.refinement_feedback
        has_conversation_history = bool(request.conversation_context and request.conversation_context.strip())
        should_be_decisive = request.iteration > 1 or has_conversation_history

        # Yield complexity analysis progress
        yield format_sse_message("progress", {
            "stage": "complexity",
            "message": "🔍 Analyzing task complexity...",
            "progress": 50
        })

        await asyncio.sleep(0.2)

        # Build the planning prompt (same as original)
        planning_prompt = f"""
# Task Planning Request - Iteration #{request.iteration}

## Task Description
{request.description}

## Priority
{request.priority.upper()}

{"## Previous Conversation (USE THIS CONTEXT)" if has_conversation_history else ""}
{request.conversation_context if has_conversation_history else ""}

{"## User Feedback for Refinement" if request.refinement_feedback else ""}
{request.refinement_feedback if request.refinement_feedback else ""}

{"## Previous Plan (to be refined)" if request.previous_plan else ""}
{json.dumps(request.previous_plan, indent=2) if request.previous_plan else ""}

## Available Resources

### Agents
{agents_context if agents_context else "No individual agents available"}

### Teams
{teams_context if teams_context else "No teams available"}

### Execution Environments
{environments_context}

### Worker Queues
{worker_queues_context}

{system_capabilities}

{pricing_context}

## Your Task

{'**BE DECISIVE**: You have conversation history showing the user has already provided context. DO NOT ask more questions. Use the information provided in the conversation history above to create a reasonable plan. Make sensible assumptions where needed and proceed with planning.' if should_be_decisive else '**FIRST ITERATION**: Review if you have enough context. ONLY ask questions if you are missing CRITICAL information that makes planning impossible (like completely unknown technology stack or domain). If the task is reasonably clear, proceed with planning and make reasonable assumptions.'}

{'**IMPORTANT**: DO NOT ask questions. The user wants a plan now. Use the conversation history above.' if should_be_decisive else 'If you need CRITICAL information to proceed, respond with:'}
{'```json' if not should_be_decisive else ''}
{'{' if not should_be_decisive else ''}
{'  "has_questions": true,' if not should_be_decisive else ''}
{'  "questions": "List 1-2 CRITICAL questions (not nice-to-haves). Be very selective."' if not should_be_decisive else ''}
{'}' if not should_be_decisive else ''}
{'```' if not should_be_decisive else ''}

Otherwise, analyze this task and provide a comprehensive plan in the following JSON format:

{{
  "title": "Concise task title",
  "summary": "2-3 sentence summary of what needs to be done",
  "complexity": {{
    "story_points": 5,
    "confidence": "medium",
    "reasoning": "Explanation of complexity assessment"
  }},
  "team_breakdown": [
    {{
      "team_id": "team-uuid-or-null",
      "team_name": "Team Name or Agent Name",
      "agent_id": "agent-uuid-or-null",
      "agent_name": "Agent Name if individual agent",
      "responsibilities": ["Task 1", "Task 2"],
      "estimated_time_hours": 2.5
    }}
  ],
  "recommended_execution": {{
    "entity_type": "agent or team",
    "entity_id": "uuid-of-recommended-agent-or-team",
    "entity_name": "Name",
    "reasoning": "Why this entity is best suited for this task",
    "recommended_environment_id": "uuid-of-best-environment-or-null",
    "recommended_environment_name": "Environment Name or null",
    "recommended_worker_queue_id": "uuid-of-best-worker-queue-or-null",
    "recommended_worker_queue_name": "Worker Queue Name or null",
    "execution_reasoning": "Why this environment/queue is optimal for execution (consider capacity, type, status)"
  }},
  "cost_estimate": {{
    "estimated_cost_usd": 1.50,
    "breakdown": [
      {{"item": "API calls", "cost": 1.00}},
      {{"item": "Processing", "cost": 0.50}}
    ]
  }},
  "realized_savings": {{
    "without_kubiya_cost": 1440.0,
    "without_kubiya_hours": 10.0,
    "without_kubiya_resources": [
      {{
        "role": "Senior DevOps Engineer",
        "hourly_rate": 150.0,
        "estimated_hours": 8.0,
        "total_cost": 1200.0
      }},
      {{
        "role": "Security Engineer",
        "hourly_rate": 120.0,
        "estimated_hours": 2.0,
        "total_cost": 240.0
      }}
    ],
    "with_kubiya_cost": 3.75,
    "with_kubiya_hours": 4.0,
    "money_saved": 1436.25,
    "time_saved_hours": 6.0,
    "time_saved_percentage": 60,
    "savings_summary": "By using Kubiya's AI orchestration, you saved $1,436 and 6 hours. Manual execution would require 10 hours of skilled engineers ($1,440), but Kubiya completes it in 4 hours for just $3.75."
  }},
  "risks": ["Risk 1", "Risk 2"],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
  "success_criteria": ["Criterion 1", "Criterion 2"]
}}

**Important Guidelines:**
1. For `recommended_execution`, choose the MOST CAPABLE entity (agent or team) based on:
   - Task complexity
   - Agent/team capabilities and model
   - Description fit
   - Whether multiple agents are needed (prefer team) or single agent is sufficient
2. The recommended entity MUST be from the available agents/teams list above
3. For `recommended_environment_id` and `recommended_worker_queue_id`:
   - Choose the BEST environment based on task requirements (production vs staging vs development)
   - Choose a worker queue with AVAILABLE CAPACITY (active_workers > 0 and status = 'active')
   - Match worker queue to the selected environment if possible
   - Provide clear `execution_reasoning` explaining your environment/queue selection
   - If no suitable queue is available, still recommend one and note the capacity concern in reasoning
4. Use IDs exactly as provided from the lists above
4. **CRITICAL - Enhanced Cost Breakdown**:
   - **Team Breakdown**: For each agent/team member, include:
     - `model_info`: Specify the model they'll use (use the model_id from agent info)
       - Estimate input/output tokens based on task complexity
       - Use realistic pricing: Claude Sonnet 4 ($0.003/1K in, $0.015/1K out), GPT-4o ($0.0025/1K in, $0.01/1K out)
       - Calculate total_model_cost accurately
     - `expected_tools`: List tools they'll use with estimated call counts
       - AWS APIs: $0.0004-0.001 per call
       - Database queries: $0.0001 per query
       - Free tools (kubectl, bash): $0.0 per call
     - `agent_cost`: Sum of model_cost + tool_costs
   - **Cost Estimate**: Provide detailed breakdown:
     - `llm_costs`: Array of LLM costs by model (aggregate from team breakdown)
     - `tool_costs`: Categorized tool costs (AWS APIs, Database Queries, External APIs)
     - `runtime_cost`: Worker execution time × cost per hour ($0.10/hr typical)
     - Ensure `estimated_cost_usd` = sum of all LLM + tool + runtime costs
     - Legacy `breakdown` still required for backwards compatibility
5. **Realistic Token Estimates**:
   - Simple tasks (story points 1-3): 2-5K input, 1-2K output tokens per agent
   - Medium tasks (story points 5-8): 5-10K input, 2-5K output tokens per agent
   - Complex tasks (story points 13-21): 10-20K input, 5-10K output tokens per agent
6. **Tool Call Estimates**:
   - Consider what APIs/tools the agent will actually use for this specific task
   - Be realistic: Simple tasks might only need 5-10 API calls total
   - Complex deployments might need 50+ API calls across multiple tools
7. **CRITICAL - Realized Savings Calculation** (keep for backwards compatibility):
   - **WITHOUT KUBIYA**: Calculate what it would cost using manual human execution
     - Break down by SPECIFIC ROLES (e.g., "Senior DevOps Engineer", "Security Engineer")
     - Use realistic hourly rates: Senior ($120-200/hr), Mid-level ($80-120/hr), Junior ($50-80/hr)
     - Calculate without_kubiya_cost = sum of all human resource costs
     - Estimate without_kubiya_hours = total time if done manually
   - **WITH KUBIYA**: Calculate AI orchestration costs and time
     - with_kubiya_cost = estimated AI execution cost (API calls, compute)
     - with_kubiya_hours = estimated time for AI agents to complete
   - **REALIZED SAVINGS**:
     - money_saved = without_kubiya_cost - with_kubiya_cost
     - time_saved_hours = without_kubiya_hours - with_kubiya_hours
     - time_saved_percentage = (time_saved_hours / without_kubiya_hours) * 100
   - **COMPELLING NARRATIVE**: Create savings_summary that emphasizes the concrete savings:
     - "By using Kubiya, you saved $X and Y hours"
     - Show the contrast: "Without Kubiya: $X (Y hours)" vs "With Kubiya: $X (Y hours)"
6. Be specific and actionable in all fields
7. Output ONLY valid JSON, no markdown formatting
"""

        # Yield AI agent creation progress
        yield format_sse_message("progress", {
            "stage": "creating_agent",
            "message": "🤖 Creating AI planning agent...",
            "progress": 60
        })

        await asyncio.sleep(0.2)

        # Get organization ID from agents/teams if available
        organization_id = None
        if request.agents and len(request.agents) > 0:
            organization_id = getattr(request.agents[0], "organization_id", None)
        elif request.teams and len(request.teams) > 0:
            organization_id = getattr(request.teams[0], "organization_id", None)

        # Create planning agent with tools
        logger.info("creating_planning_agent_stream", organization_id=organization_id)
        planning_agent = create_planning_agent(organization_id=organization_id)

        # Yield generating plan progress
        yield format_sse_message("progress", {
            "stage": "generating",
            "message": "✨ Generating comprehensive plan...",
            "progress": 75
        })

        # Run the agent with streaming to capture reasoning
        # The actual reasoning will be streamed in real-time (no need for generic "thinking" message)
        logger.info("executing_agent_run_stream", prompt_length=len(planning_prompt))

        # Use streaming to capture reasoning content as it comes in
        # ReasoningTools provide structured reasoning capabilities
        reasoning_chunks = []
        final_response = None

        # Set timeout for agent run to prevent hanging (2 minutes max)
        agent_timeout = 120  # seconds
        start_time = asyncio.get_event_loop().time()

        # Stream with ReasoningTools - it handles reasoning display automatically
        for chunk in planning_agent.run(planning_prompt, stream=True):
            # Check for timeout
            if asyncio.get_event_loop().time() - start_time > agent_timeout:
                logger.error("agent_run_timeout", elapsed=agent_timeout)
                raise TimeoutError(f"Agent run exceeded {agent_timeout}s timeout")
            # Log chunk attributes for debugging
            logger.info("streaming_chunk_received",
                       has_content=hasattr(chunk, 'content'),
                       has_reasoning=hasattr(chunk, 'reasoning_content'),
                       has_tool_calls=hasattr(chunk, 'tool_calls'),
                       content_type=type(chunk.content).__name__ if hasattr(chunk, 'content') else None)

            # Check for reasoning content (Agno's reasoning agent output)
            if hasattr(chunk, 'reasoning_content') and chunk.reasoning_content:
                reasoning_text = str(chunk.reasoning_content)
                reasoning_chunks.append(reasoning_text)

                # Stream reasoning to frontend in real-time
                yield format_sse_message("reasoning", {
                    "content": reasoning_text,
                    "is_complete": False
                })

            # Check for regular content chunks (chain-of-thought reasoning before structured output)
            elif hasattr(chunk, 'content') and chunk.content and not hasattr(chunk, 'tool_calls'):
                # This might be reasoning content - stream it to frontend
                reasoning_text = str(chunk.content)

                # Filter out the final structured response (which will be a dict/object)
                if not isinstance(chunk.content, (dict, TaskPlanResponse)):
                    reasoning_chunks.append(reasoning_text)

                    # Stream reasoning to frontend in real-time
                    yield format_sse_message("reasoning", {
                        "content": reasoning_text,
                        "is_complete": False
                    })
                    logger.info("streaming_reasoning_chunk", length=len(reasoning_text))
                else:
                    # This is the final response with structured output
                    final_response = chunk
                    logger.info("received_final_structured_response")

            # Check for tool calls (when agent uses planning tools)
            if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                for tool_call in chunk.tool_calls:
                    tool_name = tool_call.function.name if hasattr(tool_call, 'function') else str(tool_call)
                    yield format_sse_message("tool_call", {
                        "tool_name": tool_name,
                        "message": f"🔧 Calling tool: {tool_name}"
                    })
                    logger.info("streaming_tool_call", tool_name=tool_name)

            # Capture the final response if we haven't yet
            # In streaming mode, Agno returns the full structured response at the end
            if hasattr(chunk, 'content') and isinstance(chunk.content, (dict, TaskPlanResponse)):
                final_response = chunk

        # Signal reasoning is complete
        if reasoning_chunks:
            full_reasoning = ''.join(reasoning_chunks)
            yield format_sse_message("reasoning", {
                "content": "",
                "is_complete": True,
                "full_reasoning": full_reasoning,
                "token_count": len(full_reasoning.split())
            })

        logger.info("agent_run_completed_stream", has_final_response=final_response is not None, reasoning_length=len(reasoning_chunks))

        # Yield calculating savings progress
        yield format_sse_message("progress", {
            "stage": "calculating",
            "message": "💰 Calculating cost savings...",
            "progress": 90
        })

        await asyncio.sleep(0.2)

        # With output_schema, the final response.content should be a TaskPlanResponse object
        if not final_response or not hasattr(final_response, 'content'):
            logger.error("no_final_response_from_agent")
            yield format_sse_message("error", {
                "message": "Agent did not return a final response. Please try again."
            })
            return

        # Validate that we got the correct type
        if not isinstance(final_response.content, TaskPlanResponse):
            logger.error(
                "unexpected_response_type",
                type_received=type(final_response.content).__name__,
                content_preview=str(final_response.content)[:200]
            )
            yield format_sse_message("error", {
                "message": f"Agent returned unexpected response type: {type(final_response.content).__name__}"
            })
            return

        plan = final_response.content

        # Check if AI is asking questions
        if plan.has_questions:
            logger.info("task_planner_asking_questions_stream", iteration=request.iteration)
            yield format_sse_message("complete", {
                "has_questions": True,
                "questions": plan.questions,
                "progress": 100
            })
            return

        logger.info(
            "task_plan_generated_stream",
            title=plan.title,
            complexity=plan.complexity.story_points,
            recommended_entity=plan.recommended_execution.entity_name,
            iteration=request.iteration,
        )

        # Yield complete event with the full plan
        yield format_sse_message("complete", {
            "plan": plan.model_dump(),
            "progress": 100,
            "message": "✅ Plan generated successfully!"
        })

    except Exception as e:
        from sqlalchemy.exc import OperationalError, DisconnectionError
        from control_plane_api.app.database import dispose_engine, IS_SERVERLESS

        error_type = type(e).__name__
        logger.error("task_planning_stream_error", error=str(e), error_type=error_type)

        # Specific handling for database connection errors
        if isinstance(e, (OperationalError, DisconnectionError)):
            error_msg = "Database connection lost. This may be due to serverless timeout or connection pool exhaustion. Please try again."
            logger.error("database_connection_error_in_planning", error=str(e))

            # Dispose engine in serverless to force fresh connections on next request
            if IS_SERVERLESS:
                dispose_engine()
        else:
            error_msg = f"Task planning failed: {str(e)}"

        yield format_sse_message("error", {
            "message": error_msg
        })
    finally:
        # Cleanup: Dispose engine in serverless environments after each invocation
        from control_plane_api.app.database import dispose_engine, IS_SERVERLESS
        if IS_SERVERLESS:
            logger.info("cleaning_up_serverless_database_connections")
            dispose_engine()


@router.post("/tasks/plan/stream")
async def plan_task_stream(request: TaskPlanRequest):
    """
    Generate an AI-powered task plan with streaming progress updates (SSE)

    This endpoint streams progress events during plan generation:
    - initializing: Starting the planner
    - context: Gathering organizational context
    - analyzing_teams: Finding best teams
    - complexity: Analyzing task complexity
    - creating_agent: Creating AI agent
    - generating: Generating plan
    - calculating: Calculating savings
    - complete: Final plan ready
    - error: If something went wrong
    """
    return StreamingResponse(
        generate_task_plan_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/tasks/plan/health")
async def planning_health():
    """Health check for task planning endpoint"""
    return {
        "status": "healthy",
        "service": "task_planning",
        "ai_provider": "OpenAI GPT-4o",
    }
