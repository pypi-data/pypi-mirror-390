from datetime import date
import json
import os
import pathlib
import platform
from typing import Any

import numpy
import streamlit as st
import yaml
from pathvalidate import is_valid_filepath

from gw_ui_streamlit import constants, independent_utils
from gw_ui_streamlit.constants import KeyType, CURRENCY_SYMBOLS
import gw_ui_streamlit._utils as _utils
from datetime import datetime

from gw_ui_streamlit.yaml_model import YamlModel, YamlModelBase


def codify_string(input_string: str) -> str:
    """
    Converts the input string into a unique code for the application.

    This function utilizes the `independent_utils.codify_string` method to perform
    the conversion. It is designed to ensure that the input string is transformed
    into a consistent and unique representation suitable for application use.

    Args:
        input_string (str): The string to be converted into a unique code.

    Returns:
        str: The unique code generated from the input string.
    """
    return independent_utils.codify_string(input_string)


def create_simple_key(key_type: KeyType, value: str) -> str:
    """
    Generates a simple key string by combining the key type, application name, and a given value.

    Args:
        key_type (KeyType): An enumeration representing the type of key.
        value (str): A string value to be included in the key.

    Returns:
        str: A codified string representing the generated key.

    Notes:
        - The function relies on the `st.session_state` to access the "GWStreamlit" object.
        - The `codify_string` function is used to process the final key string.
    """
    gw_streamlit = st.session_state["GWStreamlit"]
    application = gw_streamlit.application
    key = codify_string(input_string=f"{key_type.value}_{application}_{value}")
    return key


def _create_storage_key(value: str) -> str:
    """
    Generates a storage key by combining a predefined key type, the application name,
    and the provided value. The resulting key is codified using the `codify_string` function.

    Args:
        value (str): The value to be included in the storage key.

    Returns:
        str: A codified storage key string.

    Notes:
        - This function relies on the `st.session_state` to access the `GWStreamlit` instance
          and its associated application name.
        - The `KeyType.STORAGE.value` is used as a prefix for the storage key.
    """
    gw_streamlit = st.session_state["GWStreamlit"]
    application = gw_streamlit.application
    key = codify_string(input_string=f"{KeyType.STORAGE.value}_{application}_{value}")
    return key


