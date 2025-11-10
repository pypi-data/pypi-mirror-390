"""Chain Of Thought Service - Pre-configured AssetService for CRUD operations only"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from ..asset_service import AssetService, CacheConfig
from ..collections.chain_of_thought_collection import ChainOfThoughtCollection
from ....models.company.assets.ai_agents_v2.chain_of_thought_in_chat import ChainOfThoughtInChat
from ....models.data_base.mongo_connection import MongoConnection
from ....models.utils.types.identifier import StrObjectId
from ....models.utils.types.serializer_type import SerializerType
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ChainOfThoughtService(AssetService[ChainOfThoughtInChat, ChainOfThoughtInChat]):
    """
    Pre-configured service for Chain Of Thought CRUD operations.

    For business logic operations (create for N8N, set as failed, etc.),
    use ChainOfThoughtsEditor instead.

    No events needed - this is execution state, not a business asset.
    """

    def __init__(
        self,
        connection: MongoConnection,
        cache_config: CacheConfig = CacheConfig(
            keep_items_always_in_memory=False,
            keep_previews_always_in_memory=False
        )
    ):
        collection = ChainOfThoughtCollection(connection)
        super().__init__(
            collection=collection,
            cache_config=cache_config
        )

    # CRUD Operations only

    def get_by_id(self, cot_id: StrObjectId) -> Optional[ChainOfThoughtInChat]:
        """Get a chain of thought by ID"""
        cot_doc = self.collection.collection.find_one({"_id": ObjectId(cot_id)})
        if not cot_doc:
            return None
        return ChainOfThoughtInChat(**cot_doc)

    def create(self, chain_of_thought: ChainOfThoughtInChat) -> ChainOfThoughtInChat:
        """Create a new chain of thought"""
        cot_dict = chain_of_thought.model_dump_json(serializer=SerializerType.DATABASE)
        result = self.collection.collection.insert_one(cot_dict)
        if not result.inserted_id:
            raise Exception(f"Failed to create chain of thought with id {chain_of_thought.id}")
        return chain_of_thought

    def update(self, chain_of_thought: ChainOfThoughtInChat) -> ChainOfThoughtInChat:
        """Update a chain of thought"""
        chain_of_thought.updated_at = datetime.now(ZoneInfo("UTC"))
        cot_dict = chain_of_thought.model_dump_json(serializer=SerializerType.DATABASE)
        result = self.collection.collection.update_one(
            {"_id": ObjectId(chain_of_thought.id)},
            {"$set": cot_dict}
        )
        if result.matched_count == 0:
            raise ValueError(f"Chain of thought with id {chain_of_thought.id} not found")
        return chain_of_thought

    def delete(self, cot_id: StrObjectId) -> None:
        """Delete a chain of thought"""
        result = self.collection.collection.delete_one({"_id": ObjectId(cot_id)})
        if result.deleted_count == 0:
            raise ValueError(f"Chain of thought with id {cot_id} not found")
