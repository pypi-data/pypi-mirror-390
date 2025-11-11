"""Filter Criteria Collection - Pre-configured AssetCollection for Filter Criterias"""

from typing import List
from bson import ObjectId
from ..asset_service import AssetCollection
from ....models.company.assets.filter_criteria import FilterCriteria, FilterCriteriaPreview
from ....models.data_base.mongo_connection import MongoConnection
from ....models.utils.types.identifier import StrObjectId


class FilterCriteriaCollection(AssetCollection[FilterCriteria, FilterCriteriaPreview]):
    """Pre-configured collection for Filter Criteria assets"""

    def __init__(self, connection: MongoConnection):
        super().__init__(
            collection="filter_criterias",
            asset_type=FilterCriteria,
            connection=connection,
            create_instance_method=FilterCriteria.default_create_instance_method,
            preview_type=FilterCriteriaPreview
        )

    def get_by_ids(self, ids: List[StrObjectId]) -> List[FilterCriteria]:
        """
        Get multiple filter criteria by their IDs in a single query.

        Args:
            ids: List of filter criteria IDs

        Returns:
            List of FilterCriteria objects
        """
        if not ids:
            return []

        # Convert string IDs to ObjectIds
        object_ids = [ObjectId(id) for id in ids]

        # Query for all filter criteria with matching IDs
        query = {
            "_id": {"$in": object_ids},
            "deleted_at": None
        }

        # Use sync client to fetch documents
        docs = list(self.connection.sync_client[self.database][self.collection_name].find(query))

        # Create FilterCriteria instances
        return [self.create_instance(doc) for doc in docs]