def read_yaml(yaml_file: str):
    """
    Reads a YAML file and returns its contents as a Python dictionary.

    Args:
        yaml_file (str): The path to the YAML file to be read.

    Returns:
        dict: The contents of the YAML file as a dictionary.

    Raises:
        FileNotFoundError: If the specified YAML file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    with open(yaml_file, "r") as file:
        yaml_data = yaml.safe_load(file)
        return yaml_data


def get_config_path(directory, file_name: str):
    """
    Constructs and returns the full path to a configuration file based on the operating system.

    On Windows, the configuration file is stored in the AppData directory.
    On macOS, the configuration file is stored in the Application Support directory.
    Raises an OSError for unsupported operating systems.

    If the specified directory does not exist, it will be created.

    Args:
        directory (str): The name of the directory where the configuration file should be stored.
        file_name (str): The name of the configuration file. If the file name does not end with ".json",
                         ".json" will be appended to the file name.

    Returns:
        str: The full path to the configuration file.

    Raises:
        OSError: If the operating system is unsupported.
    """
    if file_name.endswith(".json"):
        config_filename = file_name
    else:
        config_filename = f"{file_name}.json"
    if platform.system() == "Windows":
        # On Windows, it's typical to store config files in the AppData directory
        config_directory = os.path.join(os.getenv("APPDATA"), directory)
    elif platform.system() == "Darwin":
        # On macOS, it's typical to store config files in the Application Support directory
        user_directory = os.path.expanduser("~/Library/Application Support/")
        config_directory = os.path.join(user_directory, "Field Framework", directory)
    else:
        raise OSError("Unsupported operating system")

    if not os.path.exists(config_directory):
        os.makedirs(config_directory)  # Create the directory if it does not exist

    return os.path.join(config_directory, config_filename)


def disabled(item: YamlModelBase) -> bool | None:
    """
    Determines whether a given item is disabled based on its attributes and session state.

    Args:
        item (YamlModelBase): An object that contains attributes `immutable` and `enabled`.

    Returns:
        bool | None:
            - `True` if the item is considered disabled.
            - `False` if the item is considered enabled.
            - `None` if no determination can be made.

    Notes:
        - The `immutable` attribute is used to fetch a boolean value indicating if the item is immutable.
        - If the `enabled` attribute is not `None`, the function checks the session state for the corresponding key.
        - If the session state key for `enabled` is `None`, the item is considered disabled.
        - Otherwise, the item is considered enabled.
    """
    disabled_value = fetch_boolean(getattr(item, "immutable", False))
    if item.enabled is not None:
        if st.session_state.get(_fetch_key(item.enabled), None) is None:
            disabled_value = True
        else:
            disabled_value = False
    return disabled_value


def fetch_boolean(value):
    """
    Converts a given value to a boolean if possible.

    Parameters:
        value (bool or str): The input value to be converted.
                             If the value is a boolean, it is returned as is.
                             If the value is a string, it is checked for "true" or "false"
                             (case-insensitive) and converted accordingly.

    Returns:
        bool: The boolean representation of the input value.
              Returns False if the input is neither a boolean nor a valid string representation.
    """
    if type(value) is bool:
        return value
    if type(value) is str:
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
    return False


def build_label(item: YamlModelBase) -> str:
    """
    Constructs a formatted label string for a given item.

    The label is built based on the item's attributes such as `label`, `language`,
    `currency`, and `required`. Additional formatting is applied to indicate
    missing required fields and to emphasize the label.

    Args:
        item (YamlModelBase): An object containing attributes used to build the label.
            - `label` (str): The base label text.
            - `language` (str, optional): The language associated with the item.
            - `currency` (str, optional): The currency code associated with the item.
            - `required` (bool): Indicates whether the item is required.
            - `code` (str): A unique code used to check for missing required fields.

    Returns:
        str: A formatted label string with additional information such as language,
        currency symbol, and required status.
    """
    label = item.label
    if item.language:
        label = f"{label} ({item.language})"
    if item.currency:
        symbol_label = f"{CURRENCY_SYMBOLS.get(item.currency.upper(), '')}"
        label = f"{label} ({symbol_label})"
    if item.required:
        if missing_required(item.code):
            label = f":red[* {label}]"
        else:
            required_label = ":red[*]"
            label = f"{required_label} {label}"

    label = f"**{label}**"
    return label


def to_list(item_value) -> list:
    """
    Converts the input value to a list. If the input is already a list, it is returned as-is.
    Otherwise, the input is wrapped in a new list.

    Args:
        item_value: The input value to be converted to a list. Can be of any type.

    Returns:
        list: A list containing the input value, or the input itself if it is already a list.
    """
    if isinstance(item_value, list):
        return item_value
    else:
        return [item_value]


def updated_edited_rows(df, edited_item):
    """
    Updates the rows of a DataFrame based on the provided edited items.

    This function takes a DataFrame and a dictionary of edited items, where the keys
    represent row indices and the values are dictionaries containing column names
    and their updated values. It modifies the DataFrame in-place by updating the
    specified rows and columns with the new values.

    Args:
        df (pd.DataFrame): The DataFrame to be updated.
        edited_item (dict): A dictionary containing the edited items.
            The structure is {row_index: {column_name: new_value}}.

    Returns:
        pd.DataFrame: The updated DataFrame with the modified rows and columns.
    """
    for key, value in edited_item.items():
        for item_key, item_value in value.items():
            df.loc[key, item_key] = item_value
    return df


def update_data_editor(*, key: str, replace_values: dict):
    """
    Updates the data editor by replacing values in the specified rows.

    Args:
        key (str): The unique identifier for the data editor instance.
        replace_values (dict): A dictionary containing the values to replace,
            where keys represent column names and values represent the new data.

    Returns:
        None
    """
    update_dataframe(key=key, update_rows=replace_values)


def update_dataframe(key: str, update_rows: dict):
    """
    Updates a DataFrame stored in Streamlit's session state by replacing its rows with new data.

    Args:
        key (str): The key used to identify the DataFrame in the session state.
                   The actual key in the session state is expected to be formatted as "{key}_df".
        update_rows (dict): A dictionary containing the new rows to be added to the DataFrame.
                            Each item in the dictionary represents a row.

    Behavior:
        - If the DataFrame associated with the given key does not exist in the session state, the function returns without making any changes.
        - The function clears all existing rows in the DataFrame.
        - It appends the new rows from `update_rows` to the cleared DataFrame.
        - Finally, the DataFrame's index is reset to ensure sequential numbering.

    Note:
        This function assumes that the DataFrame is stored in Streamlit's session state and is accessible via the key "{key}_df".
    """
    df_key = f"{key}_df"
    if st.session_state.get(df_key, None) is None:
        return

    st.session_state.get(df_key)

    original_index = st.session_state.get(df_key).index
    index_range = numpy.arange(original_index.start, original_index.stop).tolist()
    st.session_state.get(df_key).drop(index_range, inplace=True)
    for item in update_rows:
        st.session_state.get(df_key).loc[len(st.session_state.get(df_key))] = item
    st.session_state.get(df_key).reset_index(drop=True, inplace=True)


def _load_config(file_name):
    """
    Load a configuration file and update the Streamlit session state.

    Args:
        file_name (str): The name or path of the configuration file to load.
                         If the file name is relative (does not include a path),
                         the function constructs the full path using the application directory.

    Returns:
        None: Updates the Streamlit session state with the loaded configuration.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.

    Notes:
        - The function uses the `GWStreamlit` object from the Streamlit session state to determine the application directory.
        - If `file_name` is None, the function exits without performing any operations.
        - The configuration file is expected to be in JSON format.
    """
    gws = st.session_state["GWStreamlit"]
    if file_name is None:
        return
    if pathlib.Path(file_name).name == file_name:
        directory = codify_string(input_string=gws.application)
        config_path = get_config_path(directory, file_name)
    else:
        config_path = file_name
    try:
        with open(config_path, "r") as file:
            config = json.load(file)
            update_session(config)
    except FileNotFoundError:
        return


def fetch_model_input(model_code):
    """
    Fetches a model input object based on the provided model code.

    This function searches for an input object in the `GWStreamlit` session state
    using the `model_code`. It first attempts to match the `code` attribute of the
    input objects. If no match is found, it then attempts to match the `db_field`
    attribute. The function returns the matching input object if exactly one match
    is found, otherwise it returns `None`.

    Args:
        model_code (str): The code or database field identifier used to locate the model input.

    Returns:
        object or None: The matching input object if found and unique, otherwise `None`.
    """
    gws = st.session_state["GWStreamlit"]
    model = gws.yaml_model
    inputs = [item for item in model.inputs if item.code == model_code]
    if len(inputs) == 0:
        inputs = [item for item in model.inputs if item.db_field == model_code]
    if len(inputs) == 0:
        return None
    if len(inputs) == 1:
        return inputs[0]
    if len(inputs) > 1:
        return None


def update_session(config: dict, *, using_code: bool = False):
    """
    Updates the Streamlit session state based on the provided configuration dictionary.

    Args:
        config (dict): A dictionary containing key-value pairs to update the session state.
            Keys represent the identifiers for session state variables, and values are the
            corresponding data to be set.
        using_code (bool, optional): A flag indicating whether the keys in the configuration
            dictionary are derived from code-based model inputs. Defaults to False.

    Behavior:
        - Iterates through the provided configuration dictionary and updates the session state
          variables accordingly.
        - Handles special cases for keys starting with `input_` or `table_`, updating them
          using `update_data_editor` or setting date values if the type is `date_input`.
        - Ensures that unprocessed session state variables starting with `input_` are reset
          to `None` if they are not present in the processed keys and exist in the model inputs.

    Notes:
        - The function interacts with the `GWStreamlit` object stored in the session state,
          specifically its `yaml_model` attribute.
        - The `fetch_model_input` function is used to retrieve model input details when
          `using_code` is True.
        - The `update_session_state` function is used for general session state updates.

    Raises:
        KeyError: If the "GWStreamlit" object is not found in the session state.
        AttributeError: If the `yaml_model` or its attributes are not properly defined.

    Example:
        config = {
            "input_name": "John Doe",
            "input_date": "2023-01-01",
            "table_data": [1, 2, 3]
        }
        update_session(config, using_code=False)
    """
    gws = st.session_state["GWStreamlit"]
    model = gws.yaml_model
    processed_keys = []
    for key, value in config.items():
        if using_code:
            model_part = fetch_model_input(key)
            if model_part is None:
                continue
            long_key = model_part.key
        else:
            model_part = None
            long_key = key
        processed_keys.append(long_key)
        if str(long_key).startswith("input_") or str(long_key).startswith("table_"):
            if type(value) is list:
                update_data_editor(key=long_key, replace_values=value)
            elif model_part.type == "date_input":
                if value is None:
                    st.session_state[long_key] = None
                else:
                    date_format = "%Y-%m-%d"
                    date_value = datetime.strptime(value, date_format)
                    st.session_state[long_key] = date_value
            else:
                update_session_state(model_part, long_key, value)

    for key in st.session_state:
        if key.startswith("input_"):
            if key not in processed_keys and key in [item.key for item in model.inputs]:
                st.session_state[key] = None


def update_session_state(model_part, key: str, value: Any):
    """
    Updates the Streamlit session state with the provided key-value pair.
    If the `model_part` contains a `field_value` attribute and it is not None,
    the session state is updated using both the `field_value_key` from `model_part`
    and the provided key.

    Args:
        model_part (object): An object that may contain `field_value` and `field_value_key` attributes.
        key (str): The key to update in the Streamlit session state.
        value (Any): The value to associate with the given key in the session state.

    Returns:
        None
    """
    if "field_value" in model_part.__dict__.keys():
        if model_part.get("field_value") is not None:
            st.session_state[model_part["field_value_key"]] = value
            st.session_state[key] = value
    else:
        st.session_state[key] = value


def build_key_dict(*, short_key: bool = False):
    """
    Builds a dictionary mapping keys to their corresponding short keys or vice versa
    based on the `short_key` parameter.

    Args:
        short_key (bool): If True, the dictionary maps short keys to full keys.
                          If False, the dictionary maps full keys to short keys.

    Returns:
        dict: A dictionary containing mappings between keys and short keys for
              both model inputs and their columns.

    Notes:
        - This function relies on the `GWStreamlit` object stored in `st.session_state`.
        - The `GWStreamlit` object is expected to have a `model.inputs` attribute,
          where each input has `key`, `short_key`, and `columns` attributes.
    """
    key_dict = {}
    gws = st.session_state["GWStreamlit"]
    for item in gws.model.inputs:
        if short_key:
            key_dict[item.short_key] = item.key
        else:
            key_dict[item.key] = item.short_key
        for column in item.columns:
            if short_key:
                key_dict[column.short_key] = column.key
            else:
                key_dict[column.key] = column.short_key
    return key_dict


def replace_short_key(section: str, short_key_config: dict):
    """
    Replace short keys in a configuration section with their corresponding full keys.

    Args:
        section (str): The name of the configuration section to process.
        short_key_config (dict): A dictionary containing configuration data with short keys.

    Returns:
        dict: A dictionary with the short keys replaced by their corresponding full keys.
    """
    key_mapping = build_key_dict(short_key=True)
    data = short_key_config.get(section, None)
    result = replace_keys(data=data, key_mapping=key_mapping)
    return result


def replace_keys(data, key_mapping):
    """
    Recursively replaces keys in a dictionary or list based on a given key mapping.

    Args:
        data (dict | list | any): The input data, which can be a dictionary, list, or any other type.
        key_mapping (dict): A dictionary mapping old keys to new keys.

    Returns:
        dict | list | any: The transformed data with keys replaced according to the key mapping.
                           If the input is neither a dictionary nor a list, it is returned unchanged.

    Example:
        >>> data = {"a": 1, "b": {"c": 2, "d": 3}}
        >>> key_mapping = {"a": "x", "c": "y"}
        >>> replace_keys(data, key_mapping)
        {'x': 1, 'b': {'y': 2, 'd': 3}}
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # Replace the key if it exists in the key_mapping
            new_key = key_mapping.get(key, key)
            # Recursively replace keys in the value
            new_dict[new_key] = replace_keys(value, key_mapping)
        return new_dict

    elif isinstance(data, list):
        # Recursively replace keys in each item of the list
        return [replace_keys(item, key_mapping) for item in data]

    else:
        # If the value is neither a dict nor a list, return it as is
        return data


