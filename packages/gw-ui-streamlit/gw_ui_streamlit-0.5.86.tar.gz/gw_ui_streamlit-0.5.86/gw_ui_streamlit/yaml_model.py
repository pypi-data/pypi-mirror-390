from typing import Any, List

from gw_ui_streamlit.constants import ButtonLevel, ButtonVariantType


class YamlModelBase:
    """
    YamlModelBase is a class that represents a model for handling YAML-based configurations. 
    It initializes various attributes based on the provided input dictionary.

    Attributes:
        code (str): A unique code identifier for the model.
        key (str): An optional key associated with the model.
        short_key (str): An optional short key for the model.
        label (str): A label describing the model.
        language: The language associated with the model.
        currency: The currency associated with the model.
        required: Indicates whether the model is required.
        tab: The tab associated with the model.
        cache: Cache settings for the model.
        enabled: Indicates whether the model is enabled.
        on_click: Configuration for the on-click event.
        on_click_function: A function to execute on-click (default is None).
        source: The source configuration for the model.
        on_change: Configuration for the on-change event.
        on_change_function: A function to execute on-change (default is None).
        on_select: Configuration for the on-select event.
        on_select_function: A function to execute on-select (default is None).
        default_function: Configuration for the default function.
        default_function_function: A function to execute as the default function (default is None).
        hidden: Indicates whether the model is hidden.
        source_function: A function to retrieve the source configuration.
        date_format: The date format associated with the model.
        db_field: The database field associated with the model.
        primary (bool): Indicates whether the model is a primary field.
        option_label: The label for options in the model.
        field_value_key (str): The key for the field value.
        field_value_short_key (str): The short key for the field value.

    Properties:
        Required (bool): Returns True if the model is marked as required, otherwise False.

    Methods:
        __init__(input_dict): Initializes the model attributes based on the input dictionary.
    """

    def __init__(self, input_dict):
        self.code: str = input_dict["code"]
        self.key: str = input_dict.get("key")
        self.short_key: str = input_dict.get("short_key")
        self.label: str = input_dict.get("label")
        self.language = input_dict.get("language")
        self.currency = input_dict.get("currency")
        self.required = input_dict.get("required")
        self.tab = input_dict.get("tab", "Main")
        self.cache = input_dict.get("cache")
        self.enabled = input_dict.get("enabled")
        self.on_click = input_dict.get("on_click")
        self.on_click_function: Any = None
        self.source = input_dict.get("source")
        self.on_change = input_dict.get("on_change")
        self.on_change_function = None
        self.on_select = input_dict.get("on_select")
        self.on_select_function = None
        self.default_function = input_dict.get("default_function")
        self.default_function_function = None
        self.hidden = input_dict.get("hidden")
        self.source_function = input_dict.get("source_function")
        self.date_format = input_dict.get("date_format")
        self.db_field = input_dict.get("field")
        self.primary: bool = input_dict.get("primary")
        self.option_label = input_dict.get("option_label")
        self.field_value_key: str = input_dict.get("value_key")
        self.field_value_short_key: str = input_dict.get("value_short_key")

    @property
    def Required(self):
        """
        Check if the 'required' attribute is set to True.

        Returns:
            bool: True if the 'required' attribute is True, otherwise False.
        """
        if self.required:
            return True
        return False


class YamlModelButtons(YamlModelBase):
    """
    A class representing button configurations parsed from a YAML input dictionary.

    Attributes:
        level (ButtonLevel): The level of the button, defaulting to ButtonLevel.application if not provided.
        icon (str): The icon associated with the button, if specified in the input dictionary.
        variant (ButtonVariantType): The variant type of the button, defaulting to ButtonVariantType.secondary if not provided.

    Methods:
        __init__(input_dict):
            Initializes the YamlModelButtons instance with values from the input dictionary.
    """
    def __init__(self, input_dict):
        super().__init__(input_dict)
        self.level = input_dict.get("level", ButtonLevel.application)
        self.icon: str = input_dict.get("icon")
        self.variant = input_dict.get("variant", ButtonVariantType.secondary)


class YamlModelOption:
    """
    Represents an option defined in a YAML configuration file.

    Attributes:
        option_dict (dict): A dictionary containing the option's properties.
        value (Any): The value of the option, retrieved from the dictionary using the key "value".
        function (Any): The function associated with the option, retrieved from the dictionary using the key "function".
        option_function (Any): An additional function or callable associated with the option, retrieved from the dictionary using the key "option_function".

    Args:
        option_dict (dict): A dictionary containing the properties of the option.
    """

    def __init__(self, option_dict):
        self.option_dict = option_dict
        self.value = option_dict.get("value")
        self.function = option_dict.get("function")
        self.option_function = option_dict.get("option_function")


