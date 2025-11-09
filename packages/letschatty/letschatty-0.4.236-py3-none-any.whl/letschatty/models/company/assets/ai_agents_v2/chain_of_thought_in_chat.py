from pydantic import ConfigDict, Field, BaseModel
from typing import Optional, List
from ....base_models import CompanyAssetModel
from ....utils.types.identifier import StrObjectId
from enum import StrEnum
from .chatty_ai_agent import ChattyAIAgent
from ....base_models.chatty_asset_model import ChattyAssetPreview
from typing import ClassVar, Type, Any, Dict
from datetime import datetime
from zoneinfo import ZoneInfo

class ChainOfThoughtInChatTrigger(StrEnum):
    """Trigger for the chain of thought in chat"""
    USER_MESSAGE = "user_message"
    FOLLOW_UP = "follow_up"
    MANUAL_TRIGGER = "manual_trigger"
    AUTOMATIC_TAGGING = "automatic_tagging"
    RETRY_CALL = "retry_call"
    DOUBLE_CHECKER = "double_checker"

class ChainOfThoughtInChatStatus(StrEnum):
    """Status for the chain of thought in chat"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class SimplifiedExecutionEvent(BaseModel):
    """
    Simplified event for UI display embedded in Chain of Thought documents.

    This provides user-facing visibility into the AI agent execution lifecycle
    without requiring access to the full analytics event stream.
    """
    type: str = Field(description="Event type (e.g., 'trigger.user_message', 'call.tagger', 'decision.send')")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    message: str = Field(description="Human-readable message describing the event")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional event-specific data")

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )


class ChainOfThoughtInChatRequest(BaseModel):
    """Request for the chain of thought in chat"""
    id: Optional[StrObjectId] = Field(default=None, description="The id of the chain of thought")
    trigger: ChainOfThoughtInChatTrigger
    trigger_id : str = Field(description="The id of the trigger which could be a message_id or a workflow assigned to chat link id")
    chatty_ai_agent_id : str = Field(description="The chatty ai agent at the moment of triggering the chain of thought")
    chain_of_thought : Optional[str] = Field(default=None, description="The chain of thought")
    name: str = Field(description="A title for the chain of thought", alias="title")

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        arbitrary_types_allowed=True
                )

    @classmethod
    def example(cls) -> dict:
        return {
            "trigger": "user_message",
            "trigger_id": "123",
            "chatty_ai_agent_id": "456",
            "chain_of_thought": "The user's not from the jurisdiction of the law firm, so we need to offer a consultation service with extra fees",
            "name": "Out of jurisdiction - consultation service"
        }

    @property
    def obtained_chain_of_thought(self) -> str:
        if self.chain_of_thought is None:
            raise ValueError("Chain of thought is not set")
        return self.chain_of_thought

class ChainOfThoughtInChatPreview(ChattyAssetPreview):
    """Preview of the chain of thought in chat"""
    chat_id : StrObjectId
    trigger: ChainOfThoughtInChatTrigger
    trigger_id : str = Field(description="The id of the trigger which could be a message_id or a workflow assigned to chat link id")
    chain_of_thought : Optional[str] = Field(default=None, description="The chain of thought")
    status: Optional[ChainOfThoughtInChatStatus] = Field(default=None, description="The status of the chain of thought")
    name: str = Field(description="A title for the chain of thought")

    @classmethod
    def get_projection(cls) -> dict[str, Any]:
        return super().get_projection() | {"chat_id": 1, "trigger": 1, "trigger_id": 1, "chain_of_thought": 1, "name": 1, "status": 1}

    @classmethod
    def from_dict(cls, data: dict) -> 'ChainOfThoughtInChatPreview':
        return cls(**data)

    @classmethod
    def from_asset(cls, asset: 'ChainOfThoughtInChat') -> 'ChainOfThoughtInChatPreview':
        return cls(
            _id=asset.id,
            name=asset.name,
            chat_id=asset.chat_id,
            trigger=asset.trigger,
            trigger_id=asset.trigger_id,
            chain_of_thought=asset.chain_of_thought,
            status=asset.status,
            company_id=asset.company_id,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            deleted_at=asset.deleted_at
        )


class ChainOfThoughtInChat(CompanyAssetModel):
    """Chain of thought in chat"""
    chat_id : StrObjectId
    trigger: ChainOfThoughtInChatTrigger = Field(description="The trigger of the chain of thought")
    trigger_id : str = Field(description="The id of the trigger which could be a message_id or a workflow assigned to chat link id")
    status: ChainOfThoughtInChatStatus = Field(default=ChainOfThoughtInChatStatus.PROCESSING, description="The status of the chain of thought")
    chatty_ai_agent_id : StrObjectId = Field(description="The chatty ai agent id")
    chatty_ai_agent : Dict[str, Any] = Field(description="The chatty ai agent at the moment of triggering the chain of thought")
    chain_of_thought : Optional[str] = Field(default=None, description="The chain of thought")
    name: str = Field(description="A title for the chain of thought", alias="title")
    events: List[SimplifiedExecutionEvent] = Field(default_factory=list, description="Simplified events for UI visibility")
    preview_class: ClassVar[Type[ChattyAssetPreview]] = ChainOfThoughtInChatPreview

    def add_cot_to_existing_cot_if_exists(self, cot: str) -> None:
        if self.chain_of_thought is None:
            self.chain_of_thought = cot
        else:
            self.chain_of_thought += f"\n{cot}"

    def add_event(self, event_type: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a simplified event for UI visibility.

        Args:
            event_type: Event type identifier (e.g., 'trigger.user_message', 'call.tagger')
            message: Human-readable message describing what happened
            metadata: Optional additional data for the event
        """
        self.events.append(SimplifiedExecutionEvent(
            type=event_type,
            timestamp=datetime.now(ZoneInfo("UTC")),
            message=message,
            metadata=metadata
        ))
