from typing import Any, Dict, List, Optional
from datasourcelib.datasources.datasource_base import DataSourceBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.utils.validators import require_keys
import os
import pyodbc


logger = get_logger(__name__)

class SQLDataSource(DataSourceBase):
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._conn = None
        self._is_sqlite = False

    def validate_config(self) -> bool:
        try:
            require_keys(self.config, ["sql_server","sql_database","sql_username","sql_password","sql_is_onprem"])
            return True
        except Exception as ex:
            logger.error("SQLDataSource.validate_config: %s", ex)
            return False

    def connect(self) -> bool:
        try:
            sql_server = self.config.get("sql_server", "")
            sql_database = self.config.get("sql_database", "")
            sql_username = self.config.get("sql_username", "")
            sql_password = self.config.get("sql_password", "")
            sql_is_onprem = self.config.get("sql_is_onprem", False)
            
            # Get available driver
            sql_driver = self._get_available_driver()
            
            # Build connection string with appropriate encryption settings
            conn_params = [
                f'DRIVER={sql_driver}',
                f'SERVER={sql_server}',
                f'DATABASE={sql_database}',
                f'UID={sql_username}',
                f'PWD={sql_password}'
            ]
            
            # Add encryption settings based on environment
            if not sql_is_onprem:
                conn_params.extend([
                    'Encrypt=yes',
                    'TrustServerCertificate=no'
                ])
            else:
                conn_params.extend([
                    'Encrypt=optional',
                    'TrustServerCertificate=yes'
                ])

            conn_str = ';'.join(conn_params)
            
            # Attempt connection with timeout
            self._conn = pyodbc.connect(conn_str, timeout=30)
            self._connected = True
            logger.info("SQLDataSource connected to %s using driver %s", sql_server, sql_driver)
            return True
            
        except pyodbc.Error as ex:
            logger.error("SQLDataSource.connect failed - ODBC Error: %s", ex)
            self._connected = False
            return False
        except Exception as ex:
            logger.error("SQLDataSource.connect failed - Unexpected Error: %s", ex)
            self._connected = False
            return False

    def disconnect(self) -> None:
        try:
            if self._conn:
                self._conn.close()
        finally:
            self._conn = None
            self._connected = False
            logger.info("SQLDataSource disconnected")

    def fetch_data(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self._connected:
                    ok = self.connect()
                    if not ok:
                        raise RuntimeError("SQLDataSource: not connected and cannot connect")

                query = self.config.get("sql_query")
                if not query:
                    raise ValueError("SQLDataSource.fetch_data requires a query")

                cur = self._conn.cursor()
                try:
                    cur.execute(query)
                    cols = [d[0] if hasattr(d, "__len__") else d[0] for d in (cur.description or [])]
                    rows = cur.fetchall()
                    results: List[Dict[str, Any]] = []
                    for r in rows:
                        results.append({cols[i]: r[i] for i in range(len(cols))})
                    return results
                finally:
                    try:
                        cur.close()
                    except Exception:
                        pass
                        
            except pyodbc.OperationalError as ex:
                # Handle connection lost
                retry_count += 1
                logger.warning("Connection lost, attempt %d of %d: %s", retry_count, max_retries, ex)
                self.disconnect()
                if retry_count >= max_retries:
                    raise
            except Exception as ex:
                logger.error("Query execution failed: %s", ex)
                raise

    def _get_available_driver(self) -> str:
        """Get first available SQL Server driver from preferred list."""
        preferred_drivers = [
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 17 for SQL Server',
            'SQL Server Native Client 11.0',
            'SQL Server'
        ]
        
        try:
            available_drivers = pyodbc.drivers()
            for driver in preferred_drivers:
                if driver in available_drivers:
                    return driver
            raise RuntimeError(f"No suitable SQL Server driver found. Available drivers: {available_drivers}")
        except Exception as ex:
            logger.error("Failed to get SQL drivers: %s", ex)
            raise