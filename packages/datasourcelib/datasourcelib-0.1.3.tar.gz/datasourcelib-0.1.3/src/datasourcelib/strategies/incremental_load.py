from datetime import datetime
from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger

logger = get_logger(__name__)

class IncrementalLoadStrategy(SyncBase):
    """Incremental load using last_sync timestamp or cursor."""

    def validate(self) -> bool:
        # require source to support incremental field or cursor
        if "cursor_field" not in self.source_config and "last_sync" not in self.source_config:
            logger.error("IncrementalLoadStrategy missing cursor_field or last_sync in source_config")
            return False
        return True

    def sync(self, last_sync: str = None, **kwargs) -> bool:
        try:
            last = last_sync or self.source_config.get("last_sync")
            logger.info("Running incremental load since %s", last)
            # TODO: fetch delta rows since 'last' and upsert to vector DB
            # After successful run store new last_sync timestamp
            logger.info("Incremental load completed")
            return True
        except Exception:
            logger.exception("IncrementalLoadStrategy.sync failed")
            return False