from typing import Any, Dict, List, Optional, Tuple, TypedDict

from pydantic import BaseModel, ConfigDict, Field

from repello_argus_client.enums.core import Action, PolicyName, Verdict


class PolicyConfig(TypedDict):
    action: Action


class BannedTopicsConfig(PolicyConfig):
    topics: List[str]


class SecretsKeysConfig(PolicyConfig):
    patterns: List[Tuple[str, str]]


class CompetitorMentionConfig(PolicyConfig):
    competitors: List[str]


class PolicyViolationConfig(PolicyConfig):
    rules: List[str]


class SystemPromptLeakConfig(PolicyConfig):
    system_prompt: str


PolicyValue = Dict[str, Any]


Policy = Dict[PolicyName, PolicyValue]

Metadata = Dict[str, Any] | str


class AppliedPolicyInfo(BaseModel):
    """Details of a policy that was evaluated by the backend."""

    action: Action
    metadata: Metadata
    policy_name: PolicyName


class ViolatedPolicyInfo(BaseModel):
    """Details of a policy that found a violation."""

    action_taken: Action
    details: Dict[str, Any] = Field(
        ..., description="Specific details of the violation, like scores or labels."
    )
    policy_name: PolicyName


class ApiResult(BaseModel):
    """The structured result from an Argus API scan."""

    policies_applied: List[AppliedPolicyInfo]
    policies_violated: List[ViolatedPolicyInfo]
    request_id: str
    verdict: Verdict


class GuardrailEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    node_name: str = Field(
        ...,
        description="The name of the decorated function or node (e.g., 'Policy_Lookup').",
    )
    payload: str = Field(
        ..., description="The actual string content that was analyzed by the guardrail."
    )
    scan_result: ApiResult = Field(
        ..., description="The raw result object returned from the Argus API scan."
    )
    request_policy: Optional[Policy] = Field(
        None, description="The policy configuration used for this specific check."
    )
    node_metadata: Optional[Metadata] = Field(
        None,
        description="The user-provided metadata from the decorator for custom observability.",
    )
    session_id: Optional[str] = Field(
        None, description="The session ID active during this check."
    )
    user_id: Optional[str] = Field(
        None,
        description="The user ID for the entity making the request that is intercepted by the guardrail.",
    )
