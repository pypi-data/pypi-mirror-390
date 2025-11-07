from typing import Dict, Any
from datetime import datetime
from .sync_types import SyncType, SyncStatus 
from ..datasources.datasource_types import DataSourceType
from ..utils.logger import get_logger
from ..utils.exceptions import SyncStrategyNotFound, DataSourceNotFound

# Import data sources
from ..datasources.sql_source import SQLDataSource
from ..datasources.azure_devops_source import AzureDevOpsSource
from ..datasources.sharepoint_source import SharePointSource
from ..datasources.blob_source import BlobStorageSource

# concrete strategies
from datasourcelib.strategies.full_load import FullLoadStrategy
from datasourcelib.strategies.incremental_load import IncrementalLoadStrategy
from datasourcelib.strategies.timerange_load import TimeRangeLoadStrategy
from datasourcelib.strategies.daily_load import DailyLoadStrategy
from datasourcelib.strategies.ondemand_load import OnDemandLoadStrategy

logger = get_logger(__name__)

class SyncManager:
    """High-level manager to select and execute a sync strategy with data source."""

    _strategy_map = {
        SyncType.FULL: FullLoadStrategy,
        SyncType.INCREMENTAL: IncrementalLoadStrategy,
        SyncType.TIMERANGE: TimeRangeLoadStrategy,
        SyncType.DAILY: DailyLoadStrategy,
        SyncType.ONDEMAND: OnDemandLoadStrategy,
    }

    _datasource_map = {
        DataSourceType.SQL: SQLDataSource,
        DataSourceType.AZURE_DEVOPS: AzureDevOpsSource, 
        DataSourceType.SHAREPOINT: SharePointSource,
        DataSourceType.BLOB_STORAGE: BlobStorageSource
    }

    def execute_sync(self, sync_type: SyncType, 
                    source_type: DataSourceType,
                    source_config: Dict[str, Any],
                    vector_db_config: Dict[str, Any], 
                    **kwargs) -> Dict[str, Any]:
        start = datetime.utcnow()
        logger.info(f"Execute {sync_type} sync using {source_type} source")
        
        try:
            # Get data source class
            source_cls = self._datasource_map.get(source_type)
            if not source_cls:
                raise DataSourceNotFound(f"No source registered for {source_type}")

            # Initialize data source
            data_source = source_cls(source_config)
            if not data_source.validate_config():
                raise ValueError("Invalid data source configuration")

            # Get sync strategy
            strategy_cls = self._strategy_map.get(sync_type)
            if not strategy_cls:
                raise SyncStrategyNotFound(f"No strategy for {sync_type}")

            # Initialize strategy with data source
            strategy = strategy_cls(data_source=data_source, 
                                 vector_db_config=vector_db_config)

            if not strategy.validate():
                message = "Strategy validation failed"
                logger.error(message)
                return {
                    "status": SyncStatus.FAILED,
                    "message": message,
                    "started_at": start
                }

            # Execute sync
            success = strategy.sync(**kwargs)
            status = SyncStatus.SUCCESS if success else SyncStatus.FAILED
            
            return {
                "status": status,
                "message": f"{sync_type} completed" if success else f"{sync_type} failed",
                "started_at": start,
                "finished_at": datetime.utcnow()
            }

        except Exception as ex:
            logger.exception("SyncManager.execute_sync failed")
            return {
                "status": SyncStatus.FAILED, 
                "message": str(ex),
                "started_at": start,
                "finished_at": datetime.utcnow()
            }