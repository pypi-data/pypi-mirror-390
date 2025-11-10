import json
from pathlib import Path
from typing import Any

import gw_ui_streamlit._create_ui as gwu
import gw_ui_streamlit.database as gwd
import pandas as pd
import streamlit as st
from gw_ui_streamlit._utils import build_default_rows
from gw_ui_streamlit.cache import GWSCache
from gw_ui_streamlit.input_types import table_inputs
from gw_ui_streamlit.process_templates import _process_template_by_name
from gw_ui_streamlit.utils import (
    find_yaml_ui,
    find_yaml_other,
    build_model,
    _fetch_key,
    _fetch_configs,
    _completed_required_fields,
    _create_saved_state,
    _save_config,
    _load_config,
    _write_string,
    fetch_tab,
    _create_storage_key,
    _show_info,
    _show_warning,
    _show_error,
    codify_string,
    process_dataframe,
)
from gw_ui_streamlit.yaml_model import YamlModel


class GWStreamlit:
    def create_ui(self):
        """Builds the UI for the application"""
        if self.built_ui:
            return
        gwu.create_ui_title()
        gwu.create_ui_buttons()
        if not self.yaml_model.title:
            gwu.create_ui_tabs()
        gwu.create_tab_buttons()
        gwu.create_ui_inputs()
        self.built_ui = True

    def find_model_part(self, identifier: str):
        """Finds a model part by the identifier provided. The identifier can be the code or the
        label of the item. If the item is not found None is returned.
        Parameters
        ----------
        identifier: str
            Identifier of the item to find"""
        items = [
            item
            for item in self.yaml_model.inputs
            if codify_string(item.code) == codify_string(identifier)
        ]
        if len(items) == 0:
            items = [
                item for item in self.yaml_model.inputs if item.label == identifier
            ]
        if len(items) == 0:
            return None
        return items[0]

    def __init__(
        self,
        application: str = None,
        yaml_file: dict = None,
        *,
        single_application: bool = False,
    ):
        self.application = application
        self.yaml_file = yaml_file
        self.yaml_model: YamlModel = build_model(self.yaml_file)
        self.keys = []
        self.input_values = {}
        self.button_values = {}
        self.built_ui = False
        self.tab_dict = {}
        self.default_rows = build_default_rows(self)
        self.child = None
        self.saved_state: dict
        self.modal = False
        self.cache = GWSCache()
        self.single_application = single_application

    def populate(

        self,
        application: str = None,
        yaml_file: dict = None,
        *,
        single_application: bool = False,
    ):
        """
        Populates the core object with application-specific data and configurations.

        Args:
            application (str, optional): The name of the application to be populated. Defaults to None.
            yaml_file (dict, optional): A dictionary representing the YAML configuration file. Defaults to None.
            single_application (bool, optional): Flag indicating whether the core object is configured for a single application. Defaults to False.

        Attributes:
            application (str): The name of the application being populated.
            yaml_file (dict): The YAML configuration file used for building the model.
            yaml_model (Any): The model built from the provided YAML configuration file.
            default_rows (Any): Default rows generated based on the core object.
            built_ui (bool): Flag indicating whether the UI has been built. Defaults to False.

        Side Effects:
            Calls `gwu.discover_functions()` to discover application-specific functions.
        """        
        self.application = application
        self.yaml_file = yaml_file
        self.yaml_model = build_model(self.yaml_file)
        self.default_rows = build_default_rows(self)
        self.built_ui = False
        gwu.discover_functions()


def initialize(
    application: str, yaml_file_name: str, *, single_application: bool = False
):
    """
    Initialization of the GW Streamlit class

    Initializes the GWStreamlit application by loading the specified YAML file 
    and creating the user interface.
    
    Args:
        application (str): The name of the application to initialize.
        yaml_file_name (str): The name or path of the YAML file containing the UI configuration.
        single_application (bool, optional): Flag indicating whether the application is 
        running in single application mode. Defaults to False.
    
    Raises:
        FileNotFoundError: If the specified YAML file cannot be found.
    
    Notes:
        - If `yaml_file_name` is a simple file name (without a path), it will attempt 
          to locate the file using `find_yaml_ui`.
        - If `yaml_file_name` includes a path, it will attempt to locate the file 
          using `find_yaml_other`.
        - The `GWStreamlit` object in `st.session_state` is used to populate and 
          create the UI based on the loaded YAML file.
    
    Example:
        import gw_ui_streamlit.core as gws

        gws.initialize(state_name, yaml_file_name)
    """
    if Path(yaml_file_name).name == yaml_file_name:
        yaml_file = find_yaml_ui(yaml_file_name)
    else:
        yaml_file = find_yaml_other(yaml_file_name)
    st.session_state["GWStreamlit"].populate(
        application, yaml_file, single_application=single_application
    )
    st.session_state["GWStreamlit"].create_ui()


