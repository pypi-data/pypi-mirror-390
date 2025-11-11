# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
import json
import pytest
from igrafx_mining_sdk.column_mapping import ColumnType, Column, ColumnMapping, GroupedTasksDimensionAggregation, \
    MetricAggregation


class TestColumnMapping:
    """Test class for ColumnMapping"""
    @pytest.mark.dependency(name='case_id_column', scope='session')
    def test_create_case_id_column(self):
        """ Test to create a case id column"""
        column = Column('test', 0, ColumnType.CASE_ID)
        assert isinstance(column, Column)

    def test_exception_case_id_column_with_time_format(self):
        """ Test case_id type column with time format"""
        with pytest.raises(ValueError):
            Column('test', 0, ColumnType.CASE_ID, time_format="yyyy-MM-dd'T'HH:mm")

    def test_create_time_column(self):
        """ Test to create a time column"""
        column = Column('test', 0, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm")
        assert isinstance(column, Column)

    def test_exception_time_column_without_time_format(self):
        """Test time column without time format"""
        with pytest.raises(ValueError):
            Column('test', 0, ColumnType.TIME)

    def test_create_metric_grouped_tasks(self):
        """ Test to create a metric column with a grouped task aggregation"""
        column = Column('test', 0, ColumnType.METRIC, grouped_tasks_aggregation=MetricAggregation.FIRST)
        assert isinstance(column, Column)

    def test_exception_metric_type_grouped_tasks(self):
        """ Test metric type column with grouped task aggregation of type GroupedTasksDimensionAggregation"""
        with pytest.raises(ValueError):
            Column('test', 0, ColumnType.METRIC, grouped_tasks_aggregation=GroupedTasksDimensionAggregation.FIRST)

    def test_create_dimension_grouped_tasks(self):
        """ Test to create a dimension column with a grouped task aggregation"""
        column = Column('test', 0, ColumnType.DIMENSION,
                        grouped_tasks_aggregation=GroupedTasksDimensionAggregation.FIRST)
        assert isinstance(column, Column)

    def test_exception_dimension_type_group_tasks(self):
        """ Test dimension type column with grouped task aggregation of type MetricAggregation"""
        with pytest.raises(ValueError):
            Column('test', 0, ColumnType.DIMENSION, grouped_tasks_aggregation=MetricAggregation.FIRST)

    def test_create_task_name_grouped_tasks(self):
        """ Test to create a task name column with a grouped_tasks_column"""
        column = Column('test', 0, ColumnType.TASK_NAME, grouped_tasks_columns=[1, 3])
        assert isinstance(column, Column)

    def test_exception_task_name_type_group_tasks(self):
        """ Test metric type column with grouped_tasks_columns"""
        with pytest.raises(ValueError):
            Column('test', 0, ColumnType.METRIC, grouped_tasks_columns=[1, 3])

    @pytest.mark.dependency(name='column_mapping', depends=["case_id_column"], scope='session')
    def test_column_mapping_creation(self):
        """ Test to create a column mapping with columns"""
        column_list = [
            Column('case_id', 0, ColumnType.CASE_ID),
            Column('task_name', 1, ColumnType.TASK_NAME),
            Column('time', 2, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm")
        ]
        column_mapping = ColumnMapping(column_list)
        assert isinstance(column_mapping, ColumnMapping)

    def test_exception_time_column_missing(self):
        """ Test that time column is missing"""
        with pytest.raises(ValueError):
            ColumnMapping([
                Column('case_id', 0, ColumnType.CASE_ID),
                Column('task_name', 1, ColumnType.TASK_NAME)
            ])

    @pytest.mark.dependency(depends=["column_mapping"])
    def test_column_mapping_with_grouped_tasks_columns(self):
        """ Test to define a valid column mapping with grouped_tasks_columns and grouped_tasks_aggregation"""
        column_list = [
            Column('case_id', 0, ColumnType.CASE_ID),
            Column('time', 1, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm"),
            Column('task_name', 2, ColumnType.TASK_NAME, grouped_tasks_columns=[2, 3]),
            Column('country', 3, ColumnType.METRIC, grouped_tasks_aggregation=MetricAggregation.FIRST),
            Column('price', 4, ColumnType.DIMENSION, grouped_tasks_aggregation=GroupedTasksDimensionAggregation.FIRST)
        ]
        column_mapping = ColumnMapping(column_list)
        assert isinstance(column_mapping, ColumnMapping)

    def test_column_mapping_with_grouped_tasks_columns_case_id_exception(self):
        """ Test to define an invalid column mapping with grouped_tasks_columns containing the index of CASE_ID"""
        with pytest.raises(ValueError):
            ColumnMapping([
                Column('case_id', 0, ColumnType.CASE_ID),
                Column('time', 1, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm"),
                Column('task_name', 2, ColumnType.TASK_NAME, grouped_tasks_columns=[2, 0]),
                Column('country', 3, ColumnType.METRIC, grouped_tasks_aggregation=MetricAggregation.FIRST),
                Column('price', 4, ColumnType.DIMENSION,
                       grouped_tasks_aggregation=GroupedTasksDimensionAggregation.FIRST)
            ])

    def test_column_mapping_with_grouped_tasks_columns_task_name_exception(self):
        """Test to define an invalid column mapping with grouped_tasks_columns missing the index of TASK_NAME"""
        with pytest.raises(ValueError):
            ColumnMapping([
                Column('case_id', 0, ColumnType.CASE_ID),
                Column('time', 1, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm"),
                Column('task_name', 2, ColumnType.TASK_NAME, grouped_tasks_columns=[1, 3]),
                Column('country', 3, ColumnType.METRIC, grouped_tasks_aggregation=MetricAggregation.FIRST),
                Column('price', 4, ColumnType.DIMENSION,
                       grouped_tasks_aggregation=GroupedTasksDimensionAggregation.FIRST)
            ])

    def test_column_mapping_with_grouped_tasks_columns_type_exception(self):
        """Test to define an invalid column mapping with grouped_tasks_columns missing the index of TASK_NAME
            but having the index of a column of type METRIC, DIMENSION or TIME"""
        column_list = [
            Column('case_id', 0, ColumnType.CASE_ID),
            Column('time', 1, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm"),
            Column('task_name', 2, ColumnType.TASK_NAME, grouped_tasks_columns=[3]),
            Column('country', 3, ColumnType.METRIC, grouped_tasks_aggregation=MetricAggregation.FIRST),
            Column('price', 4, ColumnType.DIMENSION, grouped_tasks_aggregation=GroupedTasksDimensionAggregation.FIRST)
        ]
        with pytest.raises(ValueError):
            ColumnMapping(column_list)

    def test_exception_column_mapping_with_grouped_tasks_columns(self):
        """ Test to define an invalid column mapping with grouped_tasks_columns
            but without a METRIC grouped_tasks_aggregation"""
        with pytest.raises(ValueError):
            ColumnMapping([
                Column('case_id', 0, ColumnType.CASE_ID),
                Column('time', 1, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm"),
                Column('task_name', 2, ColumnType.TASK_NAME, grouped_tasks_columns=[2, 3]),
                Column('country', 3, ColumnType.METRIC),
                Column('price', 4, ColumnType.DIMENSION,
                       grouped_tasks_aggregation=GroupedTasksDimensionAggregation.FIRST)
            ])

    def test_exception_column_mapping_without_grouped_tasks_columns(self):
        """ Test to define an invalid column mapping without grouped_tasks_columns but with grouped_tasks_aggregation"""
        with pytest.raises(ValueError):
            ColumnMapping([
                Column('case_id', 0, ColumnType.CASE_ID),
                Column('time', 1, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm"),
                Column('task_name', 2, ColumnType.TASK_NAME),
                Column('country', 3, ColumnType.METRIC, grouped_tasks_aggregation=MetricAggregation.FIRST),
            ])

    def test_exception_too_many_case_id_columns(self):
        """ Test to define an invalid column mapping with too many case_id columns"""
        with pytest.raises(ValueError):
            ColumnMapping([
                Column('case_id_1', 0, ColumnType.CASE_ID),
                Column('case_id_2', 1, ColumnType.CASE_ID),
                Column('task_name', 2, ColumnType.TASK_NAME),
                Column('time', 3, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm")
            ])

    def test_exception_duplicate_column_indices(self):
        """ Test to define an invalid column mapping with duplicate column indices"""
        with pytest.raises(ValueError):
            ColumnMapping([
                Column('case_id', 0, ColumnType.CASE_ID),
                Column('task_name', 0, ColumnType.TASK_NAME),
                Column('time', 1, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm")
            ])

    @pytest.mark.dependency(name='create_column_from_json', depends=['case_id_column'])
    def test_create_column_from_json(self):
        """ Test to define a valid column from json"""
        json_str = '{"name": "test", "columnIndex": "1", "columnType": "CASE_ID"}'
        column = Column.from_json(json_str)
        assert isinstance(column, Column)

    def test_create_column_with_aggregation_from_json(self):
        """ Test to define a valid column with aggregation  from json"""
        json_str = '{"name": "test", "columnIndex": "1", "columnType": "METRIC", "aggregation": "MAX"}'
        column = Column.from_json(json_str)
        assert isinstance(column, Column)

    def test_exception_invalid_column_type(self):
        """ Test to define an invalid column type from json"""
        with pytest.raises(ValueError):
            json_str = '{"name": "test", "columnIndex": "1", "columnType": "INVALID_TYPE"}'
            Column.from_json(json_str)

    def test_exception_aggregation_on_non_metric_or_dimension_column(self):
        """ Test exception aggregation on non-metric or dimension column"""
        with pytest.raises(ValueError):
            json_str = '{"name": "test", "columnIndex": "1", "columnType": "CASE_ID", "aggregation": "MAX"}'
            Column.from_json(json_str)

    def test_exception_invalid_aggregation(self):
        """ Test exception for an invalid aggregation whn creating a column from json"""
        with pytest.raises(ValueError):
            json_str = '{"name": "test", "columnIndex": "1", "columnType": "DIMENSION", "aggregation": "MAX"}'
            Column.from_json(json_str)

    @pytest.mark.dependency(name='column_to_dict_from_json', depends=["create_column_from_json"])
    def test_column_to_dict_from_json(self):
        """ Test to define a valid column , convert it to JSON string and back"""
        column = Column('test', 0, ColumnType.CASE_ID)
        json_str = json.dumps(column.to_dict())
        column = Column.from_json(json_str)
        assert isinstance(column, Column)

    @pytest.mark.dependency(depends=['create_column_from_json', 'column_mapping'])
    def test_create_column_mapping_from_json_dict(self):
        """ Test to define a valid column mapping from a column dictionary json"""
        column_dict = '''{
        "col1": {"name": "case_id", "columnIndex": "0", "columnType": "CASE_ID"},
        "col2": {"name": "task_name", "columnIndex": "1", "columnType": "TASK_NAME"},
        "col3": {"name": "time", "columnIndex": "2", "columnType": "TIME", "format": "yyyy-MM-dd'T'HH:mm"}
        }'''
        column_mapping = ColumnMapping.from_json(column_dict)
        assert isinstance(column_mapping, ColumnMapping)

    def test_create_column_mapping_from_json_dict_grouped_tasks(self):
        """ Test to define a valid column mapping from a column dictionary json with grouped tasks"""
        column_dict = '''{
        "col1": {"name": "Case ID", "columnIndex": "0", "columnType":   "CASE_ID"},
        "col2": {"name": "Activity", "columnIndex": "1", "columnType": "TASK_NAME", "groupedTasksColumns": [1, 2, 3]},
        "col3": {"name": "Start Date", "columnIndex": "2", "columnType": "TIME", "format": "dd/MM/yyyy HH:mm"},
        "col4": {"name": "End Date", "columnIndex": "3", "columnType": "TIME", "format": "dd/MM/yyyy HH:mm"},
        "col5": {"name": "Price", "columnIndex": "4", "columnType": "METRIC", "isCaseScope": false,
        "groupedTasksAggregation": "SUM", "aggregation": "SUM", "unit": "円"},
        "col6": {"name": "Forme", "columnIndex": "5", "columnType": "DIMENSION", "isCaseScope": false,
        "groupedTasksAggregation": "LAST", "aggregation": "DISTINCT"}
        }'''
        column_mapping = ColumnMapping.from_json(column_dict)
        assert isinstance(column_mapping, ColumnMapping)

    @pytest.mark.dependency(depends=['create_column_from_json', 'column_mapping'])
    def test_create_column_mapping_from_json_list(self):
        """ Test to define a valid column mapping from a column list json"""
        column_list = '''[
        {"name": "case_id", "columnIndex": "0", "columnType": "CASE_ID"},
        {"name": "task_name", "columnIndex": "1", "columnType": "TASK_NAME"},
        {"name": "time", "columnIndex": "2", "columnType": "TIME", "format": "yyyy-MM-dd'T'HH:mm"}
        ]'''
        column_mapping = ColumnMapping.from_json(column_list)
        assert isinstance(column_mapping, ColumnMapping)

    @pytest.mark.dependency(depends=['column_to_dict_from_json'])
    def test_column_mapping_to_dict_from_json(self):
        """ Test to define a valid column mapping from column list , convert it to JSON string and back"""
        column_list = [
            Column('case_id', 0, ColumnType.CASE_ID),
            Column('task_name', 1, ColumnType.TASK_NAME),
            Column('time', 2, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm")
        ]
        column_mapping = ColumnMapping(column_list)
        json_str = json.dumps(column_mapping.to_dict())
        column_mapping = ColumnMapping.from_json(json_str)
        assert isinstance(column_mapping, ColumnMapping)