class YamlModelTableColumn(YamlModelBase):
    """
    Represents a column in a YAML-defined table model.

    This class is initialized with a dictionary containing configuration
    details for the column and provides attributes to access these details.

    Attributes:
        yaml_input_dict (dict): The original input dictionary used for initialization.
        table (str): The name of the table associated with the column.
        type (str): The data type of the column.
        default (Any): The default value for the column.
        default_function (callable, optional): A function to compute the default value, if applicable.
        function (str, optional): A function or operation associated with the column.
        min (Any, optional): The minimum value constraint for the column.
        max (Any, optional): The maximum value constraint for the column.
        immutable (bool, optional): Indicates whether the column is immutable.
        help (str, optional): Help text or description for the column.
        options (list, optional): A list of options or choices for the column, processed from the input dictionary.

    Methods:
        __init__(input_dict: dict): Initializes the column attributes based on the input dictionary.
    """

    def __init__(self, input_dict: dict):
        super().__init__(input_dict)
        self.yaml_input_dict = input_dict
        self.table = input_dict.get("table")
        self.type = input_dict.get("type")
        self.default = input_dict.get("default")
        self.default_function = None
        self.function = input_dict.get("function")
        self.min = input_dict.get("min")
        self.max = input_dict.get("max")
        self.immutable = input_dict.get("immutable")
        self.help = input_dict.get("help")
        self.options = process_options(self.yaml_input_dict)


class YamlModelTable(YamlModelBase):
    """
    Represents a table model parsed from a YAML configuration.

    Attributes:
        yaml_table_dict (dict): The dictionary representation of the YAML table configuration.
        columns (List[YamlModelTableColumn]): A list of column objects populated from the YAML table configuration.
        order (Any): The order of the table, as specified in the YAML configuration.
        immutable (Any): Indicates whether the table is immutable, as specified in the YAML configuration.
        type (Any): The type of the table, as specified in the YAML configuration.
        on_select (Any): The action or function to execute upon selecting a row, as specified in the YAML configuration.
        selection_mode (str): The selection mode for the table (e.g., "single-row"), defaults to "single-row".
        default_rows (Any): The default rows for the table, as specified in the YAML configuration.
        dialog_anchor (Any): The anchor for the dialog, as specified in the YAML configuration.
        dialog_inputs (Any): The inputs for the dialog, as specified in the YAML configuration.

    Properties:
        function (Optional[Any]): Returns the function associated with the column if there is only one column; 
                                  otherwise, returns None.

    Methods:
        __init__(table_dict): Initializes the YamlModelTable instance with the given table dictionary.
    """

    def __init__(self, table_dict):
        super().__init__(table_dict)
        self.yaml_table_dict = table_dict
        self.columns: List[YamlModelTableColumn] = populate_columns(self.yaml_table_dict)
        self.order = table_dict.get("order")
        self.immutable = table_dict.get("immutable")
        self.type = table_dict.get("type")
        self.on_select = table_dict.get("on_select")
        self.selection_mode = table_dict.get("selection_mode", "single-row")
        self.default_rows = table_dict.get("default_rows")
        self.dialog_anchor = table_dict.get("dialog_anchor")
        self.dialog_inputs = table_dict.get("dialog_inputs")


    @property
    def function(self):
        """
        Determines the function associated with the columns attribute.

        If the `columns` attribute contains exactly one element, this method returns
        the `function` attribute of that element. Otherwise, it returns `None`.

        Returns:
            Any: The `function` attribute of the single column if `columns` has one element,
            otherwise `None`.
        """
        if len(self.columns) == 1:
            return self.columns[0].function
        return None


