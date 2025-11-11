# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
import json
from enum import Enum
from typing import List, Union


class FileType(str, Enum):
    """Type of the file that can be added."""
    CSV = "csv"
    XLS = "xls"
    XLSX = "xlsx"


class FileStructure:
    """ A FileStructure used to create a column mapping"""

    def __init__(self, file_type: FileType, charset: str = "UTF-8", delimiter: str = ",", quote_char: str = '"',
                 escape_char: str = '\\',
                 eol_char: str = "\\r\\n", comment_char: str = "#", sheet_name: str = None,
                 header: bool = True):
        """ Creates a FileStructure used to create a column mapping

        :param file_type: the type of the file (CSV, XLS, XLSX)
        :param charset: the charset of the file (UTF-8, ...)
        :param delimiter: the delimiter of the file (';', ',', ...)
        :param quote_char: the character to quote field in the file ('\',...)
        :param escape_char: the character to escape('\\', ...)
        :param eol_char: the character for the end of line ('\\n')
        :param header: the character to comment ('#')
        :param comment_char: boolean to say if the file contains a header
        :param sheet_name: the name of the sheet in Excel file
        """

        self.file_type = file_type
        self.charset = charset
        self.delimiter = delimiter
        self.quote_char = quote_char
        self.escape_char = escape_char
        self.eol_char = eol_char
        self.header = header
        self.comment_char = comment_char
        self.sheet_name = sheet_name

    def to_dict(self):
        """Returns the JSON dictionary format of the FileStructure"""

        res = {
            'fileType': self.file_type.value,
            'charset': self.charset,
            'delimiter': self.delimiter,
            'quoteChar': self.quote_char,
            'escapeChar': self.escape_char,
            'eolChar': self.eol_char,
            'header': self.header,
            'commentChar': self.comment_char,
        }
        if self.sheet_name is not None:
            res['sheetName'] = self.sheet_name
        return res

    @classmethod
    def from_json(cls, json_str):
        """Convert JSON string to dictionary

        :param json_str: JSON string"""
        data = json.loads(json_str)

        # Extract files from json dictionary
        file_type = data.get('fileType')
        if file_type is None:
            raise KeyError('FileStructure JSON must contain a "fileType" field.')
        try:
            file_type = FileType[file_type]
        except Exception as e:
            valid_file_types = [x.name for x in FileType]
            raise KeyError(f'Invalid fileType, must be one of following: {", ".join(valid_file_types)}.') from e
        charset = data.get('charset', 'UTF-8')
        delimiter = data.get('delimiter', ',')
        quote_char = data.get('quoteChar', '"')
        escape_char = data.get('escapeChar', '\\')
        eol_char = data.get('eolChar', '\\r\\n')
        comment_char = data.get('commentChar', '#')
        sheet_name = data.get('sheetName')
        header = data.get('header', True)

        return cls(
            file_type,
            charset,
            delimiter,
            quote_char,
            escape_char,
            eol_char,
            comment_char,
            sheet_name,
            bool(header))


class DimensionAggregation(Enum):
    """Class DimensionAggregation for the aggregation types used in column mapping"""
    FIRST = "FIRST"
    LAST = "LAST"
    DISTINCT = "DISTINCT"


class GroupedTasksDimensionAggregation(Enum):
    """Class GroupedTasksDimensionAggregation for the aggregation types used in column mapping"""
    FIRST = "FIRST"
    LAST = "LAST"


class MetricAggregation(Enum):
    """Class MetricAggregation for the aggregation types used in column mapping"""
    FIRST = "FIRST"
    LAST = "LAST"
    MIN = "MIN"
    MAX = "MAX"
    SUM = "SUM"
    AVG = "AVG"
    MEDIAN = "MEDIAN"


class ColumnType(Enum):
    """Class ColumnType for the column types used in column mapping"""
    CASE_ID = "CASE_ID"
    TASK_NAME = "TASK_NAME"
    TIME = "TIME"
    METRIC = "METRIC"
    DIMENSION = "DIMENSION"


