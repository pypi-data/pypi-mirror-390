from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger

logger = get_logger(__name__)

class OnDemandLoadStrategy(SyncBase):
    """On demand load triggered by user request (arbitrary params)."""

    def validate(self) -> bool:
        return True

    def sync(self, **kwargs) -> bool:
        try:
            logger.info("On-demand sync invoked with params: %s", kwargs)
            # Use kwargs to drive partial loads, filters, ids etc.
            return True
        except Exception:
            logger.exception("OnDemandLoadStrategy.sync failed")
            return False