# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

from igrafx_mining_sdk.column_mapping import (FileType, FileStructure, ColumnMapping, MetricAggregation,
                                              DimensionAggregation)
from igrafx_mining_sdk.datasource import Datasource
from igrafx_mining_sdk.workgroup import Workgroup
from igrafx_mining_sdk.project import Project
from igrafx_mining_sdk.graph import Graph, GraphInstance

import toml
from pathlib import Path
import importlib


def extract_metadata():
    metadata = dict()
    try:
        root_dir = Path(__file__).parent.parent
        with open(
            root_dir / "pyproject.toml", encoding="utf-8"
        ) as f:
            pyproject_data = toml.load(f)
            metadata['author'] = pyproject_data['tool']['poetry']['authors'][0]
            metadata['email'] = "contact@igrafx.com"
            metadata['version'] = pyproject_data['tool']['poetry']['version']
    except (FileNotFoundError, StopIteration):
        metadata['author'] = importlib.metadata.metadata('igrafx_mining_sdk')['Author']
        metadata['email'] = importlib.metadata.metadata('igrafx_mining_sdk')['Author-email']
        metadata['version'] = importlib.metadata.metadata('igrafx_mining_sdk')['Version']
    return metadata


metadata = extract_metadata()
__author__ = metadata['author']
__email__ = metadata['email']
__version__ = metadata['version']
__doc__ = """
igrafx_mining_sdk
==================

Description
-----------
igrafx_mining_sdk is a Python package created by iGrafx.
The iGrafx P360 Live Mining SDK is an open source application that can be used to manage your mining projects.
This information will show up when using the help function.
"""
