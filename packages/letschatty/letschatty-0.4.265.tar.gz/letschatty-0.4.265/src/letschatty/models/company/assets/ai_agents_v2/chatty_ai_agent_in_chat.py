"""
Chatty AI Agent In Chat - Standalone model for AI agent state in chats

This is a standalone version of ChattyAIAgentAssignedToChat that lives in its own collection
rather than being embedded in the Chat document. This allows Lambda to manage AI agent state
independently without loading entire chat documents.
"""

from letschatty.models.analytics.events.base import EventType
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, ClassVar, List, Dict, Any
from enum import StrEnum
from letschatty.models.base_models.chatty_asset_model import CompanyAssetModel, ChattyAssetPreview
from letschatty.models.utils.types.identifier import StrObjectId
from .chain_of_thought_in_chat import ChainOfThoughtInChatTrigger, ChainOfThoughtInChat
from .chatty_ai_mode import ChattyAIMode
import logging

logger = logging.getLogger(__name__)

class SimplifiedExecutionEvent(BaseModel):
    """
    Simplified event for UI display embedded in Chain of Thought documents.

    This provides user-facing visibility into the AI agent execution lifecycle
    without requiring access to the full analytics event stream.
    """
    type: EventType = Field(description="Event type (e.g., EventType.CHATTY_AI_AGENT_IN_CHAT_STATE_CALL_STARTED, EventType.CHATTY_AI_AGENT_IN_CHAT_DECISION_COMPLETED, EventType.CHATTY_AI_AGENT_IN_CHAT_ERROR_CALL_FAILED, EventType.CHATTY_AI_AGENT_IN_CHAT_ERROR_CALL_CANCELLED)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    message: str = Field(description="Human-readable message describing the event")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional event-specific data")

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

class HumanInterventionReason(StrEnum):
    """
    Reason for human intervention
    """
    SUGGESTED_MESSAGES = "suggested_messages"
    CONTROL_TRIGGER = "control_trigger"
    SOMETHING_WENT_WRONG = "something_went_wrong"


class HumanIntervention(BaseModel):
    """
    Reason for human intervention
    """
    reason: HumanInterventionReason = Field(description="The reason for human intervention")
    message: Optional[str] = Field(default=None, description="The message to display to the user if any")