def _completed_required_fields(*, dialog: bool = False) -> bool:
    """
    Validates whether all required input fields have been completed.

    This function checks the session state for required input fields defined
    in the `yaml_model` of the `GWStreamlit` object. If any required fields
    are missing, it updates the session state with the list of missing fields,
    displays a toast notification, and returns `False`. Otherwise, it clears
    the list of missing fields and returns `True`.

    Args:
        dialog (bool, optional): A flag indicating whether the validation is
            being performed in a dialog context. Defaults to `False`.

    Returns:
        bool: `True` if all required fields are completed, `False` otherwise.
    """
    required_list = []
    gws = st.session_state["GWStreamlit"]
    model = gws.yaml_model
    for input_field in [
        model_input for model_input in model.inputs if model_input.required
    ]:
        if input_field.Required and st.session_state.get(input_field.key) is None:
            required_list.append(input_field.code)
    if len(required_list) > 0:
        st.session_state["required_fields"] = required_list
        st.toast("**Missing Required Fields**")
        return False
    else:
        st.session_state["required_fields"] = None
    return True


def _write_string(location, file_name, content, **kwargs):
    """
    Writes a string to a file at the specified location and file name, creating directories if necessary.

    Args:
        location (str): The directory path where the file will be written.
        file_name (str): The name of the file to be created.
        content (str): The content to be written to the file. If None, the function logs an error and exits.
        **kwargs: Additional optional arguments:
            - package (str): A dot-separated package path to append to the location.
            - extension (str): The file extension to append to the file name.

    Returns:
        None: This function does not return a value. It writes the content to a file and logs actions or errors.

    Logs:
        - Logs an error if the content is None or the location is invalid.
        - Logs the creation of directories if they do not exist.
        - Logs the creation of the file with its full path.

    Raises:
        None: This function handles errors internally and logs them instead of raising exceptions.
    """
    for key, value in kwargs.items():
        if key == "package":
            package_parts = value.split(".")
            for package_part in package_parts:
                location = os.path.join(location, package_part)
        if key == "extension":
            file_name = f"{file_name}.{value}"

    if content is None:
        fetch_tab("Output").write(f"File content for: {location}/{file_name} is None")
        return
    if not is_valid_filepath(location, platform="auto"):
        fetch_tab("Output").error("Source Location is an invalid path")
        return
    is_exist = os.path.exists(location)
    if not is_exist:
        os.makedirs(location)
        fetch_tab("Output").write(f"Directory created: {location}")
    with open(f"{location}/{file_name}", "w") as file:
        file.write(content)
    fetch_tab("Output").write(f"File created: {location}/{file_name}")