def cache() -> GWSCache:
    """
    Retrieve the cached data associated with the current Streamlit session.

    This function accesses the Streamlit session state to fetch the `GWStreamlit`
    instance and returns its `cache` attribute.

    Returns:
        GWSCache: The cache object associated with the `GWStreamlit` instance in the session state.
    Example:
        import gw_ui_streamlit.core as gws

        cache = gws.cache()
        value = cache.get(key)

    """
    gws = st.session_state["GWStreamlit"]
    return gws.cache


def required_fields(*, dialog: bool = False) -> bool:
    """
    Checks whether the required fields have been completed.

    Args:
        dialog (bool, optional): Indicates whether the check is for a dialog. 
                                 Defaults to False.

    Returns:
        bool: True if the required fields are completed, False otherwise.
    """
    return _completed_required_fields(dialog=dialog)


def fetch_key(ui_item: Any) -> str:
    """
    Retrieve the key associated with a given UI item.

    This function delegates the key-fetching logic to an internal helper function `_fetch_key`.

    Args:
        ui_item (Any): The UI item for which the key needs to be fetched.

    Returns:
        str: The key associated with the provided UI item.
    """
    return _fetch_key(ui_item)


def fetch_configs(application_name: str = None) -> list:
    """
    Fetches configuration settings for a given application.

    If no application name is provided, the function retrieves the application name
    from the Streamlit session state and uses it to fetch the configurations.

    Args:
        application_name (str, optional): The name of the application for which 
            configurations are to be fetched. Defaults to None.

    Returns:
        list: A list of configuration settings for the specified application.
    """
    if application_name is None:
        application_name = st.session_state["GWStreamlit"].application
    return _fetch_configs(application_name)


def create_saved_state(*, short_key: bool = False, fields=False):
    """
    Creates a saved state object with optional configurations.

    Args:
        short_key (bool, optional): If True, uses a shortened key format. Defaults to False.
        fields (optional): Specifies additional fields to include in the saved state. Defaults to False.

    Returns:
        The saved state object created by the underlying `_create_saved_state` function.
    """
    return _create_saved_state(short_key=short_key, fields=fields)


def save_config(file_name, config_data: None):
    """
    Save the application configuration to a file.

    Args:
        file_name (str): The name of the file where the configuration will be saved.
        config_data (dict, optional): The configuration data to be saved. If None, 
            a default saved state will be created using `create_saved_state()`.

    Raises:
        KeyError: If the "GWStreamlit" key is not found in the session state.

    Notes:
        This function retrieves the application name from the Streamlit session state 
        and uses it to save the configuration data to the specified file.
    """
    if config_data is None:
        config_data = create_saved_state()
    application_name = st.session_state["GWStreamlit"].application
    _save_config(application_name, file_name, config_data)


def load_config(file_name):
    """
    Load configuration from the specified file.

    This function serves as a wrapper for the internal `_load_config` function,
    which performs the actual loading of the configuration.

    Args:
        file_name (str): The name of the configuration file to load.

    Returns:
        None
    """
    _load_config(file_name)


def process_template_by_name(template_name, input_dict: dict, location="resources/templates"):
    """
    Processes a template by its name using the provided input dictionary and optional location.

    Args:
        template_name (str): The name of the template to process.
        input_dict (dict): A dictionary containing the input data to populate the template.
        location (str, optional): The directory path where templates are located. Defaults to "resources/templates".

    Returns:
        Any: The processed template result, as determined by the underlying `_process_template_by_name` function.
    """
    return _process_template_by_name(template_name, input_dict, location)


def write_string(location, file_name, content, **kwargs):
    """
    Writes a string to a file at the specified location.

    Args:
        location (str): The directory path where the file will be written.
        file_name (str): The name of the file to be created or overwritten.
        content (str): The string content to write into the file.
        **kwargs: Additional keyword arguments passed to the underlying `_write_string` function.

    Returns:
        None
    """
    _write_string(location, file_name, content, **kwargs)


