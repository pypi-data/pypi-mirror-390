from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.indexes.azure_search_index import AzureSearchIndexer
logger = get_logger(__name__)

class FullLoadStrategy(SyncBase):
    """Full load: replace or reload entire source into vector DB."""

    def validate(self) -> bool:
        # Minimal validation: required keys exist
        dsok = self.data_source.validate_config()
        return dsok

    def sync(self, **kwargs) -> bool:
        try:
            logger.info("Running full data load")
            data = self.data_source.fetch_data(**kwargs)
            for key, value in kwargs.items():
                print(f"{key} = {value}")
            # Implement real extract -> transform -> load to vector DB
            # Example pseudocode:
            # vector_client.upsert_batch(self.vector_db_config, rows)
            # New: use AzureSearchIndexer to create index and upload documents if requested
            if isinstance(data, list) and data:                
                indexer = AzureSearchIndexer(self.vector_db_config or {})
                if not indexer.validate_config():
                    logger.error("Vector DB config invalid for Azure Search indexer")
                    return False
                ok = indexer.index(data)
                if not ok:
                    logger.error("Indexing data to Azure Search failed")
                    return False

            logger.info("Full data load finished successfully")
            return True
        except Exception:
            logger.exception("FullLoadStrategy.sync failed")
            return False