def _fetch_key(ui_item: Any, short_key: bool = False) -> str | None:
    """
    Recursively fetches the key or short key associated with a UI item.

    Args:
        ui_item (Any): The UI item to fetch the key for. Can be a string or an object with `key` or `short_key` attributes.
        short_key (bool, optional): If True, fetches the `short_key` attribute of the UI item. Defaults to False.

    Returns:
        str | None: The key or short key of the UI item, or None if the item cannot be resolved.
    """
    if isinstance(ui_item, str):
        item_code = codify_string(ui_item)
        gw_streamlit = st.session_state["GWStreamlit"]
        model_item = gw_streamlit.find_model_part(item_code)
        if model_item is None:
            return None
        return _fetch_key(model_item)
    else:
        if short_key:
            return ui_item.short_key
        else:
            return ui_item.key


def build_model(yaml_file) -> YamlModel | None:
    """
    Constructs a YamlModel instance from the provided YAML file data.

    Args:
        yaml_file (dict): A dictionary representing the YAML file data.
                          If None, the function returns None.

    Returns:
        YamlModel | None: A YamlModel instance created from the YAML file data,
                          or None if the input is None.

    Notes:
        - If the "rest" key is not present in the `yaml_file`, it is added
          with a value derived from the lowercase string representation of
          the "code" key in `yaml_file`.
        - The `add_code` function is called with `yaml_file` before processing.
    """
    if yaml_file is None:
        return None
    add_code(yaml_file)
    if "rest" not in yaml_file:
        yaml_file["rest"] = str(yaml_file["code"]).lower()
    model = YamlModel(yaml_file)
    return model


