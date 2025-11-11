# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

import importlib.resources
import requests as req


class InvalidRouteError(Exception):
    """Raised when Login failed after a number of try to log in"""
    def __init__(self, message="Unauthorized to use this route"):
        self.message = message
        super().__init__(self.message)


class APIConnector:
    """Class to connect to the API. It allows us to log into the Mining Public API and retrieve a token.
    It also allows us to do HTTP GET, POST and DELETE requests."""
    def __init__(self, wg_id: str, wg_key: str, apiurl: str, authurl: str, jdbc_url: str, ssl_verify: bool):
        """Initializes the APIConnector class.

        :param wg_id: The ID of the workgroup
        :param wg_key: The secret key of the workgroup
        :param apiurl: The URL of the API
        :param authurl: The URL of the authentication
        :param jdbc_url: The URL of the JDBC connection
        :param ssl_verify: Verify SSL certificates
        """

        self.wg_id = wg_id
        self.wg_key = wg_key
        self.apiurl = self.__process_apiurl(self.__remove_slash(apiurl))
        self._authurl = self.__remove_slash(authurl)
        self.jdbc_url = jdbc_url
        self.jdbc_driver_class = "org.apache.calcite.avatica.remote.Driver"
        self.jdbc_driver_path = str(importlib.resources.files("igrafx_mining_sdk") / "jars" / "avatica-1.26.0.jar")
        self.ssl_verify = ssl_verify
        self.token_header = self.__login()

    def __process_apiurl(self, apiurl):
        """Ensure that the API URL ends with  /pub

        :param apiurl: The URL of the API
        """
        return apiurl if apiurl.endswith("/pub") else apiurl + "/pub"

    def __remove_slash(self, url):
        """Ensure that any URL ending with  / are correctly managed and remove / if needed

        :param url: The URL to analyse
        """
        return url.strip().rstrip('/')

    def __login(self):
        """Logs into the Mining Public API with the Workgroups credentials and retrieves a token for later requests.
        Handles the authentication ``/protocol/openid-connect/token`` suffix.
        """

        login_url = f"{self._authurl}"
        login_data = {
            "grant_type": "client_credentials",
            "client_id": self.wg_id,
            "client_secret": self.wg_key
        }

        try:
            response = req.post(login_url, login_data, verify=self.ssl_verify)
            response.raise_for_status()
            return {"Authorization": "Bearer " + response.json()["access_token"]}

        except req.exceptions.HTTPError as error:
            print(f"HTTP Error occurred: {error}")
            if error.response.reason == 'Bad Request':
                raise Exception("Invalid login credentials. \n\nTo check your credentials,"
                                "please go to the Process Explorer 360.\n"
                                "When on the platform, go to the workgroup settings and on the Open API tab and "
                                "check that the correct credentials have been entered.\n\n"
                                "There, you can find your workgroups ID and secret key "
                                "and the API and authentication url.")

    def get_request(self, route, *, params=None, nblasttries=0, maxtries=3):
        """Does an HTTP GET request to the Mining Public API by simply taking the route and eventual parameters

        :param route: The route of the request
        :param params: The parameters of the request
        :param nblasttries: The number of try of this route
        :param maxtries: The maximum number of try
        """

        response = None
        _route = self.apiurl + (route if route.startswith('/') else '/' + route)
        try:
            response = req.get(_route,
                               params=params,
                               headers=self.token_header,
                               verify=self.ssl_verify)
            if response.status_code == 401:  # Only possible if the token has expired
                if nblasttries < maxtries:
                    self.token_header = self.__login()
                    self.get_request(route, params=params, nblasttries=nblasttries + 1, maxtries=maxtries)
                else:
                    raise InvalidRouteError()
            response.raise_for_status()
        except (req.HTTPError, InvalidRouteError) as error:
            print(f"Http error occurred: {error}")
            print(response.text)
        return response

    def post_request(self, route, *, params=None, json=None, files=None, headers={}, nblasttries=0, maxtries=3):
        """Does an HTTP POST request to the Mining Public API by simply taking the route, an eventual JSON,
        files and headers

        :param route: The route of the request
        :param params: The parameters of the request
        :param json: A given JSON object
        :param files: Eventual files
        :param headers: Additional headers
        :param nblasttries: The number of try of this route
        :param maxtries: The maximum number of tries
        """

        response = None
        _route = self.apiurl + (route if route.startswith('/') else '/' + route)
        try:
            response = req.post(_route,
                                params=params,
                                json=json,
                                files=files,
                                headers={**self.token_header, **headers},
                                verify=self.ssl_verify)
            if response.status_code == 401:  # Only possible if the token has expired
                if nblasttries < maxtries:
                    self.token_header = self.__login()
                    self.post_request(route,
                                      json=json,
                                      files=files,
                                      headers=headers,
                                      nblasttries=nblasttries + 1,
                                      maxtries=maxtries)
                else:
                    raise InvalidRouteError()
            response.raise_for_status()
        except (req.HTTPError, InvalidRouteError) as error:
            if response is not None:
                print(f"Http error occurred: {error}")
                print(response.text)
        return response

    def delete_request(self, route, *, nblasttries=0, maxtries=3):
        """Does an HTTP DELETE request to the Mining Public API by simply taking the route

        :param route: The route of the request
        :param nblasttries: The number of try of this route
        :param maxtries: The maximum number of tries
        """

        response = None
        _route = self.apiurl + (route if route.startswith('/') else '/' + route)
        try:
            response = req.delete(_route,
                                  headers=self.token_header,
                                  verify=self.ssl_verify)
            if response.status_code == 401:  # Only possible if the token has expired
                if nblasttries < maxtries:
                    self.token_header = self.__login()
                    self.delete_request(route, nblasttries=nblasttries + 1, maxtries=maxtries)
                else:
                    raise InvalidRouteError()
            response.raise_for_status()
        except (req.HTTPError, InvalidRouteError) as error:
            print(f"Http error occurred: {error}")
            print(response.text)
        return response

    def put_request(self, route, *, params=None, nblasttries=0, maxtries=3):
        """Does an HTTP PUT request to the Mining Public API by simply taking the route

        :param route: The route of the request
        :param params: The parameters of the request
        :param nblasttries: The number of try of this route
        :param maxtries: The maximum number of tries
        """

        response = None
        _route = self.apiurl + (route if route.startswith('/') else '/' + route)
        try:
            response = req.put(_route,
                               params=params,
                               headers=self.token_header,
                               verify=self.ssl_verify)
            if response.status_code == 401:  # Only possible if the token has expired
                if nblasttries < maxtries:
                    self.token_header = self.__login()
                    self.put_request(route, params=params, nblasttries=nblasttries + 1, maxtries=maxtries)
                else:
                    raise InvalidRouteError()
            response.raise_for_status()
        except (req.HTTPError, InvalidRouteError) as error:
            print(f"Http error occurred: {error}")
            print(response.text)
        return response
