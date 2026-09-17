from enum import Enum
from pydantic import BaseModel, Field

class Action(str, Enum):
    observe = "observe"
    keep_in_general = "keep_in_general"
    create_thread = "create_thread"
    propose_trial_channel = "propose_trial_channel"
    create_trial_channel = "create_trial_channel"
    archive_trial_channel = "archive_trial_channel"
    escalate_to_staff = "escalate_to_staff"

class TopicDecision(BaseModel):
    topic: str
    normalized_topic: str
    summary: str
    action: Action
    reason: str
    confidence: float = Field(ge=0, le=1)
    structural_need: float = Field(ge=0, le=1)
    unique_users_estimate: int = Field(ge=0)
    active_days_estimate: int = Field(ge=0)
    meaningful_messages_estimate: int = Field(ge=0)
    is_social_invite: bool
    is_short_lived_trend: bool
    is_repetitive_or_spammy: bool
    existing_channel_sufficient: bool
    suggested_channel_name: str | None = None
    suggested_channel_topic: str | None = None

class CommunityReview(BaseModel):
    health_summary: str
    major_observations: list[str]
    decisions: list[TopicDecision]