def write_json(location, file_name, content, **kwargs):
    """
    Writes JSON content to a file.

    This function serializes the given content into a JSON string and writes it
    to a file at the specified location with the specified file name.

    Args:
        location (str): The directory path where the file will be saved.
        file_name (str): The name of the file to be created or overwritten.
        content (dict): The Python dictionary to be serialized into JSON format.
        **kwargs: Additional keyword arguments passed to the underlying `_write_string` function.

    Raises:
        TypeError: If `content` is not serializable to JSON.
        IOError: If there is an error writing the file to the specified location.

    Example:
        write_json("/path/to/directory", "data.json", {"key": "value"})
    """
    string_content = json.dumps(content)
    _write_string(location, file_name, string_content, **kwargs)

def create_storage_key(key_value: str) -> str:
    """
    Generates a storage key based on the provided key value.

    Args:
        key_value (str): The input value used to generate the storage key.

    Returns:
        str: The generated storage key.
    """
    return _create_storage_key(key_value)


def generate_image(item):
    """
    Generate an image using the GWStreamlit session state.

    This function retrieves the GWStreamlit instance from the Streamlit session state
    and uses it to generate an image based on the provided item.

    Args:
        item (Any): The input data or parameters required to generate the image.

    Returns:
        None: The function does not return a value; it performs an action.
    """
    gws = st.session_state["GWStreamlit"]
    gwu.generate_image(gws, item)


def find_model_part(identifier: str):
    """
    Retrieve a model part by its identifier from the GWStreamlit session state.

    Args:
        identifier (str): The unique identifier of the model part to retrieve.

    Returns:
        Any: The model part associated with the given identifier, as returned by the `find_model_part` method of the GWStreamlit instance.

    Raises:
        KeyError: If the "GWStreamlit" key is not present in the session state.
    """
    gws = st.session_state["GWStreamlit"]
    return gws.find_model_part(identifier)


def show_info(message, tab="Output"):
    """
    Displays an informational message in the specified tab.

    Args:
        message (str): The message to be displayed.
        tab (str, optional): The name of the tab where the message will be shown. 
                             Defaults to "Output".
    """
    _show_info(message, tab)


def show_warning(message, tab="Output"):
    """
    Displays a warning message in the specified tab.

    Args:
        message (str): The warning message to display.
        tab (str, optional): The name of the tab where the warning should be shown. 
                             Defaults to "Output".
    """
    _show_warning(message, tab)


def show_error(message, tab="Output"):
    """
    Displays an error message in the specified tab.

    Args:
        message (str): The error message to display.
        tab (str, optional): The name of the tab where the error message will be shown. 
                             Defaults to "Output".
    """
    _show_error(message, tab)


def model() -> YamlModel:
    """
    Retrieves the YAML model from the Streamlit session state.

    This function accesses the "GWStreamlit" object stored in the Streamlit
    session state and returns its associated YAML model.

    Returns:
        YamlModel: The YAML model associated with the "GWStreamlit" object
        in the session state.

    Raises:
        KeyError: If "GWStreamlit" is not found in the session state.
    """
    gws = st.session_state["GWStreamlit"]
    return gws.yaml_model


def model_inputs():
    """
    Retrieves the model inputs from the GWStreamlit object stored in the session state.

    Returns:
        dict: A dictionary containing the model inputs.
    """
    gws = st.session_state["GWStreamlit"]
    return gws.model.inputs


def value(identifier: str):
    """
    Retrieves a value from the Streamlit session state based on the given identifier.

    If the identifier corresponds to an existing model part, the function retrieves
    the value using the model part's key. Otherwise, it generates a storage key
    for the identifier and retrieves the value using that key.

    Args:
        identifier (str): The identifier used to locate the model part or generate
                          a storage key.

    Returns:
        Any: The value associated with the identifier or model part key in the
             Streamlit session state, or None if no value is found.
    """
    item = find_model_part(identifier)
    if item is None:
        key = create_storage_key(identifier)
        return st.session_state.get(key)
    else:
        return st.session_state.get(item.key)


def save_storage(key, storage_value: Any):
    """
    Saves a value to Streamlit's session state using a generated storage key.

    Args:
        key (str): The base key to be used for generating the storage key.
        storage_value (Any): The value to be stored in the session state.

    Returns:
        None
    """
    key = create_storage_key(key)
    st.session_state[key] = storage_value


