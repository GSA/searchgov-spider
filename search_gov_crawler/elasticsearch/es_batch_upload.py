import os
import asyncio
import logging
from elasticsearch import helpers
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from pythonjsonlogger.json import JsonFormatter
from urllib.parse import urlparse
from search_gov_crawler.search_gov_spiders.extensions.json_logging import LOG_FMT
from search_gov_crawler.elasticsearch.convert_html_i14y import convert_html

# Setup Logging
logging.basicConfig(level=os.environ.get("SCRAPY_LOG_LEVEL", "INFO"))
log = logging.getLogger("search_gov_crawler.es_batch_upload")

if not log.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(fmt=LOG_FMT))
    log.addHandler(handler)

class SearchGovElasticsearch:
    def __init__(self, batch_size: int = 50):
        self._current_batch = []
        self._batch_size = batch_size
        self._es_client = None
        self._env_es_hosts = os.environ.get("ELASTICSEARCH_HOSTS", "")
        self._env_es_index = os.environ.get("ELASTICSEARCH_INDEX", "")
        self._env_es_username = os.environ.get("ELASTICSEARCH_USERNAME", "")
        self._env_es_password = os.environ.get("ELASTICSEARCH_PASSWORD", "")
        self._executor = ThreadPoolExecutor(max_workers=5)  # Reuse one executor

    def add_to_batch(self, html_content: str, url: str, domain_name: str):
        """
        Add a document to the batch for Elasticsearch upload.
        """
        doc = convert_html(html_content=html_content, url=url, domain_name=domain_name)
        if doc:
            self._current_batch.append(doc)

            if len(self._current_batch) >= self._batch_size:
                self.batch_upload()
        else:
            log.warning(f"Did not create i14y document for URL: {url}")
    
    def batch_upload(self):
        """
        Initiates batch upload using asyncio.
        """
        if not self._current_batch:
            return

        current_batch_copy = self._current_batch.copy()
        self._current_batch = []

        loop = asyncio.get_running_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
        asyncio.ensure_future(self._batch_elasticsearch_upload(current_batch_copy, loop))

    def _parse_es_urls(self, url_string: str) -> List[Dict[str, Any]]:
        """
        Parse Elasticsearch hosts from a comma-separated string.
        """
        hosts = []
        for url in url_string.split(','):
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.hostname or not parsed.port:
                raise ValueError(f"Invalid Elasticsearch URL: {url}")
            
            hosts.append({"host": parsed.hostname, "port": parsed.port, "scheme": parsed.scheme})
        return hosts
    
    def _get_client(self):
        """
        Lazily initializes the Elasticsearch client.
        """
        if not self._es_client:
            self._es_client = Elasticsearch(
                hosts=self._parse_es_urls(self._env_es_hosts),
                http_auth=(self._env_es_username, self._env_es_password)
            )
            self._create_index_if_not_exists()
        return self._es_client

    def _create_index_if_not_exists(self):
        """
        Creates an index in Elasticsearch if it does not exist.
        """
        index_name = self._env_es_index
        try:
            es_client = self._get_client()
            if not es_client.indices.exists(index=index_name):
                index_settings = {
                    "settings": {
                        "index": {
                            "number_of_shards": 6,
                            "number_of_replicas": 1
                        }
                    },
                    "aliases": {
                        "production-i14y-documents-searchgov": {}
                    }
                }
                es_client.indices.create(index=index_name, body=index_settings)
                log.info(f"Index '{index_name}' created successfully.")
            else:
                log.info(f"Index '{index_name}' already exists.")
        except Exception as e:
            log.error(f"Error creating/checking index: {str(e)}", exc_info=True)

    def _create_actions(self, docs: List[Dict[Any, Any]]) -> List[Dict[str, Any]]:
        """
        Create actions for bulk upload from documents.
        """
        return [
            {
                "_index": self._env_es_index,
                "_id": doc.pop("_id", None),
                "_source": doc
            }
            for doc in docs
        ]

    async def _batch_elasticsearch_upload(self, docs: List[Dict[Any, Any]], loop):
        """
        Perform bulk upload asynchronously using ThreadPoolExecutor.
        """
        def _bulk_upload():
            try:
                actions = self._create_actions(docs)
                helpers.bulk(self._get_client(), actions)
            except Exception as e:
                log.error(f"Error in bulk upload: {str(e)}", exc_info=True)

        await loop.run_in_executor(self._executor, _bulk_upload)
