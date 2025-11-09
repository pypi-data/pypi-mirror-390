"""
Chatty AI Agent In Chat - Standalone model for AI agent state in chats

This is a standalone version of ChattyAIAgentAssignedToChat that lives in its own collection
rather than being embedded in the Chat document. This allows Lambda to manage AI agent state
independently without loading entire chat documents.
"""

from pydantic import Field, field_validator, ConfigDict
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, ClassVar
from ...base_models.chatty_asset_model import CompanyAssetModel, ChattyAssetPreview
from ...utils.types.identifier import StrObjectId
from .chain_of_thought_in_chat import ChainOfThoughtInChatTrigger
from .chatty_ai_mode import ChattyAIMode
import logging

logger = logging.getLogger(__name__)


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
    requires_human_intervention: bool = Field(default=False)
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

    # Preview class
    preview_class: ClassVar[type[ChattyAssetPreview]] = ChattyAssetPreview

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True
    )

    @field_validator('last_call_started_at', 'trigger_timestamp', 'assigned_at', mode="after")
    @classmethod
    def ensure_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        return v.replace(tzinfo=ZoneInfo("UTC")) if v.tzinfo is None else v.astimezone(ZoneInfo("UTC"))

    # State management methods (from ChattyAIAgentAssignedToChat)

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

    def manual_trigger(self, cot_id: StrObjectId) -> None:
        """Trigger AI agent manually"""
        self.is_processing = True
        self.trigger = ChainOfThoughtInChatTrigger.MANUAL_TRIGGER
        self.trigger_timestamp = datetime.now(ZoneInfo("UTC"))
        self.last_call_cot_id = cot_id
        self.updated_at = datetime.now(ZoneInfo("UTC"))
        logger.debug(f"Starting a manual trigger for chat {self.chat_id} | ai agent {self.asset_id} | cot id {cot_id}")

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

    def escalate(self) -> None:
        """Mark as requiring human intervention"""
        self.requires_human_intervention = True
        self.updated_at = datetime.now(ZoneInfo("UTC"))

    def unescalate(self) -> None:
        """Remove requirement for human intervention"""
        self.requires_human_intervention = False
        self.updated_at = datetime.now(ZoneInfo("UTC"))

