# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
import json
import os
import random
import uuid
from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Union
from collections import OrderedDict
from igrafx_mining_sdk.graph import Graph, GraphInstance
from igrafx_mining_sdk.column_mapping import FileStructure, ColumnMapping
from igrafx_mining_sdk.datasource import Datasource
from igrafx_mining_sdk.api_connector import APIConnector


class Project:
    """A iGrafx P360 Live Mining project"""
    def __init__(self, pid: str, api_connector: APIConnector):
        """Create a iGrafx P360 Live Mining project from a project ID and the Workgroup it was created from

        :param pid: the Project's ID
        :param api_connector: the APIConnector object
        """
        self.id = pid
        self.api_connector = api_connector
        self._graph = None
        self._ds_response = None
        self._process_keys = []

    @property
    def exists(self):
        """Check if the project exists"""
        response_project_exist = self.api_connector.get_request(f"/project/{self.id}/exist").json()
        return response_project_exist["exists"]

    def delete_project(self):
        """Deletes the project"""
        response_project_delete = self.api_connector.delete_request(f"/project/{self.id}")
        return response_project_delete

    def get_project_name(self):
        """Returns the name of the project"""
        response_project_name = self.api_connector.get_request(f"/projects/{self.id}").json()
        return response_project_name["name"]

    def graph(self, gateways=False):
        """Performs a REST request for the project model graph if it hasn't already been retrieved.

        :param gateways: Boolean that controls whether the graph returned will be BPMN-like or not
        """
        if self._graph is None:
            params = {"mode": "gateways" if gateways else "simplified"}
            response_graph = self.api_connector.get_request(
                f"/project/{self.id}/graph",
                params=params)
            self._graph = Graph.from_dict(self.id, response_graph.json())
        return self._graph

    def get_graph_instances(self, limit=None, shuffle=False):
        """Returns all the project's Graph Instances, performing a REST request for any instances that don't already
        exist within the project.

        :param limit: the maximum number of graph instances to return
        :param shuffle: whether to shuffle the list of graph instances with a default value set to False
        """
        limit = min(limit, len(self.process_keys)) if limit is not None else len(self.process_keys)
        sample = random.sample(self.process_keys, limit) if shuffle else self.process_keys[:limit]
        return [self.graph_instance_from_key(k) for k in sample]

    def graph_instance_from_key(self, process_id):
        """Performs a REST request for the graph instance associated with a process key, and returns it.

        :param process_id: the id of the process whose graph we want to get
        """
        parameters = {"processId": process_id}
        response_graph_instance = None
        try:
            response_graph_instance = self.api_connector.get_request(
                f"/project/{self.id}/graphInstance",
                params=parameters)
            graph = response_graph_instance.json()
            graph_instance = GraphInstance.from_dict(self.id, graph)
        except Exception as error:
            print(f"Could not parse graph: {error}")
            print(response_graph_instance)
            return None
        return graph_instance

    def __datasource_request(self):
        """Request datasources associated with the project. It returns a name, type, host and port per datasource."""

        response_datasource = self.api_connector.get_request(f"/datasources/{self.id}")
        return response_datasource

    @property
    def nodes_datasource(self):
        """Returns datasource of type '_vertex'"""
        return self.__get_datasource_by_name('_vertex')

    @property
    def edges_datasource(self):
        """Returns datasource of type '_simplifiedEdge'"""
        return self.__get_datasource_by_name('_edge')

    @property
    def cases_datasource(self):
        """Returns datasource of type 'cases'"""
        return self.__get_datasource_by_name('cases')

    def __get_datasource_by_name(self, ds_type):
        """Helper method that filters the datasources based on the given type

        :param ds_type: The type of datasource. Can be 'cases', '_simplifiedEdge' or '_vertex'
        """
        if self._ds_response is None or self._ds_response.status_code == 404:
            self._ds_response = self.__datasource_request()

        if self._ds_response.status_code == 200:
            json_response = self._ds_response.json()
            for item in json_response:
                if "_edge" in item["name"]:
                    item["type"] = "_edge"
                elif "_vertex" in item["name"]:
                    item["type"] = "_vertex"
                else:
                    item["type"] = "cases"

            # Set the datasource NAME and TYPE
            response_filtered = [d for d in json_response if d['type'] == ds_type][0]
            return Datasource(
                response_filtered["name"],
                response_filtered["type"],
                self.api_connector)
        else:
            return None

    def get_project_lookups(self):
        """Returns available list of lookups for the project"""

        response_lookups = self.api_connector.get_request(f"/lookups/{self.id}").json()
        print(response_lookups)

        return response_lookups

    def get_project_variants(self, page_index: int, limit: int, search: str = None):
        """Returns the project variants

        :param page_index: the page index for pagination
        :param limit: The maximum number of items to return per page
        :param search: The search query to filter variants by name (optional)
        """
        params = {"projectId": self.id, "pageIndex": page_index, "limit": limit}
        if search is not None:
            params["search"] = search

        route = f"/project/{self.id}/variants"
        response_variants = self.api_connector.get_request(route, params=params)
        return response_variants.json()

    def get_project_completed_cases(self, page_index: int, limit: int, search_case_id: str = None):
        """Returns the projects completed cases

        :param page_index: the page index for pagination
        :param limit: The maximum number of items to return per page
        :param search_case_id: The search query to filter cases by ID (optional)

        """
        params = {"projectId": self.id, "pageIndex": page_index, "limit": limit}
        if search_case_id is not None:
            params["searchCaseId"] = search_case_id

        route = f"/project/{self.id}/completedCases"
        response_case_ids = self.api_connector.get_request(route, params=params)
        return response_case_ids.json()

    @property
    def process_keys(self):
        """Queries the datasources to find the different process keys of the project"""

        if len(self._process_keys) == 0:
            ds = self.edges_datasource
            res = ds.request(f"SELECT DISTINCT processkey FROM \"{ds.name}\"")
            self._process_keys = [key for key in res['processkey']]

        return self._process_keys

    def add_column_mapping(self, filestructure: FileStructure, columnmapping: ColumnMapping):
        """Create a column mapping for the project

        :param filestructure: The filestructure
        :param columnmapping: The column mapping
        """
        route = f"/project/{self.id}/column-mapping"
        json = {'fileStructure': filestructure.to_dict(), 'columnMapping': columnmapping.to_dict()}
        response_column_mapping = self.api_connector.post_request(route, json=json)
        return response_column_mapping.status_code == 204

    @property
    def column_mapping_exists(self):
        """Check if a column mapping exists"""

        json_response = self.api_connector.get_request(f"/project/{self.id}/column-mapping-exists")
        return json_response.json()['exists']

    def get_mapping_infos(self):
        """Returns the mapping infos of the project such as the column names"""

        response_mapping_infos = self.api_connector.get_request(f"/project/{self.id}/mappingInfos").json()
        return response_mapping_infos

    def get_column_mapping(self):
        """Returns the column mapping of the project"""

        if self.column_mapping_exists:
            response_column_mapping = self.api_connector.get_request(f"/project/{self.id}/column-mapping").json()

            column_mapping = {}
            for k, v in response_column_mapping.items():
                if isinstance(v, dict):
                    v['name'] = k
                    if k == 'caseId':
                        v['columnType'] = "CASE_ID"
                    elif k == 'activity':
                        v['columnType'] = "TASK_NAME"
                    elif k in ["dateColumn", "otherDateColumn"]:
                        v['columnType'] = "TIME"
                    else:
                        raise ValueError("Default columns should be of type 'caseId', 'activity', 'dateColumn' or "
                                         "'otherDateColumn'")
                    column_mapping['col' + str(v['columnIndex'])] = v
                elif isinstance(v, list):
                    for i, subdict in enumerate(v):
                        if k == 'dimensions':
                            subdict['columnType'] = "DIMENSION"
                        elif k == 'metrics':
                            subdict['columnType'] = "METRIC"
                        else:
                            raise ValueError("Nested lists should be of type 'dimensions' or 'metrics'")
                        column_mapping['col' + str(subdict['columnIndex'])] = subdict

            # Sort the column mapping by columnIndex value and cast to json
            column_mapping = OrderedDict(sorted(column_mapping.items(), key=lambda x: x[1]["columnIndex"]))
            return json.dumps(column_mapping)
        else:
            raise ValueError("Column mapping does not exist for this project.")

    def reset(self):
        """Makes an API call to manually reset a project"""

        response_reset = self.api_connector.post_request(f"/project/{self.id}/reset")
        return response_reset.status_code == 204

    def unarchive(self):
        """Makes an API call to manually unarchive a project"""

        response_unarchive = self.api_connector.put_request(f"/projects/{self.id}/unarchive")
        return response_unarchive.status_code == 204

    def add_file(self, path):
        """Adds a file to the project.
        A zip file can also be added. In the file structure,
        the declared file type should be the final format of the file within the zip (e.g., .csv, .xlsx, .xls).
        It returns the information of the added file such as the file ID, the name and status of the file.

        :param path: The path to the file to add
        """
        route = f"/project/{self.id}/file?teamId={self.api_connector.wg_id}"
        file_extension = os.path.splitext(path)[-1].lower()
        if file_extension == ".csv":
            mime_type = "text/csv"
        elif file_extension == ".xlsx":
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_extension == ".xls":
            mime_type = "application/vnd.ms-excel"
        elif file_extension == ".zip":
            # When a zip is added, the mime type is a zip file.
            # The file type is automatically detected through the file structure
            mime_type = "application/zip"
        else:
            raise ValueError(f"File extension {file_extension} is not supported")

        with open(path, 'rb') as file:
            files = {'file': (os.path.basename(path), file, mime_type)}
            headers = {"accept": "application/json, text/plain, */*"}
            response_add_file = self.api_connector.post_request(route, files=files, headers=headers)

        # print(response_add_file.status_code) to get the status response
        if response_add_file.status_code == 201:
            return response_add_file.json()
        else:
            raise Exception(f"Error adding file. Status code: {response_add_file.status_code}")

    def get_project_files_metadata(self, page_index: int, limit: int, sort_order: str = "ASC"):
        """Makes an API call to get the ingestion status of all files in a project

        :param page_index: The page index for pagination
        :param limit: The maximum number of items to return per page
        :param sort_order: The sort order (ASC or DESC)
        """
        params = {"pageIndex": page_index, "limit": limit, "sortOrder": sort_order}
        response_status = self.api_connector.get_request(f"/projects/{self.id}/files", params=params)
        return response_status.json()

    def get_file_metadata(self, file_id: str):
        """Makes an API call to get the metadata of a specific file from a file id in a project

        :param file_id: The ID of the file
        """
        response_status_file_id = self.api_connector.get_request(f"/projects/{self.id}/files/{file_id}").json()
        return response_status_file_id

    def get_file_ingestion_status(self, file_id: str):
        """Makes an API call to get the ingestion status of a specific file from a file id in a project

        :param file_id: The ID of the file
        """

        return self.get_file_metadata(file_id).get('status')