def add_code(ui_item, ui_type: str = None):
    """
    Enhances a UI item dictionary by adding various keys and values based on its properties.

    Args:
        ui_item (dict): A dictionary representing a UI item. Expected to contain keys such as
                        "label", "name", "unknown", "type", and "field_value".
        ui_type (str, optional): A default type to assign to the UI item if the "type" key is not present.

    Returns:
        dict: The updated UI item dictionary with additional keys:
              - "code": A capitalized version of "label", "name", or "unknown" key value.
              - "type": Assigned from `ui_type` if not already present.
              - "key": A unique key generated using `build_key`.
              - "field_value_key": A key generated for "field_value" if present.
              - "short_key": A short key derived from "code" or generated using `build_key`.
              - Additional keys added by `add_code_buttons` and `add_code_inputs`.

    Notes:
        - The function relies on external helper functions `capital_case`, `build_key`,
          `add_code_buttons`, and `add_code_inputs` to perform specific operations.
        - The "code" key is generated based on the first available key among "label", "name",
          or "unknown" in the `ui_item` dictionary.
    """
    if ui_item.get("code") is None:
        if "label" in ui_item.keys():
            ui_item["code"] = capital_case(ui_item.get("label"))
        elif "name" in ui_item.keys():
            ui_item["code"] = capital_case(ui_item.get("name"))
        else:
            ui_item["code"] = capital_case(ui_item.get("unknown"))
    if ui_item.get("type") is None:
        ui_item["type"] = ui_type
    ui_item["key"] = build_key(ui_item, short_key=False)
    if "field_value" in ui_item.keys():
        ui_item["field_value_key"] = build_key(ui_item, field_key=True)
    if ui_item.get("code") is None:
        ui_item["short_key"] = build_key(ui_item, short_key=True)
    else:
        ui_item["short_key"] = ui_item["code"]
    add_code_buttons(ui_item)
    add_code_inputs(ui_item)

    return ui_item


def add_code_buttons(ui_item):
    """
    Adds code functionality to buttons specified in the given UI item.

    This function iterates through the "buttons" key in the provided `ui_item`
    dictionary and applies the `add_code` function to each button, associating
    it with the "button" type.

    Args:
        ui_item (dict): A dictionary representing a UI item. It should contain
                        a "buttons" key with a list of button elements.

    Returns:
        None
    """
    if "buttons" in ui_item.keys():
        for button in ui_item["buttons"]:
            add_code(button, "button")


def add_code_inputs(ui_item):
    """
    Recursively adds code to input fields and their nested columns within a UI item.

    Args:
        ui_item (dict): A dictionary representing a UI item. It should contain an "inputs" key
                        with a list of input fields. Each input field can optionally have a
                        "columns" key containing a list of column dictionaries.

    Returns:
        None: This function modifies the input `ui_item` in place by calling `add_code` on
              each input field and its nested columns.
    """
    if "inputs" in ui_item.keys():
        for input_field in ui_item["inputs"]:
            add_code(input_field)
            if "columns" in input_field.keys():
                for column in input_field["columns"]:
                    add_code(column)


def build_key(ui_item, *, short_key: bool = False, field_key: bool = False) -> str:
    """
    Generates a unique key for a UI item based on its type and value.

    Args:
        ui_item (dict): A dictionary representing the UI item. It must contain
            a "type" key and either a "field_value" or "code" key depending on
            the `field_key` parameter.
        short_key (bool, optional): If True, generates a shorter key using
            only the value. Defaults to False.
        field_key (bool, optional): If True, uses the "field_value" key from
            the `ui_item` dictionary to generate the key. Otherwise, uses the
            "code" key. Defaults to False.

    Returns:
        str: A string representing the generated key. Returns an empty string
        if the value used to generate the key is None.

    Notes:
        - The `ui_type` is derived from the "type" key of the `ui_item` using
          the `independent_utils.type_to_key_type` function.
        - The `short_key` option uses `independent_utils.codify_string_title`
          to generate the key.
        - The full key includes the `ui_type`, application name, and value,
          and is generated using `independent_utils.codify_string`.
        - The application name is retrieved from the Streamlit session state
          under the "GWStreamlit" key.
    """
    ui_type = independent_utils.type_to_key_type(ui_item.get("type"))
    if field_key:
        value = ui_item.get("field_value")
    else:
        value = ui_item.get("code")
    if value is None:
        return ""
    if short_key:
        key = independent_utils.codify_string_title(value)
    else:
        gws = st.session_state["GWStreamlit"]
        application = gws.application
        key = independent_utils.codify_string(
            input_string=f"{ui_type.value}_{application}_{value}"
        )
    return key


