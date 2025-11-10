import importlib
from gw_ui_streamlit.yaml_model import YamlModelInput


class GWUIImportError(ImportError):
    def __init__(
        self, fq_name: str, detail: str, *, __cause__: BaseException | None = None
    ) -> None:
        msg = f"Cannot resolve '{fq_name}': {detail}"
        super().__init__(msg)
        self.__cause__ = __cause__  # Python <3.11 compatibility


def construct_function(function_name):
    """
    Constructs and returns a callable function object from a string representation.

    Args:
        function_name (str): A string in the format 'module.sub:callable' where:
            - 'module.sub' specifies the module path.
            - 'callable' specifies the name of the function to be imported.

    Returns:
        callable: The imported function object if successful.
        None: If `function_name` is None.

    Raises:
        GWUIImportError: If the `function_name` does not contain a colon (':')
                         or if the specified function cannot be imported.
    """
    if function_name is None:
        return None
    if ":" not in function_name:
        raise GWUIImportError(function_name, "expected format 'module.sub:callable'")

    try:
        function_module = function_name.split(":")[0]
        function_function = function_name.split(":")[1]
        mod = importlib.import_module(function_module)
        defined_function = getattr(mod, function_function)
        # defined_function = getattr(
        #     __import__(function_module, globals(), locals(), [function_function]),
        #     function_function,
        # )
    except AttributeError:
        raise GWUIImportError(function_name, f"Unable to import 'function' {function_module}.{function_function}")
    return defined_function


def option_function(item: YamlModelInput):
    """
    Processes the options of a given `YamlModelInput` item and constructs a function
    if specific conditions are met.

    Args:
        item (YamlModelInput): An object containing options and function definitions.

    Returns:
        Callable or None: Returns a constructed function if the item has exactly one
        option and that option has a defined function. Otherwise, returns None.
    """
    if len(item.options) == 1 and item.options[0].Function is not None:
        function_name = item.on_change_function[0].Function
        defined_function = construct_function(function_name)
        return defined_function
    else:
        return None


def built_default_original_rows(gws) -> dict:
    """
    Generates a dictionary containing default rows for table inputs based on the provided YAML file.

    Args:
        gws: An object containing a `yaml_file` attribute. The `yaml_file` is expected to be a dictionary
             with an "inputs" key, which is a list of input configurations.

    Returns:
        dict: A dictionary where the keys are labels of table inputs and the values are the corresponding
              default rows. If `yaml_file` is None or no table inputs are found, an empty dictionary is returned.

    Notes:
        - The function filters the inputs from the YAML file to include only those with a "type" of "table".
        - For each table input, it retrieves the "default_rows" and associates it with the "label" of the input.
    """
    default_rows_dict = {}
    if gws.yaml_file is None:
        return default_rows_dict
    for item in [
        table_inputs
        for table_inputs in gws.yaml_file.get("inputs", [])
        if table_inputs.get("type") == "table"
    ]:
        default_rows = item.get("default_rows", dict())
        default_rows_dict[item.get("label")] = default_rows
    return default_rows_dict


def build_default_rows(gws) -> dict:
    """
    Constructs a dictionary of default rows for tables based on the provided `gws` object.

    Args:
        gws: An object containing configuration and data, including a `yaml_model` attribute
             that defines input tables and their properties.

    Returns:
        dict: A dictionary where keys are table labels and values are lists of default rows
              for each table. If `gws.yaml_model` is None or a table lacks default rows,
              the dictionary will contain only the original default rows.

    Notes:
        - The function first initializes the dictionary using `built_default_original_rows(gws)`.
        - It iterates through tables defined in `gws.yaml_model.inputs` with a type of "table".
        - For tables with defined `default_rows`, it extracts headers and rows, builds a list
          of rows, and updates the dictionary with the table label as the key.
    """
    default_rows_dict = built_default_original_rows(gws)
    if gws.yaml_model is None:
        return default_rows_dict

    for table in [item.table for item in gws.yaml_model.inputs if item.type == "table"]:
        if table.default_rows is None:
            continue
        headers, rows = extract_headers_and_rows(table)
        if not headers:
            continue
        row_list = build_row_list(headers, rows)
        default_rows_dict.update({table.label: row_list})

    return default_rows_dict


def extract_headers_and_rows(table):
    """
    Extracts headers and rows from a table object.

    Args:
        table: An object containing a `default_rows` attribute, which is expected
               to be a list of dictionaries. Each dictionary may contain keys
               "row_header" and "row".

    Returns:
        tuple: A tuple containing two lists:
            - headers: A list of values corresponding to the "row_header" key
              in the dictionaries within `table.default_rows`, excluding None values.
            - rows: A list of values corresponding to the "row" key in the
              dictionaries within `table.default_rows`, excluding None values.
    """
    headers = [
        item.get("row_header")
        for item in table.default_rows
        if item.get("row_header") is not None
    ]
    rows = [
        item.get("row") for item in table.default_rows if item.get("row") is not None
    ]
    return headers, rows


def build_row_list(headers, rows):
    """
    Constructs a list of dictionaries representing rows of data, where each dictionary maps
    header names to corresponding row values.

    Args:
        headers (list): A list containing a single string of comma-separated header names.
        rows (list): A list of row data, where each row is expected to be in a format compatible
                     with the headers.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row of data with keys
              corresponding to the header names and values corresponding to the row values.

    Example:
        headers = ["name,age,city"]
        rows = [["John,30,New York"], ["Jane,25,Los Angeles"]]
        result = build_row_list(headers, rows)
        # result would be:
        # [{'name': 'John', 'age': '30', 'city': 'New York'},
        #  {'name': 'Jane', 'age': '25', 'city': 'Los Angeles'}]
    """
    header_list = [item.strip() for item in str(headers[0]).split(",")]
    row_list = []
    for row in rows:
        row_dict = build_row_dict(header_list, row)
        row_list.append(row_dict)
    return row_list


def build_row_dict(header_list, row):
    """
    Constructs a dictionary mapping headers to corresponding row values.

    Args:
        header_list (list): A list of header names.
        row (str): A string representing a row of data, with values separated by commas.

    Returns:
        dict: A dictionary where each key is a header from `header_list` and the value is the corresponding
              item from the `row`, stripped of leading and trailing whitespace.

    Example:
        header_list = ["Name", "Age", "City"]
        row = "Alice, 30, New York"
        result = build_row_dict(header_list, row)
        # result: {"Name": "Alice", "Age": "30", "City": "New York"}
    """
    row_dict = {}
    rows_items = [item.strip() for item in str(row).split(",")]
    for header in header_list:
        row_dict[header] = rows_items[header_list.index(header)]
    return row_dict
