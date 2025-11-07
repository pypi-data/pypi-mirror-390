from typing import List, Dict, Any, Optional
from datasourcelib.utils.logger import get_logger

logger = get_logger(__name__)

class AzureSearchIndexer:
    """
    Minimal Azure Cognitive Search indexer wrapper.
    Expects vector_db_config with:
      - service_endpoint: str
      - index_name: str
      - api_key: str
    Optional:
      - key_field: name of unique key in documents (default 'id')
    """

    def __init__(self, vector_db_config: Dict[str, Any]):
        self.config = vector_db_config or {}
        self._client = None
        self._index_client = None

    def validate_config(self) -> bool:
        required = ("aisearch_endpoint", "aisearch_index_name", "aisearch_api_key")
        missing = [k for k in required if k not in self.config]
        if missing:
            logger.error("AzureSearchIndexer.validate_config missing: %s", missing)
            return False
        return True
    
    def _ensure_sdk(self):
        try:
            from azure.core.credentials import AzureKeyCredential  # type: ignore
            from azure.search.documents import SearchClient  # type: ignore
            from azure.search.documents.indexes import SearchIndexClient  # type: ignore
            from azure.search.documents.indexes.models import (
                SearchIndex,
                SimpleField,
                SearchableField,
                SearchFieldDataType,
            )  # type: ignore
        except Exception as e:
            raise RuntimeError("azure-search-documents package is required: install azure-search-documents") from e

        return AzureKeyCredential, SearchClient, SearchIndexClient, SearchIndex, SimpleField, SearchableField, SearchFieldDataType
    
    def _infer_field_type(self, value) -> Any:
        """
        Map Python types to SearchFieldDataType
        """
        *_, SearchFieldDataType = self._ensure_sdk()
        if value is None:
            return SearchFieldDataType.String
        t = type(value)
        if t is str:
            return SearchFieldDataType.String
        if t is bool:
            return SearchFieldDataType.Boolean
        if t is int:
            return SearchFieldDataType.Int32
        if t is float:
            return SearchFieldDataType.Double
        # fallback to string
        return SearchFieldDataType.String

    def _build_fields(self, sample: Dict[str, Any], key_field: str):
        AzureKeyCredential, SearchClient, SearchIndexClient, SearchIndex, SimpleField, SearchableField, SearchFieldDataType = self._ensure_sdk()
        
        fields = []
        # ensure key field present
        if key_field not in sample:
            # we'll create a string key, uploader will populate unique ids
            fields.append(SimpleField(name=key_field, type=SearchFieldDataType.String, key=True))
        else:
            typ = self._infer_field_type(sample[key_field])
            fields.append(SimpleField(name=key_field, type=SearchFieldDataType.String, key=True))

        for k, v in sample.items():
            logger.info(f"================={k}============")
            if k == key_field:
                continue
            typ = self._infer_field_type(v)
            # for strings use SearchableField so full text queries work
            if typ == SearchFieldDataType.String:
                fields.append(SearchableField(name=k, type=SearchFieldDataType.String))
            else:
                fields.append(SimpleField(name=k, type=typ))
        return fields

    def create_index(self, sample: Dict[str, Any]) -> bool:
        try:
            AzureKeyCredential, SearchClient, SearchIndexClient, SearchIndex, SimpleField, SearchableField, SearchFieldDataType = self._ensure_sdk()
            endpoint = self.config["aisearch_endpoint"]
            api_key = self.config["aisearch_api_key"]
            index_name = self.config["aisearch_index_name"]
            key_field = self.config.get("key_field", "id")

            index_client = SearchIndexClient(endpoint, AzureKeyCredential(api_key))
            fields = self._build_fields(sample, key_field)
            logger.info("=================Creating Index============")
            index = SearchIndex(name=index_name, fields=fields)
            # create or update index
            index_client.create_or_update_index(index)
            logger.info("Azure Search index '%s' created/updated", index_name)
            return True
        except Exception as ex:
            logger.exception("AzureSearchIndexer.create_index failed")
            return False

    def upload_documents(self, docs: List[Dict[str, Any]]) -> bool:
        try:
            AzureKeyCredential, SearchClient, SearchIndexClient, SearchIndex, SimpleField, SearchableField, SearchFieldDataType = self._ensure_sdk()
            endpoint = self.config["aisearch_endpoint"]
            api_key = self.config["aisearch_api_key"]
            index_name = self.config["aisearch_index_name"]
            key_field = self.config.get("key_field", "id")

            # ensure each doc has key_field
            from uuid import uuid4
            for d in docs:
                if key_field not in d:
                    d[key_field] = str(uuid4())
            # ensure each doc has key_field is of string type
            for d in docs:
                if key_field in d:                    
                    typ = self._infer_field_type(d[key_field])
                    if typ != SearchFieldDataType.String:
                        d[key_field] = str(d[key_field])

            client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))
            logger.info("Uploading %d documents to index %s", len(docs), index_name)
            result = client.upload_documents(documents=docs)
            # Check results for failures
            failed = [r for r in result if not r.succeeded]
            if failed:
                logger.error("Some documents failed to upload: %s", failed)
                return False
            logger.info("Uploaded documents successfully")
            return True
        except Exception:
            logger.exception("AzureSearchIndexer.upload_documents failed")
            return False

    def index(self, rows: List[Dict[str, Any]]) -> bool:
        """
        High level: create index (based on first row) and upload all rows.
        """
        if not rows:
            logger.error("AzureSearchIndexer.index called with empty rows")
            return False
        try:
            if not self.validate_config():
                return False
            sample = rows[0]
            logger.info(f"================={sample}============")
            ok = self.create_index(sample)
            if not ok:
                return False
            ok2 = self.upload_documents(rows)
            return ok2
        except Exception:
            logger.exception("AzureSearchIndexer.index failed")
            return False