def find_yaml_ui(yaml_file_name: str):
    """
    Searches for a YAML template in the session state based on the provided file name.

    Args:
        yaml_file_name (str): The name of the YAML file to search for.

    Returns:
        dict or None: Returns the matching YAML object if found, otherwise None.
                      Updates the session state with the selected template name
                      or sets it to None if no match is found.

    Notes:
        - The function first attempts to match the file name with the "code" field
          of the templates. If no match is found, it tries to match with the "name" field.
        - Templates are retrieved from the session state or generated using the
          `list_files` function with the specified YAML file location.
    """
    templates = st.session_state.get(
        "templates", list_files(constants.YAML_UI_LOCATION, [".yaml", ".yml"])
    )
    yaml_object_list = [
        template for template in templates if template["code"] == yaml_file_name
    ]
    if len(yaml_object_list) == 0:
        yaml_object_list = [
            template for template in templates if template["name"] == yaml_file_name
        ]

    if len(yaml_object_list) == 0:
        st.session_state["template_selection"] = None
        return
    yaml_object = yaml_object_list[0]
    st.session_state["template_selection"] = yaml_object["name"]
    return yaml_object


def find_yaml_other(yaml_file_name: str):
    """
    Loads a YAML file, updates the Streamlit session state with the template name,
    and returns the parsed YAML object.

    Args:
        yaml_file_name (str): The path to the YAML file to be loaded.

    Returns:
        dict: The parsed YAML object containing the data from the file.

    Raises:
        FileNotFoundError: If the specified YAML file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    yaml_object = load_yaml(yaml_file_name)
    st.session_state["template_selection"] = yaml_object["name"]
    return yaml_object


def list_files(directory_path, file_types: list):
    found_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_extension = pathlib.Path(file).suffix
            if file_extension in file_types:
                found_files.append(load_yaml(os.path.join(str(root), file)))

    return found_files


def load_yaml(file_path: str):
    """
    Load and parse a YAML file.

    Args:
        file_path (str): The path to the YAML file to be loaded.

    Returns:
        dict: The contents of the YAML file as a Python dictionary.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def _create_saved_state(*, short_key: bool = False, fields=False):
    """
    Creates a saved state for the application.

    This function generates a dictionary representing the saved state of the application
    based on the current session state and the input configuration defined in the `yaml_model`.

        If True, the saved state will use the short code (`item.code`) as the key.
    fields : bool, optional
        If True, the saved state will use the database field (`item.db_field`) as the key,
        provided it is defined.

        A dictionary representing the saved state of the application, where keys are determined
        based on the `short_key` and `fields` parameters, and values are processed using the
        `process_key_value` function.

    Notes
    -----
    - The function skips inputs that are not present in the session state.
    - For inputs of type "checkbox" or "toggle", a `None` value is converted to `False`.
    """

    interim_saved_dict = {}
    gws = st.session_state["GWStreamlit"]
    yaml_objects = []
    if gws.yaml_model.parent_model is not None:
        yaml_objects.append(build_model(find_yaml_ui(gws.yaml_model.parent_model)))
    yaml_objects.append(gws.yaml_model)
    for yaml_model in yaml_objects:
        for item in yaml_model.inputs:
            if item.key not in st.session_state.keys():
                continue
            value = st.session_state[item.key]
            if short_key or fields:
                save_key = item.code
                if fields and item.db_field is not None:
                    save_key = item.db_field
            else:
                save_key = item.key
            if (item.type == "checkbox" or item.type == "toggle") and value is None:
                value = False
            interim_saved_dict[save_key] = process_key_value(item.key, value)
    return interim_saved_dict


def get_save_key(gws, key, short_key):
    """
    Retrieves the save key for a given input or table key, optionally returning the short key.

    Args:
        gws: An object containing the model with inputs.
        key (str): The original key to look up, typically prefixed with `input_` or `table_`.
        short_key (bool): If True, attempts to return the short key associated with the input or table.

    Returns:
        str: The short key if `short_key` is True and a matching input or table is found;
             otherwise, returns the original key.
    """
    if short_key:
        model = gws.model
        if key.startswith("input_"):
            inputs = [item for item in model.inputs if item.key == key]
            if len(inputs) == 1:
                return inputs[0].short_key
        if key.startswith("table_"):
            inputs = [item for item in model.inputs if item.key == key]
            if len(inputs) == 1:
                return inputs[0].short_key
    return key


