from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)

class DailyLoadStrategy(SyncBase):
    """Daily scheduled load (wraps incremental)."""

    def validate(self) -> bool:
        return True

    def sync(self, run_date: str = None, **kwargs) -> bool:
        try:
            run_date = run_date or datetime.utcnow().date().isoformat()
            logger.info("Starting daily load for %s", run_date)
            # Typically call incremental with last_sync = previous day midnight
            # TODO implement scheduling integration externally; the strategy here is idempotent
            return True
        except Exception:
            logger.exception("DailyLoadStrategy.sync failed")
            return False