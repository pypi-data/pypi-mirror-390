from datetime import datetime
from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger

logger = get_logger(__name__)

class TimeRangeLoadStrategy(SyncBase):
    """Load records between a start and end timestamp."""

    def validate(self) -> bool:
        # rely on params at runtime; minimal validation OK
        return True

    def sync(self, start: str = None, end: str = None, **kwargs) -> bool:
        try:
            if not start or not end:
                logger.error("TimeRangeLoadStrategy requires 'start' and 'end'")
                return False
            logger.info("Time range load between %s and %s", start, end)
            # TODO: query source for timeframe and upsert
            return True
        except Exception:
            logger.exception("TimeRangeLoadStrategy.sync failed")
            return False