def process_key_value(key, value):
    """
    Processes a key-value pair based on the prefix of the key and the type of the value.

    Args:
        key (str): The key to be processed, which determines the processing logic.
                   Expected prefixes are `input_`, `table_`, and `storage_`.
        value (Any): The value associated with the key, which may be transformed or returned.

    Returns:
        Any: The processed value based on the key prefix and value type:
             - For keys starting with `input_`:
               - If the value is a date object, returns its ISO format string.
               - Otherwise, returns the value unchanged.
             - For keys starting with `table_`:
               - Returns None if the key ends with "_df".
               - If a corresponding key with "_df" exists in `st.session_state`, processes the dataframe.
             - For keys starting with `storage_`:
               - Returns the value unchanged.
             - For other keys, returns None.
    """
    if key.startswith("input_"):
        if isinstance(value, date):
            return value.isoformat()
        return value
    if key.startswith("table_"):
        if key.endswith("_df"):
            return None
        if f"{key}_df" in st.session_state:
            return process_dataframe(key)
    if key.startswith("storage_"):
        return value
    return None


def process_dataframe(key):
    """
    Processes a dataframe stored in the Streamlit session state based on the specified key.
    This function retrieves a dataframe from the Streamlit session state using the provided key,
    applies modifications such as deleting rows, adding rows, and editing rows based on the session
    state data, and returns the updated dataframe as a list of dictionaries.
    Args:
        key (str): The key used to identify the dataframe and its associated modifications in the
        Streamlit session state.
    Returns:
        list[dict]: A list of dictionaries representing the updated dataframe records, or None if
        the dataframe does not exist in the session state.
    Notes:
        - The function expects the session state to contain a dataframe under the key "{key}_df".
        - Modifications to the dataframe are applied based on the session state data under the key `key`.
        - If the dataframe is empty or the session state does not contain modification data for the key,
          the dataframe is cleared.
        - The helper functions `to_list` and `updated_edited_rows` are used for processing rows.
    """
    df_key = f"{key}_df"
    if df_key not in st.session_state:
        return None
    df = st.session_state[df_key]
    deleted_rows = []
    added_rows = []
    edited_rows = []
    if st.session_state.get(key, None) is not None:
        deleted_rows = st.session_state[key].get("deleted_rows", [])
        added_rows = st.session_state[key].get("added_rows", [])
        edited_rows = st.session_state[key].get("edited_rows", [])
    len_changes = len(deleted_rows) + len(added_rows) + len(edited_rows)
    if not df.empty or len_changes > 0:
        if len_changes > 0:
            for del_index in to_list(deleted_rows):
                df.drop(del_index, inplace=True)
            for added_item in to_list(added_rows):
                if added_item:
                    df.loc[len(df)] = added_item
            for edited_item in to_list(edited_rows):
                if edited_item:
                    updated_edited_rows(df, edited_item)
            df.reset_index(drop=True, inplace=True)
        else:
            df.drop(df.index, inplace=True)
    return df.to_dict("records")


def _fetch_configs(application_name: str):
    """
    Retrieves a list of saved configuration files for the specified application.

    Args:
        application_name (str): The name of the application whose configurations are to be fetched.

    Returns:
        list: A list of filenames (strings) of JSON configuration files found in the application's directory.

    Notes:
        - The function uses `codify_string` to generate a directory name based on the application name.
        - The configuration path is determined using `get_config_path` with the directory and a temporary file name.
        - It searches for JSON files in the directory tree starting from the parent directory of the configuration path.
    """
    file_list = []
    directory = codify_string(application_name)
    config_path = get_config_path(directory, "temp.json")
    for root, dirs, files in os.walk(os.path.dirname(config_path)):
        for file in files:
            if file.endswith(".json"):
                file_list.append(file)
    return file_list


def _save_config(application_name: str, file_name, config_data):
    """
    Saves the given configuration data to a JSON file.

    Args:
        application_name (str): The name of the application, used to determine the directory for saving the configuration file.
        file_name (str): The name of the file where the configuration data will be saved. If None, the function will return without saving.
        config_data (dict): The configuration data to be saved in JSON format.

    Returns:
        None: The function does not return any value. It writes the configuration data to a file.
    """
    if file_name is None:
        return
    directory = codify_string(application_name)
    config_path = get_config_path(directory, file_name)
    with open(config_path, "w") as file:
        json.dump(config_data, file, indent=4)


def fetch_tab(item: Any):
    """
    Fetches a tab object from the session state based on the provided item.

    Args:
        item (Any): The item used to determine the tab to fetch.
                    If `item` is a string, it is treated as the name of the tab.
                    If `item` is an object, it is expected to have a `tab` attribute
                    which specifies the name of the tab.

    Returns:
        Any: The tab object corresponding to the provided item.
             Returns `None` if the tab is not found.

    Notes:
        - The function interacts with the `st.session_state["GWStreamlit"]` object
          to retrieve the tab dictionary (`tab_dict`).
        - If the `GWStreamlit` object has a `child`, the function attempts to fetch
          the tab from the child's `tab_dict`.
        - If the `tab` attribute of the `item` is `None`, the default tab name "Main"
          is used.
    """
    if isinstance(item, str):
        tab = st.session_state["GWStreamlit"].tab_dict.get(item)
    else:
        if item is None:
            return None
        tab_name = item.tab
        if tab_name is None:
            tab_name = "Main"
        gws = st.session_state["GWStreamlit"]
        if gws.child is None:
            tab = gws.tab_dict.get(tab_name)
        else:
            tab = gws.child.tab_dict.get(tab_name)
    return tab


