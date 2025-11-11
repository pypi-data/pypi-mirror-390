# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

import json
import networkx as nx


class Graph(nx.DiGraph):
    """A graph from a iGrafx P360 Live Mining project, created with the parent Project's ID,
    a list of nodes and a list of edges"""
    def __init__(self, project_id: str, nodes_list: list, edges_list: list):
        """Initializes a graph from a Mining project, created with the parent Project's ID

        :param project_id: the ID of the parent project
        :param nodes_list: the list of nodes
        :param edges_list: the list of edges
        """
        super().__init__()
        self.project_id = project_id
        self.graph['project_id'] = project_id
        self.add_nodes_from(nodes_list)
        self.add_edges_from(edges_list)

    @staticmethod
    def from_dict(project_id, jgraph):
        """Static method that creates a Graph based on the dictionary representation of the graph

        :param project_id: the ID of the project the graph is in
        :param jgraph: the dictionary we want to parse the graph from
        """
        nodes_list = [(item["id"], item) for item in jgraph["vertices"]]
        edges_list = [(item["source"], item["destination"], item) for item in jgraph["edges"]]
        return Graph(project_id, nodes_list, edges_list)

    @staticmethod
    def from_json(project_id, path):
        """Static method that creates a Graph based on the JSON returned by the iGrafx Mining Public API

        :param project_id: the ID of the project the graph is in
        :param path: the path to the JSON file we want to parse the graph from
        """
        with open(path, 'r') as f:
            jgraph = json.load(f)
        return Graph.from_dict(project_id, jgraph)


class GraphInstance(Graph):
    """A graph instance from a iGrafx P360 Live Mining project, created with the parent Project's ID,
    a list of vertex instances and a list of edge instances
    """
    def __init__(self, project_id: str, nodes_list: list, edges_list: list, rework_total: int, concurrency_rate: float):
        super().__init__(project_id, nodes_list, edges_list)
        self.rework_total = rework_total
        self.concurrency_rate = concurrency_rate

    @staticmethod
    def from_dict(project_id, jgraph):
        """Static method that creates a GraphInstance based on the dictionary representation of the graph instance

        :param project_id: the ID of the project the graph instance is in
        :param jgraph: the dictionary we want to parse the graph instance from
        """
        nodes_list = [(item["id"], item) for item in jgraph["vertexInstances"]]
        edges_list = [(item["source"]["id"], item["destination"]["id"]) for item in jgraph["edgeInstances"]]
        return GraphInstance(project_id, nodes_list, edges_list, jgraph["reworkTotal"], jgraph["concurrencyRate"])

    @staticmethod
    def from_json(project_id, path):
        """Static method that creates a GraphInstance based on the json representation returned by the iGrafx Mining API

        :param project_id: the ID of the project the graph is in
        :param path: the path to the JSON file we want to parse the graph from"""

        with open(path, 'r') as f:
            jgraph = json.load(f)
        return GraphInstance.from_dict(project_id, jgraph)
