from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, List, Optional

from letschatty.models.base_models.ai_agent_component import AiAgentComponentType
from letschatty.models.utils.types.identifier import StrObjectId
from .lambda_invokation_types import InvokationType, LambdaAiEvent
from .expected_output import ExpectedOutputIncomingMessage, ExpectedOutputSmartTag, ExpectedOutputQualityTest, IncomingMessageAIDecision
from ...models.company.assets.ai_agents_v2.ai_agents_decision_output import IncomingMessageDecisionAction

class SmartTaggingCallbackMetadata(BaseModel):
    chat_id: StrObjectId
    company_id: StrObjectId

class ComparisonAnalysisCallbackMetadata(BaseModel):
    test_case_id: StrObjectId
    company_id : StrObjectId

class InteractionCallbackMetadata(BaseModel):
    test_case_id: StrObjectId
    chat_example_id: StrObjectId
    ai_agent_id: StrObjectId
    company_id: StrObjectId
    interaction_index: int

class IncomingMessageCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.INCOMING_MESSAGE_CALLBACK
    data: IncomingMessageAIDecision
    callback_metadata: Dict[str, Any] = Field(default_factory=dict)

class QualityTestCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SINGLE_QUALITY_TEST_CALLBACK
    data: ExpectedOutputQualityTest
    callback_metadata: ComparisonAnalysisCallbackMetadata

class QualityTestInteractionCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.QUALITY_TEST_INTERACTION
    data: ExpectedOutputIncomingMessage
    callback_metadata: InteractionCallbackMetadata

    @model_validator(mode="before")
    def validate_data(cls, data):
        if isinstance(data, dict) and "data" in data and "callback_metadata" in data and "chain_of_thought" in data["data"]:
            data["data"]["chain_of_thought"]["chatty_ai_agent_id"] = data["callback_metadata"]["ai_agent_id"]
        return data

class SmartTaggingCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SMART_TAGGING_CALLBACK
    data: ExpectedOutputSmartTag
    callback_metadata: SmartTaggingCallbackMetadata

    @model_validator(mode="before")
    def validate_data(cls, data):
        if isinstance(data, dict) and "data" in data and "chain_of_thought" in data["data"]:
                data["data"]["chain_of_thought"]["chatty_ai_agent_id"] = "000000000000000000000000"
        return data

class ChatData(BaseModel):
    chat_id: StrObjectId
    company_id: StrObjectId

class IncomingMessageEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.INCOMING_MESSAGE
    data: ChatData

class FollowUpEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.FOLLOW_UP
    data: ChatData

class QualityTestEventData(BaseModel):
    chat_example_id: StrObjectId
    company_id: StrObjectId
    ai_agent_id: StrObjectId

class QualityTestEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SINGLE_QUALITY_TEST
    data: QualityTestEventData

class AllQualityTestEventData(BaseModel):
    company_id: StrObjectId
    ai_agent_id: StrObjectId

class AllQualityTestEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.ALL_QUALITY_TEST
    data: AllQualityTestEventData

class SmartTaggingEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SMART_TAGGING
    data: ChatData

class SmartTaggingPromptEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.SMART_TAGGING_PROMPT
    data: ChatData

class QualityTestsForUpdatedAIComponentEventData(BaseModel):
    company_id: StrObjectId
    ai_component_id: StrObjectId
    ai_component_type: AiAgentComponentType

class QualityTestsForUpdatedAIComponentEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.QUALITY_TESTS_FOR_UPDATED_AI_COMPONENT
    data: QualityTestsForUpdatedAIComponentEventData

class FixBuggedAiAgentsCallsInChatsEventData(BaseModel):
    company_id: Optional[StrObjectId] = None

class FixBuggedAiAgentsCallsInChatsEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.FIX_BUGGED_AI_AGENTS_CALLS_IN_CHATS
    data: FixBuggedAiAgentsCallsInChatsEventData = Field(default_factory=FixBuggedAiAgentsCallsInChatsEventData)

class DoubleCheckerForIncomingMessagesAnswerData(BaseModel):
    incoming_message_output: ExpectedOutputIncomingMessage
    chat_id: StrObjectId
    company_id: StrObjectId
    ai_agent_id: StrObjectId
    incoming_messages_ids: List[str]

class DoubleCheckerCallbackMetadata(BaseModel):
    chat_id: StrObjectId
    company_id: StrObjectId
    ai_agent_id: StrObjectId
    incoming_messages_ids: List[str]

class DoubleCheckerForIncomingMessagesAnswerEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.DOUBLE_CHECKER_FOR_INCOMING_MESSAGES_ANSWER
    data: DoubleCheckerForIncomingMessagesAnswerData

class DoubleCheckerForIncomingMessagesAnswerCallbackEvent(LambdaAiEvent):
    type: InvokationType = InvokationType.DOUBLE_CHECKER_FOR_INCOMING_MESSAGES_ANSWER_CALLBACK
    data: DoubleCheckerForIncomingMessagesAnswerData
    callback_metadata: DoubleCheckerCallbackMetadata

class DoubleCheckerForIncomingMessagesAnswerCallbackMetadata(BaseModel):
    chat_id: StrObjectId
    company_id: StrObjectId
    ai_agent_id: StrObjectId