class YamlModelInput(YamlModelBase):
    """
    Represents a YAML model input configuration, extending the functionality of `YamlModelBase`.
    This class is designed to handle various input types, including tables, and provides
    properties and methods for processing and accessing input-specific attributes.

    Attributes:
        yaml_input_dict (dict): The dictionary containing the YAML input configuration.
        type (str): The type of the input (e.g., "table").
        table (YamlModelTable | None): The processed table object if the input type is "table".
        default (Any): The default value for the input.
        default_function (Callable | None): A function to compute the default value, if applicable.
        on_change_function (Callable | None): A function to execute when the input changes.
        min (Any): The minimum value for the input, if applicable.
        max (Any): The maximum value for the input, if applicable.
        immutable (bool | None): Indicates whether the input is immutable.
        help (str | None): Help text or description for the input.
        options (list | None): Processed options for the input, if applicable.
        language (str | None): The programming language associated with the input, if applicable.
        extension (str | None): The file extension associated with the input, if applicable.

    Methods:
        process_table() -> YamlModelTable | None:
            Processes the input dictionary to create a `YamlModelTable` object if the input type is "table".

    Properties:
        columns (list | None): Returns the columns of the table if the input type is "table".
        function (Callable | None): Returns the function associated with the first column if there is only one column.
        order (Any | None): Returns the order of the table if the input type is "table".
        selection_mode (Any | None): Returns the selection mode of the table if the input type is "table".
        dialog_anchor (Any | None): Returns the dialog anchor of the table if the input type is "table".
        dialog_inputs (Any | None): Returns the dialog inputs of the table if the input type is "table".
    """

    def __init__(self, input_dict: dict):
        super().__init__(input_dict)
        self.yaml_input_dict = input_dict
        self.type = input_dict.get("type")
        self.table = self.process_table()
        self.default = input_dict.get("default")
        self.default_function = None
        self.on_change_function = None
        self.min = input_dict.get("min")
        self.max = input_dict.get("max")
        self.immutable = input_dict.get("immutable")
        self.help = input_dict.get("help")
        self.options = process_options(self.yaml_input_dict)
        self.language = input_dict.get("language")
        self.extension = input_dict.get("extension")

    def process_table(self) -> YamlModelTable | None:
        """
        Processes the YAML input dictionary and returns a YamlModelTable instance 
        if the type is "table". Otherwise, returns None.

        Returns:
            YamlModelTable | None: A YamlModelTable instance if the type is "table",
            otherwise None.
        """
        if self.type == "table":
            return YamlModelTable(self.yaml_input_dict)
        return None

    @property
    def columns(self):
        """
        Retrieve the columns of the table if the type is "table".

        Returns:
            list: A list of columns if the object type is "table".
            None: If the object type is not "table".
        """
        if self.type == "table":
            return self.table.columns
        return None

    @property
    def function(self):
        """
        Retrieves the function associated with the first column if there is only one column.

        Returns:
            function or None: The function of the first column if it exists and is not None.
            Returns None if there are no columns or if the function of the first column is None.
        """
        if len(self.columns) == 1:
            if self.columns[0].function is None:
                return None
            return self.columns[0].function
        return None

    @property
    def order(self):
        """
        Determines the order of the object based on its type.

        If the object's type is "table", it retrieves the order from the associated table.
        Otherwise, it returns None.

        Returns:
            Any: The order of the table if the type is "table", otherwise None.
        """
        if self.type == "table":
            return self.table.order
        return None

    @property
    def selection_mode(self):
        """
        Determines the selection mode based on the type of the object.

        If the object's type is "table", it returns the selection mode of the table.
        Otherwise, it returns None.

        Returns:
            str or None: The selection mode of the table if the type is "table",
            otherwise None.
        """
        if self.type == "table":
            return self.table.selection_mode
        return None

    @property
    def dialog_anchor(self):
        """
        Determines the dialog anchor based on the type of the object.

        If the object's type is "table", it retrieves the dialog anchor from the 
        associated table object. Otherwise, it returns None.

        Returns:
            Any: The dialog anchor if the type is "table", otherwise None.
        """
        if self.type == "table":
            return self.table.dialog_anchor
        return None

    @property
    def dialog_inputs(self):
        if self.type == "table":
            return self.table.dialog_inputs
        return None