def _save_storage(key, value: Any):
    """
    Save a value to Streamlit's session state using the specified key.

    Parameters:
        key (str): The key under which the value will be stored. If `None`, the function does nothing.
        value (Any): The value to be stored in the session state.

    Returns:
        None
    """
    if key is None:
        return

    if key in st.session_state.keys():
        st.session_state[key] = value


def _show_info(message, tab=None):
    """
    Displays an informational message in the specified tab.

    Args:
        message (str): The informational message to display.
        tab (str, optional): The name of the tab where the message will be displayed.
            Defaults to "Output" if not provided.

    Returns:
        None
    """
    if tab is None:
        tab = "Output"
    fetch_tab(tab).info(message)


def _show_warning(message, tab=None):
    """
    Displays a warning message in the specified tab of the Streamlit application.

    Args:
        message (str): The warning message to display.
        tab (str, optional): The name of the tab where the warning should be displayed.
            Defaults to "Output" if not specified.

    Returns:
        None
    """
    if tab is None:
        tab = "Output"
    fetch_tab(tab).warning(message)


def _show_error(message, tab=None):
    """
    Displays an error message in the specified tab or the default "Output" tab.

    Args:
        message (str): The error message to display.
        tab (str, optional): The name of the tab where the error message should be displayed.
                             Defaults to "Output" if not provided.

    Returns:
        None
    """
    if tab is None:
        tab = "Output"
    fetch_tab(tab).error(message)


def capital_case(value: str) -> str:
    """
    Converts the input string to capital case.

    Args:
        value (str): The string to be converted.

    Returns:
        str: The input string converted to capital case.
    """
    return independent_utils.capital_case(value)


def construct_function(function_name):
    """
    Constructs and returns a function based on the given function name.

    This function utilizes an internal utility method to dynamically create
    or retrieve a function corresponding to the provided name.

    Args:
        function_name (str): The name of the function to construct.

    Returns:
        Callable: The constructed function object.

    Raises:
        AttributeError: If the function name does not exist in the utilities module.
        TypeError: If the provided function name is not a string.
    """
    defined_function = _utils.construct_function(function_name)
    return defined_function


def cache_item(item, *, value=None):
    """
    Cache an item's value in the application's session state.

    This function checks if the given item has caching enabled. If caching is enabled,
    it stores the item's value in the application's cache using multiple keys: `item.key`,
    `item.short_key`, and `item.code`. If no value is provided, it defaults to the value
    stored in the session state for the item's key.

    Args:
        item: An object that contains caching information and keys for storing the value.
              It must have the attributes `cache`, `key`, `short_key`, and `code`.
        value (optional): The value to be cached. If not provided, the function retrieves
                          the value from the session state using `item.key`.

    Returns:
        None
    """
    if item.cache:
        gws = st.session_state["GWStreamlit"]
        if value is None:
            value = st.session_state[item.key]
        gws.cache.set(item.key, value)
        gws.cache.set(item.short_key, value)
        gws.cache.set(item.code, value)


def dialog_css(item: YamlModel) -> str:
    """Generates a CSS style block for customizing the width of a dialog container
    and ensuring nested vertical blocks use the full available width.

    Args:
        item (YamlModel): An object containing dialog configuration, specifically
                          the width attribute. If `item` is None, a default width
                          percentage of 30% is used.

    Returns:
        str: A string containing the CSS style block to be injected into the HTML
             for styling the dialog container and nested vertical blocks."""
    if not item:
        dialog_width_percentage = "30"
    else:
        dialog_width_percentage = item.width
    css = f"""
        <style>
        /* Set the dialog container width dynamically based on the parameter */
        div[role="dialog"] {{
            width: {dialog_width_percentage}% !important;
            max-width: 100% !important;
        }}

        /* Ensure nested vertical blocks use the full available width */
        div[data-testid="stVerticalBlock"] {{
            width: 100% !important;
        }}
        </style>
        """
    return css


def missing_required(code: str):
    """
    Check if the required fields are missing.

    This function verifies whether a given code is present in the `required_fields`
    stored in the Streamlit session state. It ensures that the `required_fields`
    key exists and is not `None` before performing the check.

    code : str
        The code to check if it is missing.

    Returns
    -------
    bool
        True if the code is in the `required_fields` list, False otherwise.
    """
    """Check if the required fields are missing
    Parameters
    ----------
    code: str
        The code to check if it is missing"""
    if "required_fields" not in st.session_state.keys():
        return False
    if st.session_state["required_fields"] is None:
        return False
    if code in st.session_state["required_fields"]:
        return True