def fetch_value(*, key: str = None, name: str = None):
    """
    Fetches a value from the Streamlit session state or a cached source.

    Args:
        key (str, optional): The key used to retrieve the value from the session state. 
                             If not provided, it will be derived using the `name` parameter.
        name (str, optional): The name used to derive the key if `key` is not provided.

    Returns:
        Any: The value associated with the key or name, retrieved from the session state 
             or the cache. Returns `None` if the value is not found.
    """
    if key is None:
        key = fetch_key(name)
    item_value = st.session_state.get(key)
    if item_value is None:
        gws = st.session_state["GWStreamlit"]
        if gws.cache.has_key(key):
            item_value = gws.cache.get(name)
    return item_value


def fetch_value_reset(*, key: str = None, name: str = None):
    """
    Fetches a value using the provided key and/or name, and resets the session state for the given key to None.

    Args:
        key (str, optional): The key used to fetch the value and reset the session state. Defaults to None.
        name (str, optional): The name used to fetch the value. Defaults to None.

    Returns:
        Any: The value fetched using the provided key and/or name.
    """
    return_value = fetch_value(key=key, name=name)
    if key is not None:
        st.session_state[key] = None
    return return_value


def set_value(name: str, input_value):
    """
    Sets a value in the Streamlit session state or in the GWStreamlit cache.

    If the specified `name` exists in the Streamlit session state, the function
    updates its value with `input_value`. Otherwise, it sets the value in the
    GWStreamlit cache.

    Args:
        name (str): The key name to set the value for.
        input_value: The value to be set for the specified key.

    Raises:
        KeyError: If "GWStreamlit" is not present in the Streamlit session state.
    """
    if name in st.session_state:
        st.session_state[name] = input_value
    else:
        gws = st.session_state["GWStreamlit"]
        gws.cache.set(name, input_value)


def set_session_state_by_code(code: str, value: Any):
    """
    Updates the Streamlit session state for a given model part identified by its code.

    Args:
        code (str): The unique identifier for the model part.
        value (Any): The new value to set in the session state.

    Returns:
        None: If the model part corresponding to the code is not found, the function exits without making changes.
    """
    part = find_model_part(code)
    if part is None:
        return
    key = part.key
    if key in st.session_state:
        st.session_state[key] = value


def get_model() -> YamlModel:
    """
    Retrieves the YAML model from the Streamlit session state.

    Returns:
        YamlModel: The YAML model associated with the "GWStreamlit" key in the session state.
    """
    return st.session_state["GWStreamlit"].yaml_model


def reset_inputs(*, alternate_model=None, table_only=False):
    """
    Resets the inputs in the Streamlit session state based on the provided model and configuration.

    Args:
        alternate_model (Optional[object]): An alternate model to use for resetting inputs. 
            If not provided, the default model obtained from `get_model()` will be used.
        table_only (bool): If True, only resets table inputs. Non-table inputs will remain unchanged.

    Behavior:
        - Clears or resets session state values for model inputs based on their type.
        - For non-table inputs:
            - Resets the session state value to `None` unless `table_only` is True.
            - If the input type is "source_code", resets the value to an empty string.
        - For table inputs:
            - Clears the associated DataFrame in the session state.
            - Populates the DataFrame with default rows if a default function is defined or 
              uses predefined default rows from the yaml file.
            - Resets tracking lists for added, edited, and deleted rows in the session state.

    Notes:
        - The function assumes the presence of a `GWStreamlit` object in the session state 
          and uses it to retrieve default rows for table inputs.
        - The function interacts with the session state keys dynamically based on the model inputs.
    """
    gws = st.session_state["GWStreamlit"]
    st.session_state["required_fields"] = None
    process_model = get_model()
    if alternate_model is not None:
        process_model = alternate_model
    for model_input in process_model.inputs:
        df_key = f"{model_input.key}_df"
        if model_input.type != "table":
            if not table_only:
                st.session_state[model_input.key] = None
            if model_input.type == "source_code":
                st.session_state[model_input.key] = ""
        else:
            if model_input.default_function:
                defined_function = model_input.default_function_built
                default_rows = defined_function()
            else:
                default_rows = gws.default_rows.get(model_input.label, dict())
            columns = table_inputs.build_columns(model_input)
            if model_input.key in st.session_state:
                process_dataframe(model_input.key)
                if st.session_state[model_input.key] is None:
                    return
                st.session_state[model_input.key]["deleted_rows"] = []
                st.session_state[model_input.key]["added_rows"] = []
                st.session_state[model_input.key]["edited_rows"] = []

            if df_key in st.session_state:
                df = st.session_state[df_key]
                df.drop(list(df.index.values), inplace=True)
                df.reset_index(drop=True, inplace=True)

                for default in default_rows:
                    df.loc[len(df)] = default
                df.reset_index(drop=True, inplace=True)