class Column:
    """A Column used in the column mapping"""

    def __init__(self, name: str, index: int, column_type: ColumnType, *, is_case_scope: bool = False,
                 aggregation: Union[MetricAggregation, DimensionAggregation] = None, grouped_tasks_columns: [] = None,
                 grouped_tasks_aggregation: Union[GroupedTasksDimensionAggregation, MetricAggregation] = None,
                 unit: str = None, time_format: str = None):
        """
        :param name: the name of the column
        :param index: the index of the column
        :param column_type: the type of the column, based on ColumnType
        :param is_case_scope: boolean to say if the column is a case scope column
        :param aggregation: the aggregation of the column
        :param grouped_tasks_columns: list of columns indices that are grouped
        :param grouped_tasks_aggregation: the aggregation of the grouped tasks
        :param unit: the unit of the column
        :param time_format: the time format of the column
        """

        self.name = name
        self.index = index
        self.column_type = column_type
        self.is_case_scope = is_case_scope
        self.aggregation = aggregation
        self.grouped_tasks_columns = grouped_tasks_columns
        self.grouped_tasks_aggregation = grouped_tasks_aggregation
        self.unit = unit
        self.time_format = time_format

        if self.column_type == ColumnType.TIME:
            if time_format is None:
                raise ValueError("time_format is required for time column")
        else:
            if self.time_format is not None:
                raise ValueError("time_format can only be used with 'time' column type")

        if (any(p is not None for p in [self.aggregation, self.unit]) and self.column_type not in
                [ColumnType.METRIC, ColumnType.DIMENSION]):
            raise ValueError(f"Aggregation and unit parameters are not allowed for {self.column_type} columns")

        if (self.column_type == ColumnType.METRIC
                and self.aggregation is not None
                and self.aggregation not in MetricAggregation):
            raise ValueError("Aggregation of a 'metric' column type must be a MetricAggregation")

        if (self.column_type == ColumnType.DIMENSION
                and self.aggregation is not None
                and self.aggregation not in DimensionAggregation):
            raise ValueError("Aggregation of a 'dimension' column type must be a DimensionAggregation")

        if (self.column_type == ColumnType.METRIC
                and self.grouped_tasks_aggregation is not None
                and self.grouped_tasks_aggregation not in MetricAggregation):
            raise ValueError("Grouped task aggregation of a 'METRIC' column type must be a MetricAggregation")

        if (self.column_type == ColumnType.DIMENSION
                and self.grouped_tasks_aggregation is not None
                and self.grouped_tasks_aggregation not in GroupedTasksDimensionAggregation):
            raise ValueError(
                "Grouped task aggregation of a 'DIMENSION' column type must be a GroupedTasksDimensionAggregation")

        if self.grouped_tasks_columns is not None and self.column_type != ColumnType.TASK_NAME:
            raise ValueError("Attribute 'grouped_tasks_columns' can only be used with 'TASK_NAME' column type")

    def to_dict(self):
        """Returns the JSON dictionary format of the Column"""

        res = {'name': self.name, 'columnIndex': self.index, 'columnType': self.column_type.value}
        if self.aggregation is not None:
            res['aggregation'] = self.aggregation.value
        if self.unit is not None:
            res['unit'] = self.unit
        if self.column_type == ColumnType.TIME:
            res['format'] = self.time_format
        elif self.column_type in [ColumnType.METRIC, ColumnType.DIMENSION]:
            res['isCaseScope'] = self.is_case_scope
        if self.grouped_tasks_columns is not None:
            res['groupedTasksColumns'] = self.grouped_tasks_columns
        if self.grouped_tasks_aggregation is not None:
            res['groupedTasksAggregation'] = self.grouped_tasks_aggregation.value if isinstance(
                self.grouped_tasks_aggregation, Enum) else self.grouped_tasks_aggregation
        return res

    @classmethod
    def from_json(cls, json_str):
        """Convert JSON string to dictionary

        :param json_str: JSON string"""
        data = json.loads(json_str)

        # Extract column parameters from the JSON dictionary
        name = data.get('name')
        if name is None:
            raise KeyError('Column JSON must contain a "name" field.')

        index = data.get('columnIndex')
        if index is None:
            raise KeyError('Column JSON must contain a "columnIndex" field.')

        column_type = data.get('columnType')
        if column_type is None:
            raise KeyError('Column JSON must contain a "columnType" field.')
        valid_column_types = [x.name for x in ColumnType]
        if column_type not in valid_column_types:
            raise ValueError(f'Invalid columnType, must be one of the following: {", ".join(valid_column_types)}.')
        column_type = ColumnType[column_type]
        is_case_scope = data.get('isCaseScope', False)
        aggregation = data.get('aggregation')
        if aggregation is not None:
            if column_type == ColumnType.METRIC:
                supported_aggregations = MetricAggregation
            elif column_type == ColumnType.DIMENSION:
                supported_aggregations = DimensionAggregation
            else:
                raise ValueError('Aggregation field should only be fill for columns of type metric or dimension')
            valid_aggregations = [x.name for x in supported_aggregations]
            if aggregation not in valid_aggregations:
                raise ValueError(f'Invalid aggregation, must be one of the following: {", ".join(valid_aggregations)}.')
            aggregation = supported_aggregations[aggregation]

        grouped_tasks_columns = data.get('groupedTasksColumns')
        grouped_tasks_aggregation = data.get('groupedTasksAggregation')

        if grouped_tasks_aggregation is not None:
            if column_type == ColumnType.METRIC:
                supported_aggregations = MetricAggregation
            elif column_type == ColumnType.DIMENSION:
                supported_aggregations = GroupedTasksDimensionAggregation
            else:
                raise ValueError(
                    'groupedTasksAggregation field should only be fill for columns of type metric or dimension')
            valid_aggregations = [x.name for x in supported_aggregations]
            if grouped_tasks_aggregation not in valid_aggregations:
                raise ValueError(f'Invalid groupedTasksAggregation, must be one of the following: '
                                 f'{", ".join(valid_aggregations)}.')
            grouped_tasks_aggregation = supported_aggregations[grouped_tasks_aggregation]
        unit = data.get('unit')
        time_format = data.get('format')

        return cls(
            name,
            int(index),
            column_type,
            is_case_scope=bool(is_case_scope),
            aggregation=aggregation,
            grouped_tasks_columns=grouped_tasks_columns,
            grouped_tasks_aggregation=grouped_tasks_aggregation,
            unit=unit,
            time_format=time_format)


