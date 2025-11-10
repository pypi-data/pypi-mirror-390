"""
Contains UW AdSEL Azure Merge DAO implementations.
"""
from restclients_core.dao import DAO
from os.path import abspath, dirname
import os
import json


class ADSEL_AZURE_MERGE_DAO(DAO):
    def service_name(self):
        return 'adsel_azure_merge'

    def service_mock_paths(self):
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path

    def get_with_body(self, url, body, headers={}):
        body = json.dumps(body).encode('utf-8')
        return self._load_resource("GET", url, headers, body)
