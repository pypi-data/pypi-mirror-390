# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

import requests as req
from igrafx_mining_sdk.project import Project
from igrafx_mining_sdk.api_connector import APIConnector


class Workgroup:
    """A iGrafx P360 Live Mining workgroup, which is used to log in and access projects"""

    def __init__(self, w_id: str, w_key: str, apiurl: str, authurl: str, jdbc_url: str = None, ssl_verify=True):
        """ Creates a iGrafx P360 Live Mining Workgroup and automatically logs into the iMining Public API using
        the provided client id and secret key

        :param w_id: the workgroup ID, which can be found in iGrafx P360 Live Mining
        :param w_key: the workgroup's secret key, used for authentication, also found in iGrafx P360 Live Mining
        :param apiurl: the URL of the api found in iGrafx P360 Live Mining
        :param authurl: the URL of the authentication found in iGrafx P360 Live Mining
        :param jdbc_url: the URL of the jdbc found in iGrafx P360 Live Mining
        :param ssl_verify: verify SSL certificates
        """
        self.w_id = w_id
        self.w_key = w_key
        self._datasources = []
        self.api_connector = APIConnector(w_id, w_key, apiurl, authurl, jdbc_url, ssl_verify)

    def get_project_list(self):
        """Returns a list of all projects in the workgroup"""
        response_project_list = self.api_connector.get_request("/projects").json()
        return response_project_list

    def get_app_version(self):
        """Returns the version of the app"""
        return self.api_connector.get_request("/version").json()

    def create_project(self, project_name: str, description: str = None):
        """Creates a project within the workgroup

        :param project_name: The name of the project
        :param description: The description of the project
        """

        params = {"name": project_name, "workgroupId": self.w_id}
        if description is not None:
            params["description"] = description

        route = "/project"
        response_project_creation = self.api_connector.post_request(route, params=params)

        if response_project_creation.status_code == 201:
            created_project = Project(response_project_creation.json()["message"], self.api_connector)
            return created_project
        else:
            raise ValueError(f"Failed to create project. Status code: {response_project_creation.status_code}")

    @property
    def get_workgroup_metadata(self):
        """
        Returns the metadata of the workgroup such as creation date, name, start validity date, isDemoWorkgroup
        """
        response_workgroup_metadata = self.api_connector.get_request(f"/workgroups/{self.w_id}")
        return response_workgroup_metadata.json()

    @property
    def get_workgroup_data_version(self):
        """
        Returns the data version of the workgroup
        """
        return self.get_workgroup_metadata.get("dataVersion")

    @property
    def datasources(self):
        """Requests and returns the list of datasources associated with the workgroup"""
        try:
            self._datasources = []
            for p_id in self.get_project_list():
                project = self.project_from_id(p_id)
                if project:
                    self._datasources.append(project.nodes_datasource)
                    self._datasources.append(project.edges_datasource)
                    self._datasources.append(project.cases_datasource)

        except req.HTTPError as error:
            print(f"HTTP Error occurred: {error}")

        return self._datasources

    def project_from_id(self, pid):
        """Returns a project based on its id, or None if no such project exists

        :param pid: The id of the project"""
        p = Project(pid, self.api_connector)
        return p if p.exists else None