class ColumnMapping:
    """Description of the columnMapping before sending a file"""

    def __init__(self, column_list: List[Column]):
        """ Creates a ColumnMapping

        :param column_list: the list of columns to use
        """
        column_indices = [c.index for c in column_list]
        if len(set(column_indices)) != len(column_indices):
            raise ValueError("Duplicate column indices")

        self.case_id_column = self.__get_columns_from_type(column_list, ColumnType.CASE_ID, expected_num=1)[0]
        self.task_name_column = self.__get_columns_from_type(column_list, ColumnType.TASK_NAME, expected_num=1)[0]
        self.time_columns = self.__get_columns_from_type(column_list, ColumnType.TIME, expected_num=[1, 2])
        self.metric_columns = self.__get_columns_from_type(column_list, ColumnType.METRIC)
        self.dimension_columns = self.__get_columns_from_type(column_list, ColumnType.DIMENSION)

        if self.task_name_column.grouped_tasks_columns is not None:
            if any(c.grouped_tasks_aggregation is None for c in self.metric_columns + self.dimension_columns):
                raise ValueError(
                    'If using "grouped_tasks_columns" for "task_name_column",'
                    ' please provide "grouped_task_aggregations" for other columns')

            if self.task_name_column.index not in self.task_name_column.grouped_tasks_columns:
                raise ValueError(
                    'The "grouped_tasks_columns" list must include at least an index of a column of type "TASK_NAME"')

            if self.case_id_column.index in self.task_name_column.grouped_tasks_columns:
                raise ValueError(
                    'The "grouped_tasks_columns" list cannot contain the index of a column of type "CASE_ID"')

            required_types = {ColumnType.METRIC, ColumnType.DIMENSION, ColumnType.TIME}
            other_types = set(c.column_type for c in self.metric_columns + self.dimension_columns + self.time_columns)
            # Check for the intersection of required_types and types of other columns.
            # If there is no intersection (none of the required types are present), raise an error
            if not required_types.intersection(other_types):
                raise ValueError(
                    'The "grouped_tasks_columns" list must contain the index of a column of type "METRIC", '
                    '"DIMENSION", or "TIME"')

        if self.task_name_column.grouped_tasks_columns is None:
            if any(c.grouped_tasks_aggregation is not None for c in self.metric_columns + self.dimension_columns):
                raise ValueError(
                    'If not using "grouped_tasks_columns" for "task_name_column", '
                    'please do not provide "grouped_task_aggregations" for other columns')

    def __get_columns_from_type(self, column_list: List[Column], filter: ColumnType, *,
                                expected_num: Union[int, List[int]] = None) -> List[Column]:
        """Returns a list of columns based on their type

        :param column_list: the list of columns to use
        :param filter: the type of the column
        :param expected_num: the expected number of columns
        :return: the list of columns
        """
        filtered_list = [c for c in column_list if c.column_type == filter]
        if expected_num is not None:
            if isinstance(expected_num, int):
                if len(filtered_list) != expected_num:
                    raise ValueError(f"Number of {filter} columns should be {expected_num}")
            else:
                if len(filtered_list) not in expected_num:
                    raise ValueError(f"Number of {filter} columns should be one of following values: {expected_num}")
        return filtered_list

    def to_dict(self):
        """Returns the JSON dictionary format of the ColumnMapping"""
        return {
            'caseIdMapping': self.case_id_column.to_dict(),
            'activityMapping': self.task_name_column.to_dict(),  # activity = task_name
            'timeMappings': [c.to_dict() for c in self.time_columns],
            'dimensionsMappings': [c.to_dict() for c in self.dimension_columns],
            'metricsMappings': [c.to_dict() for c in self.metric_columns],
        }

    @classmethod
    def from_json(cls, json_str):
        """Convert JSON string to dictionary

        :param json_str: the JSON string"""
        # Load json to get dictionary of columns dicts
        columns_dict_collection = json.loads(json_str)

        # if collection is dict format, only

        # If collection of columns is dict format, only keep values and make it list
        if type(columns_dict_collection) is dict:
            columns_dict_collection = columns_dict_collection.values()

        columns_dict_list = []
        for element in columns_dict_collection:
            # Nested list of columns_dicts encountered, so we use extend method
            if type(element) is list:
                columns_dict_list.extend(element)
            # Otherwise we assume the element to be a column_dict ready to be converted into Column object
            else:
                columns_dict_list.append(element)

        # Convert each column dict to a json so that we can call Column's from_json method
        columns_json_list = [json.dumps(c_dict) for c_dict in columns_dict_list]

        # Convert each column json to Column object
        columns_list = [Column.from_json(json_str) for json_str in columns_json_list]

        # Call constructor with column_list
        return cls(columns_list)