def get_search_model():
    """
    Retrieves the search model from the Streamlit session state.

    Returns:
        object: The search model stored in the session state, or None if 
        "search_model" is not present in the session state.
    """
    if "search_model" not in st.session_state:
        return None
    return st.session_state["search_model"]


def get_streamlit():
    """
    Returns the Streamlit module.

    This function provides access to the `streamlit` module, which is typically
    imported as `st`. It can be useful for dynamically accessing Streamlit
    functionality in a modular or encapsulated way.

    Returns:
        module: The `streamlit` module.
    """
    return st


def get_primary_code(ui_model: YamlModel):
    """
    Retrieves the primary code or label from the given UI model.

    This function iterates through the inputs of the provided `ui_model` to find
    the primary code or label. If an input item is marked as primary, its `code`
    is returned. If the input item is of type "table", the function checks its
    columns for a primary column and returns the column's `label` if found.

    Args:
        ui_model (YamlModel): The UI model containing input items and their metadata.

    Returns:
        str or None: The primary code or label if found, otherwise `None`.
    """
    for input_item in ui_model.inputs:
        if input_item.primary:
            return input_item.code
        if input_item.type == "table":
            for input_column in input_item.columns:
                if input_column.primary:
                    return input_column.label
    return None


def get_primary(ui_model: YamlModel):
    """
    Retrieve the primary input or column from the given UI model.

    This function iterates through the inputs of the provided `ui_model` to find
    the first item marked as primary. If the input is of type "table", it further
    checks the columns of the table for a primary column.

    Args:
        ui_model (YamlModel): The UI model containing inputs and their configurations.

    Returns:
        Union[InputItem, InputColumn, None]: The primary input item or column if found,
        otherwise `None`.
    """
    for input_item in ui_model.inputs:
        if input_item.primary:
            return input_item
        if input_item.type == "table":
            for input_column in input_item.columns:
                if input_column.primary:
                    return input_column
    return None


def update_record():
    """
    Updates a record in the database or data source.

    This function acts as a wrapper for the `gwd.update_record()` method,
    delegating the record update operation to the `gwd` module.

    Note:
        Ensure that the `gwd` module is properly initialized and configured
        before calling this function.

    Raises:
        Any exceptions raised by `gwd.update_record()` will propagate through
        this function.
    """
    gwd.update_record()


def delete_record():
    """
    Deletes a record using the gwd module.

    This function calls the `delete_record` method from the `gwd` module
    to perform the deletion of a record. Ensure that the `gwd` module is
    properly imported and initialized before calling this function.
    """
    gwd.delete_record()


def selectbox_dataframe(item_code, data_list):
    """
    Processes a list of data records into a DataFrame and applies a selection logic based on a model part.

    Args:
        item_code (str): The code used to identify the model part.
        data_list (list): A list of data records to be converted into a DataFrame.

    Returns:
        pd.DataFrame or None: A processed DataFrame if the model part is found; 
                              otherwise, None if the model part does not exist.
    """
    item = find_model_part(item_code)
    if item is None:
        return None
    df = pd.DataFrame.from_records(data_list)
    return process_selectbox_dataframe(item, df)


def process_selectbox_dataframe(item, data_frame):
    """
    Reorders the columns of a DataFrame based on a specified option label.

    This function modifies the order of columns in the given DataFrame by moving
    the column specified by `item.option_label` to the first position. If the
    `option_label` is not specified or does not exist in the DataFrame, the
    DataFrame remains unchanged.

    Args:
        item (object): An object containing the attribute `option_label`, which
            specifies the column name to be moved to the first position.
        data_frame (pd.DataFrame): The DataFrame whose columns are to be reordered.

    Returns:
        pd.DataFrame: The DataFrame with reordered columns, if applicable.
    """
    if item.option_label:
        cols = list(data_frame)
        cols.insert(0, cols.pop(cols.index(item.option_label)))
        data_frame = data_frame.loc[:, cols]
    return data_frame


@property
def streamlit():
    """
    Returns the Streamlit module object.

    This function provides access to the Streamlit module, allowing
    users to utilize its functionality for building interactive web
    applications.

    Returns:
        module: The Streamlit module object.
    """
    return st
