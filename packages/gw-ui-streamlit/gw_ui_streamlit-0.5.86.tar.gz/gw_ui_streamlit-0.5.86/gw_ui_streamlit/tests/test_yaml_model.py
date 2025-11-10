import unittest
from unittest.mock import patch, MagicMock

from gw_ui_streamlit.yaml_model import (
    YamlModelBase,
    YamlModelButtons,
    YamlModelOption,
    YamlModelTableColumn,
    YamlModelTable,
    YamlModelInput,
    YamlModel,
    process_options,
    populate_columns,
)


class TestYamlModelBase(unittest.TestCase):
    def test_initialization(self):
        input_dict = {
            "code": "test_code",
            "key": "test_key",
            "label": "Test Label",
            "required": True,
            "primary": True,
        }
        model = YamlModelBase(input_dict)
        self.assertEqual(model.code, "test_code")
        self.assertEqual(model.key, "test_key")
        self.assertEqual(model.label, "Test Label")
        self.assertTrue(model.Required)
        self.assertTrue(model.primary)


class TestYamlModelButtons(unittest.TestCase):
    def test_initialization(self):
        input_dict = {
            "code": "button_code",
            "level": "application",
            "icon": "test_icon",
            "variant": "secondary",
        }
        model = YamlModelButtons(input_dict)
        self.assertEqual(model.code, "button_code")
        self.assertEqual(model.level, "application")
        self.assertEqual(model.icon, "test_icon")
        self.assertEqual(model.variant, "secondary")


class TestYamlModelOption(unittest.TestCase):
    def test_initialization(self):
        option_dict = {"value": "test_value", "function": "test_function"}
        option = YamlModelOption(option_dict)
        self.assertEqual(option.value, "test_value")
        self.assertEqual(option.function, "test_function")


class TestYamlModelTableColumn(unittest.TestCase):
    def test_initialization(self):
        input_dict = {
            "code": "column_code",
            "table": "test_table",
            "type": "string",
            "primary": True,
        }
        column = YamlModelTableColumn(input_dict)
        self.assertEqual(column.code, "column_code")
        self.assertEqual(column.table, "test_table")
        self.assertEqual(column.type, "string")
        self.assertTrue(column.primary)


class TestYamlModelTable(unittest.TestCase):
    @patch("gw_ui_streamlit.yaml_model.populate_columns")
    def test_initialization(self, mock_populate_columns):
        mock_populate_columns.return_value = []
        table_dict = {"code": "table_code", "columns": []}
        table = YamlModelTable(table_dict)
        self.assertEqual(table.code, "table_code")
        self.assertEqual(table.columns, [])


class TestYamlModelInput(unittest.TestCase):
    @patch("gw_ui_streamlit.yaml_model.process_options")
    def test_initialization(self, mock_process_options):
        mock_process_options.return_value = []
        input_dict = {"code": "input_code", "type": "table"}
        model_input = YamlModelInput(input_dict)
        self.assertEqual(model_input.code, "input_code")
        self.assertEqual(model_input.type, "table")


class TestYamlModel(unittest.TestCase):
    @patch("gw_ui_streamlit.yaml_model.process_options")
    @patch("gw_ui_streamlit.yaml_model.populate_columns")
    def test_initialization(self, mock_populate_columns, mock_process_options):
        mock_populate_columns.return_value = []
        mock_process_options.return_value = []
        yaml_dict = {
            "code": "model_code",
            "name": "Test Model",
            "parent_model": None,
            "inputs": [],
            "buttons": [],
        }
        model = YamlModel(yaml_dict)
        self.assertEqual(model.code, "model_code")
        self.assertEqual(model.name, "Test Model")
        self.assertIsNone(model.parent_model)
        self.assertEqual(model.inputs, [])
        self.assertEqual(model.buttons, [])

class TestYamlModelEmpty(unittest.TestCase):
    def test_initialization(self):
        yaml_dict = {
        }
        model = YamlModel(yaml_dict)
        self.assertIsNone(model.code)
        self.assertIsNone(model.name)
        self.assertIsNone(model.parent_model)


class TestUtilityFunctions(unittest.TestCase):
    def test_process_options(self):
        yaml_input_dict = {"options": [{"value": "opt1"}, {"value": "opt2"}]}
        options = process_options(yaml_input_dict)
        self.assertEqual(len(options), 2)
        self.assertEqual(options[0].value, "opt1")
        self.assertEqual(options[1].value, "opt2")

    def test_populate_columns(self):
        yaml_table_dict = {"columns": [{"code": "col1"}, {"code": "col2"}]}
        columns = populate_columns(yaml_table_dict)
        self.assertEqual(len(columns), 2)
        self.assertEqual(columns[0].code, "col1")
        self.assertEqual(columns[1].code, "col2")


if __name__ == "__main__":
    unittest.main()