class YamlModel:
    """YamlModel is a class designed to represent and process data from a YAML file dictionary. 
        It provides attributes and methods to handle various components of the YAML structure, 
        such as inputs, buttons, tabs, and other metadata.

        Attributes:
            yaml_dict (dict): The original dictionary parsed from the YAML file.
            code (str): The code identifier extracted from the YAML dictionary.
            name (str): The name of the model extracted from the YAML dictionary.
            description (str): A description of the model extracted from the YAML dictionary.
            developer (str): The developer information extracted from the YAML dictionary.
            concept (str): The concept or idea behind the model extracted from the YAML dictionary.
            title (str): The title of the model extracted from the YAML dictionary.
            rest (str): REST-related information extracted from the YAML dictionary.
            rest_get (str): REST GET-related information extracted from the YAML dictionary.
            structure_type (str): The structure type of the model extracted from the YAML dictionary.
            inputs (List[YamlModelInput]): A list of input objects processed from the YAML dictionary.
            buttons (List[YamlModelButtons]): A list of button objects processed from the YAML dictionary.
            tabs (list): A list of tabs extracted from the YAML dictionary.
            width (str): The width of the model extracted from the YAML dictionary, defaulting to "30%".

        Methods:
            process_inputs():
                Processes the "inputs" key in the YAML dictionary and returns a list of YamlModelInput objects.
                If the "inputs" key is not present, an empty list is returned.

            process_buttons():
                If the "buttons" key is not present, an empty list is returned.

            primary:
                A property method that determines and returns the primary input or column from the inputs.
                Iterates through the `inputs` attribute to find an item or column marked as primary.
                If no primary input or column is found, returns None."""

    def __init__(self, yaml_file_dict):
        self.yaml_dict = yaml_file_dict
        self.code = yaml_file_dict.get("code")
        self.name = yaml_file_dict.get("name")
        self.description = yaml_file_dict.get("description")
        self.developer = yaml_file_dict.get("developer")
        self.concept = yaml_file_dict.get("concept")
        self.title = yaml_file_dict.get("title")
        self.rest = yaml_file_dict.get("rest")
        self.rest_get = yaml_file_dict.get("rest_get")
        self.structure_type = yaml_file_dict.get("structure_type")
        self.inputs: List[YamlModelInput] = self.process_inputs()
        self.buttons: List[YamlModelButtons] = self.process_buttons()
        self.tabs = yaml_file_dict.get("tabs", [])
        self.width = yaml_file_dict.get("width", "30%")
        self.parent_model = yaml_file_dict.get("parent_model")

    def process_inputs(self):
        """
        Processes the "inputs" key in the YAML dictionary and returns a list of YamlModelInput objects.

        If the "inputs" key is not present in the YAML dictionary, an empty list is returned.

        Returns:
            list: A list of YamlModelInput objects created from the "inputs" key in the YAML dictionary.
        """
        if "inputs" not in self.yaml_dict:
            return []
        yaml_model_inputs = [YamlModelInput(input_dict) for input_dict in self.yaml_dict.get("inputs")]
        return yaml_model_inputs

    def process_buttons(self):
        """
        Processes the "buttons" key in the YAML dictionary and returns a list of YamlModelButtons objects.

        If the "buttons" key is not present in the YAML dictionary, an empty list is returned.

        Returns:
            list: A list of YamlModelButtons objects created from the "buttons" key in the YAML dictionary.
        """
        if "buttons" not in self.yaml_dict:
            return []
        yaml_model_buttons = [YamlModelButtons(input_dict) for input_dict in self.yaml_dict.get("buttons")]
        return yaml_model_buttons

    @property
    def primary(self):
        """
        Determines and returns the primary input or column from the inputs.

        This method iterates through the `inputs` attribute to find an item or column
        marked as primary. If an input item has the `primary` attribute set to True,
        it is returned. If the input item is of type "table", the method further checks
        its columns to find a column marked as primary.

        Returns:
            object: The primary input item or column if found, otherwise None.
        """
        for input_item in self.inputs:
            if input_item.primary:
                return input_item
            if input_item.type == "table":
                for input_column in input_item.columns:
                    if input_column.primary:
                        return input_column
        return None


def process_options(yaml_input_dict) -> List[YamlModelOption] | None:
    """
    Processes the "options" key in a given YAML input dictionary and returns a list of YamlModelOption objects.

    Args:
        yaml_input_dict (dict): A dictionary representing the YAML input. It should contain an "options" key
                                with a list of dictionaries as its value.

    Returns:
        List[YamlModelOption] | None: A list of YamlModelOption objects if the "options" key exists in the input
                                       dictionary; otherwise, returns None.
    """
    if "options" not in yaml_input_dict:
        return None
    yaml_options = [YamlModelOption(input_dict) for input_dict in yaml_input_dict.get("options")]
    return yaml_options


def populate_columns(yaml_table_dict) -> List[YamlModelTableColumn] | None:
    """
    Populate a list of YamlModelTableColumn objects from a dictionary representation of a YAML table.

    Args:
        yaml_table_dict (dict): A dictionary containing YAML table data. 
                                Expected to have a "columns" key with a list of column definitions.

    Returns:
        List[YamlModelTableColumn] | None: A list of YamlModelTableColumn objects if the "columns" key exists,
                                           otherwise an empty list.
    """
    if "columns" not in yaml_table_dict:
        return []
    columns = [YamlModelTableColumn(input_dict) for input_dict in yaml_table_dict.get("columns")]
    return columns