class ChattyAIAgentInChat(CompanyAssetModel):
    """
    Standalone AI agent state for a chat, stored in dedicated collection.

    This replaces the embedded ChattyAIAgentAssignedToChat in Chat documents,
    allowing Lambda to manage AI agent state independently.

    Inherits from CompanyAssetModel for consistency with other company assets:
    - id, company_id, created_at, updated_at, deleted_at
    - Standard serialization methods
    - Preview functionality
    """
    # Core identifiers (company_id comes from CompanyAssetModel)
    chat_id: StrObjectId = Field(frozen=True, description="The chat this AI agent state belongs to")
    asset_id: StrObjectId = Field(frozen=True, description="The AI agent asset ID")
    name: str = Field(default="AI Agent State", description="Name for asset compatibility")

    # State fields (from ChattyAIAgentAssignedToChat)
    mode: ChattyAIMode = Field(default=ChattyAIMode.OFF)
    human_intervention: Optional[HumanIntervention] = Field(default=None, description="The reason for human intervention if any")
    is_processing: bool = Field(default=False)
    # Call tracking
    last_call_started_at: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the get chat with prompt (the moment n8n started processing the call)"
    )
    trigger_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the trigger that started the call"
    )
    last_call_cot_id: Optional[StrObjectId] = Field(default=None)
    trigger: Optional[ChainOfThoughtInChatTrigger] = Field(
        default=None,
        description="The trigger that started the call"
    )
    incoming_message_id_trigger: Optional[str] = Field(
        default=None,
        description="If the trigger is a user message, this will be the id of the incoming message"
    )

    # Assignment metadata
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    assigned_by: StrObjectId

    # Embedded chain of thoughts (deprecates separate chain_of_thoughts_in_chats collection)
    chain_of_thoughts: List[ChainOfThoughtInChat] = Field(
        default_factory=list,
        description="List of chain of thoughts for this AI agent in this chat. Embedded to avoid separate collection queries."
    )
    events: List[SimplifiedExecutionEvent] = Field(default_factory=list, description="Simplified events for UI visibility")

    # Preview class
    preview_class: ClassVar[type[ChattyAssetPreview]] = ChattyAssetPreview

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

    @property
    def requires_human_intervention(self) -> bool:
        """Check if the AI agent requires human intervention"""
        return self.human_intervention is not None

    @field_validator('last_call_started_at', 'trigger_timestamp', 'assigned_at', mode="after")
    @classmethod
    def ensure_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        return v.replace(tzinfo=ZoneInfo("UTC")) if v.tzinfo is None else v.astimezone(ZoneInfo("UTC"))

    # State management methods (from ChattyAIAgentAssignedToChat)
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

    def new_incoming_message_trigger(self, trigger_timestamp: datetime, incoming_message_id: str) -> None:
        """Set state when a new incoming message triggers the AI agent"""
        if self.is_processing:
            self.end_call()
        self.is_processing = True
        self.trigger = ChainOfThoughtInChatTrigger.USER_MESSAGE
        self.incoming_message_id_trigger = incoming_message_id
        self.trigger_timestamp = trigger_timestamp
        self.updated_at = datetime.now(ZoneInfo("UTC"))

    def new_call(self, cot_id: StrObjectId, trigger: ChainOfThoughtInChatTrigger) -> Optional[StrObjectId]:
        """Start a new AI agent call"""
        logger.debug(f"Starting a new call for chat {self.chat_id} | ai agent {self.asset_id} | cot id {cot_id} | trigger {trigger}")
        if trigger != ChainOfThoughtInChatTrigger.USER_MESSAGE:
            self.incoming_message_id_trigger = None
        last_call_cot_id = self.last_call_cot_id
        self.is_processing = True
        self.last_call_started_at = datetime.now(ZoneInfo("UTC"))
        self.last_call_cot_id = cot_id
        self.trigger = trigger
        self.updated_at = datetime.now(ZoneInfo("UTC"))
        return last_call_cot_id

    def is_call_valid(self, cot_id: StrObjectId) -> bool:
        """Check if a call with the given COT ID is valid"""
        return self.last_call_cot_id == cot_id and self.is_processing

    def manual_trigger(self) -> None:
        """Trigger AI agent manually"""
        self.is_processing = True
        self.trigger = ChainOfThoughtInChatTrigger.MANUAL_TRIGGER
        self.trigger_timestamp = datetime.now(ZoneInfo("UTC"))
        self.updated_at = datetime.now(ZoneInfo("UTC"))
        logger.debug(f"Starting a manual trigger for chat {self.chat_id} | ai agent {self.asset_id} | cot id ")

    def end_call(self) -> Optional[StrObjectId]:
        """End the current AI agent call"""
        logger.debug(f"Ending a call for chat {self.chat_id} | ai agent {self.asset_id}")
        if not self.is_processing:
            raise ValueError(f"Chatty AI Agent is not processing, so it can't be ended")
        self.incoming_message_id_trigger = None
        cot_id = self.last_call_cot_id
        self.is_processing = False
        self.last_call_started_at = None
        self.last_call_cot_id = None
        self.trigger = None
        self.trigger_timestamp = None
        self.updated_at = datetime.now(ZoneInfo("UTC"))
        logger.debug(f"Ended a call for chat {self.chat_id} | ai agent {self.asset_id} | cot id {cot_id}")
        return cot_id

    @property
    def is_call_in_progress(self) -> bool:
        """Check if a call is currently in progress"""
        return self.is_processing and self.last_call_started_at is not None and self.last_call_cot_id is not None

    @property
    def is_waiting_for_call_to_start_after_incoming_message(self) -> bool:
        """Check if waiting for call to start after incoming message"""
        return self.is_processing and self.trigger == ChainOfThoughtInChatTrigger.USER_MESSAGE and self.trigger_timestamp is not None

    @property
    def is_waiting_for_call_after_manual_trigger(self) -> bool:
        """Check if waiting for call after manual trigger"""
        return self.is_processing and self.trigger == ChainOfThoughtInChatTrigger.MANUAL_TRIGGER and self.trigger_timestamp is not None

    @property
    def current_call_cot_id(self) -> StrObjectId:
        """Get the current call COT ID"""
        if not self.last_call_cot_id:
            raise ValueError(f"Chatty AI Agent is not processing, so it doesn't have a current call cot id")
        return self.last_call_cot_id

    def re_run_call(self, cot_id: StrObjectId) -> Optional[StrObjectId]:
        """Re-run an existing call"""
        if not self.is_call_in_progress:
            if not self.is_waiting_for_call_to_start_after_incoming_message:
                raise ValueError(f"Chatty AI Agent is not processing, so it can't be re-run")
            else:
                logger.debug(f"Chatty AI Agent is still waiting for the n8n call to start after an incoming message")
        cot_id_to_cancel = self.end_call()
        self.new_call(cot_id=cot_id, trigger=ChainOfThoughtInChatTrigger.RETRY_CALL)
        return cot_id_to_cancel

    def escalate(self, reason: HumanInterventionReason, message: Optional[str] = None) -> None:
        """Mark as requiring human intervention"""
        self.human_intervention = HumanIntervention(reason=reason, message=message)
        self.updated_at = datetime.now(ZoneInfo("UTC"))

    def unescalate(self) -> None:
        """Remove requirement for human intervention"""
        self.human_intervention = None
        self.updated_at = datetime.now(ZoneInfo("UTC"))
    # Chain of thoughts management methods

    def get_chain_of_thought(self, cot_id: StrObjectId) -> Optional[ChainOfThoughtInChat]:
        """Get a chain of thought by ID from the embedded list"""
        for cot in self.chain_of_thoughts:
            if cot.id == cot_id:
                return cot
        return None

    def add_chain_of_thought(self, cot: ChainOfThoughtInChat) -> None:
        """Add a chain of thought to the embedded list"""
        # Verify it belongs to this chat and AI agent
        if cot.chat_id != self.chat_id:
            raise ValueError(f"Chain of thought chat_id {cot.chat_id} does not match AI agent chat_id {self.chat_id}")
        if cot.chatty_ai_agent_id != self.asset_id:
            raise ValueError(f"Chain of thought ai_agent_id {cot.chatty_ai_agent_id} does not match AI agent asset_id {self.asset_id}")

        # Check if COT with same ID already exists
        existing_cot = self.get_chain_of_thought(cot.id)
        if existing_cot:
            # Update existing COT
            index = self.chain_of_thoughts.index(existing_cot)
            self.chain_of_thoughts[index] = cot
        else:
            # Add new COT
            self.chain_of_thoughts.append(cot)

        self.updated_at = datetime.now(ZoneInfo("UTC"))

    def get_current_chain_of_thought(self) -> Optional[ChainOfThoughtInChat]:
        """Get the current active chain of thought (if processing)"""
        if not self.last_call_cot_id:
            return None
        return self.get_chain_of_thought(self.last_call_cot_id)

    def get_all_chain_of_thoughts(self) -> List[ChainOfThoughtInChat]:
        """Get all chain of thoughts, sorted by created_at (newest first)"""
        return sorted(self.chain_of_thoughts, key=lambda cot: cot.created_at, reverse=True)

