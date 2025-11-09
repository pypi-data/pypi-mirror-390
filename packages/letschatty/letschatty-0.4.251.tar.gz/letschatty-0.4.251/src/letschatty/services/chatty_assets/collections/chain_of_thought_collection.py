"""Chain of Thought Collection - Pre-configured AssetCollection for Chain of Thoughts"""

from ..asset_service import AssetCollection
from ....models.company.assets.ai_agents_v2.chain_of_thought_in_chat import (
    ChainOfThoughtInChat,
    ChainOfThoughtInChatPreview
)
from ....models.data_base.mongo_connection import MongoConnection


class ChainOfThoughtCollection(AssetCollection[ChainOfThoughtInChat, ChainOfThoughtInChatPreview]):
    """Pre-configured collection for Chain of Thought"""

    def __init__(self, connection: MongoConnection):
        super().__init__(
            collection="chain_of_thoughts",
            asset_type=ChainOfThoughtInChat,
            connection=connection,
            create_instance_method=lambda doc: ChainOfThoughtInChat(**doc),
            preview_type=ChainOfThoughtInChatPreview
        )

