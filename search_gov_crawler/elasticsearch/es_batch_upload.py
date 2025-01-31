import os
import asyncio
from elasticsearch import helpers
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from scrapy.spiders import Spider

from search_gov_crawler.elasticsearch.convert_html_i14y import convert_html

class SearchGovElasticsearch:
    def __init__(self, batch_size: int = 100):
        self._current_batch = []
        self._batch_size = batch_size
        self._es_client = None
        self._env_es_host = os.environ.get("ELASTICSEARCH_HOST")
        self._env_es_port = int(os.environ.get("ELASTICSEARCH_PORT", 9200))
        self._env_es_index = os.environ.get("ELASTICSEARCH_INDEX")
        self._env_es_username = os.environ.get("ELASTICSEARCH_USERNAME")
        self._env_es_password = os.environ.get("ELASTICSEARCH_PASSWORD")
    
    def add_to_batch(self, html_content: str, url: str, spider: Spider):
        domain_name = spider.name
        doc = convert_html(html_content=html_content, url=url, domain_name=domain_name)
        self._current_batch.append(doc)

        if len(self._current_batch) >= self._batch_size:
            current_batch_copy = self._current_batch.copy()
            self._current_batch = []
            self._batch_upload(current_batch_copy)

    def _get_client(self):
        if (not self._es_client):
            self._es_client = Elasticsearch(
                hosts=[{'host': self._env_es_host, 'port': self._env_es_port }],
                http_auth=(self._env_es_username, self._env_es_password)
            )

            self._create_index_if_not_exists()
        return self._es_client
    
    def _batch_upload(self, docs: List[Dict[str, Any]], spider: Spider):
        asyncio.run(self._batch_elasticsearch_upload(docs))
    
    def _create_index_if_not_exists(self, spider: Spider):
        index_name = self._env_es_index
        try:
            if not self._get_client().indices.exists(index=index_name):
                index_settings = {
                    "settings": {
                        "index": {
                            "number_of_shards": 5,
                            "number_of_replicas": 1
                        }
                    },
                    "aliases": {
                        "production-i14y-documents-searchgov": {}
                    }
                }

                self._get_client().indices.create(index=index_name, body=index_settings)
                spider.logger.info(f"Index '{index_name}' created successfully.")
            else:
                spider.logger.info(f"Index '{index_name}' already exists.")

        except Exception as e:
            spider.logger.error(f"Error creating/checking index: {e}")

    def _create_actions(self, docs: List[Dict[Any, Any]], index: str) -> List[Dict[str, Any]]:
        """
        Create actions for bulk upload from documents
        """
        actions = []
        for doc in docs:
            action = {
                '_index': index,
                '_id': doc.pop('_id', None),
                '_source': doc
            }
            actions.append(action)
        return actions

    async def _batch_elasticsearch_upload(self, docs: List[Dict[Any, Any]], spider: Spider) -> None:

        def _bulk_upload():
            actions = self._create_actions(docs)
            try:
                helpers.bulk(self._get_client(), actions)
            except Exception as e:
                spider.logger.error(f"Error in bulk upload: {str(e)}")
        

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            # Schedule the bulk upload in the background, like yield
            await loop.run_in_executor(pool, _bulk_upload)
