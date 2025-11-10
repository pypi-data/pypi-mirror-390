import streamlit as st

import gw_ui_streamlit.input_types.button_inputs as button_inputs
from gw_ui_streamlit._utils import construct_function
from gw_ui_streamlit.input_types.code_inputs import (
    generate_source_code_input,
    generate_code_input,
)
from gw_ui_streamlit.input_types.date_inputs import generate_date_input
from gw_ui_streamlit.input_types.numeric_inputs import (
    generate_integer_input,
    generate_percentage_input,
    generate_money_input,
)
from gw_ui_streamlit.input_types.other_inputs import (
    generate_checkbox,
    generate_file_upload,
    generate_image,
    generate_selectbox,
    generate_graphviz,
)
from gw_ui_streamlit.input_types.table_inputs import generate_table
from gw_ui_streamlit.input_types.text_inputs import generate_text_input
from gw_ui_streamlit.yaml_model import YamlModelInput, YamlModelTableColumn


def create_ui_buttons(*, alternate_buttons=None):
    """
    Creates UI buttons for the application.

    This function delegates the creation of UI buttons to the `button_inputs.create_ui_buttons` 
    function. It optionally accepts a list of alternate buttons to be used instead of the default ones.

    Args:
        alternate_buttons (list, optional): A list of alternate button configurations. 
            If provided, these buttons will be used instead of the default ones.

    Returns:
        None
    """
    button_inputs.create_ui_buttons(alternate_buttons=alternate_buttons)


def create_tab_buttons():
    """
    Creates tab buttons for the user interface by invoking the 
    `create_tab_buttons` method from the `button_inputs` module.

    This function serves as a wrapper to initialize and display 
    tab buttons in the application.

    Returns:
        None
    """
    button_inputs.create_tab_buttons()


def create_ui_tabs():
    """
    Creates and organizes tabs for a Streamlit application based on the configuration 
    provided in the session state and YAML model.

    The function dynamically generates tabs using the `st.tabs` method and organizes 
    them into a dictionary (`tab_dict`) for easy access. Tabs are created based on 
    the following criteria:
    - Tabs specified in the `model.inputs` with a `tab` attribute.
    - A default "Main" tab if any input does not have a `tab` attribute.
    - Tabs explicitly defined in `model.tabs`.
    - An "Output" tab added at the end.

    The resulting `tab_dict` is stored in the `GWStreamlit` object within the session 
    state for later use.

    Returns:
        None: The function modifies the session state directly.
    """
    gws = st.session_state["GWStreamlit"]
    model = gws.yaml_model
    tab_list = [{item.tab: None} for item in model.inputs if item.tab is not None]
    if len([item for item in model.inputs if item.tab is None]) > 0:
        tab_list.insert(0, {"Main": None})

    tab_dict = {}
    for item in tab_list:
        tab_dict.update(item)

    for tab in model.tabs:
        tab_dict[tab.label] = None
    tab_dict["Output"] = None

    tabs = st.tabs(tab_dict.keys())
    tab_position = 0

    for tab in tab_dict.keys():
        tab_dict[tab] = tabs[tab_position]
        tab_position += 1
    gws.tab_dict = tab_dict


def create_ui_title():
    """
    Generates and displays the UI title section using Streamlit components.

    This function retrieves data from the Streamlit session state and displays
    the title, description, concept, and developer information of the model
    stored in the session state. If any errors occur during execution, the
    exception is displayed using Streamlit's exception handling.

    Raises:
        Exception: If an error occurs while accessing session state or rendering UI components.
    """
    gws = st.session_state["GWStreamlit"]
    model = gws.yaml_model
    try:
        st.subheader(model.name, divider="blue")
        if model.description is not None:
            st.markdown(model.description)
        if model.concept is not None:
            st.write(f"Concept by: {model.concept}")
        if model.developer is not None:
            st.write(f"Developed by: {model.developer}")
    except Exception as e:
        st.exception(e)


def discover_functions(*, alternative_model=None):
    """
    Discovers and processes functions associated with buttons, inputs, and columns 
    in the given model or the default session state model.

    Args:
        alternative_model (optional): An alternative model to use instead of the 
            default session state model. Defaults to None.

    Functionality:
        - Iterates through buttons and inputs defined in the model.
        - Calls the `discover_function` method for each button and input item.
        - If an input item is of type "table", further iterates through its columns 
          and calls `discover_function` for each column.

    Dependencies:
        - Requires `st.session_state["GWStreamlit"]` to access the default model.
        - Assumes `discover_function` is a callable function available in the scope.

    Raises:
        KeyError: If "GWStreamlit" is not found in `st.session_state`.
    """
    gws = st.session_state["GWStreamlit"]
    process_model = gws.yaml_model
    if alternative_model is not None:
        process_model = alternative_model
    for button in process_model.buttons:
        discover_function(button)

    for input_item in process_model.inputs:
        discover_function(input_item)
        if input_item.type == "table":
            for column_item in input_item.columns:
                discover_function(column_item)


def discover_function(item):
    """
    Processes the given item to dynamically construct and assign functions based on its attributes.

    Args:
        item: An object with attributes that define various functions such as `on_click`, `source`, 
              `on_change`, `on_select`, `default_function`, and `options`. The object is expected 
              to have attributes that may include callable functions or function names.

    Behavior:
        - Constructs and assigns functions for `on_click`, `source`, and `on_change` attributes.
        - If `on_select` is not None and not in ["ignore", "rerun"], constructs and assigns a function 
          for `on_select`.
        - If `default_function` is not None, constructs and assigns a function for `default_function`.
        - For objects of type `YamlModelInput` or `YamlModelTableColumn` with non-empty `options` 
          containing a single option with a defined function, constructs and assigns a function for 
          the option's `function` attribute.

    Note:
        This function assumes the presence of a `construct_function` utility to dynamically create 
        callable functions from provided attributes, and specific object types such as 
        `YamlModelInput` and `YamlModelTableColumn`.
    """
    item.on_click_function = construct_function(item.on_click) if item.on_click else None
    item.source_function = construct_function(item.source) if item.source else None
    item.on_change_function = construct_function(item.on_change) if item.on_change else None
    
    if item.on_select is not None and item.on_select not in ["ignore", "rerun"]:
        item.on_select_function = construct_function(item.on_select)
    if item.default_function is not None:
        item.default_function_function = construct_function(item.default_function)
    if (
            (isinstance(item, YamlModelInput) or isinstance(item, YamlModelTableColumn))
        and item.options is not None
        and (len(item.options) == 1 and item.options[0].function is not None)
    ):
        function_name = item.options[0].function
        item.options[0].option_function = construct_function(function_name)


def create_ui_inputs(*, fields=False):
    """
    Generates UI input elements based on the configuration provided in the session state.

    Args:
        fields (bool, optional): A flag indicating whether additional field-specific 
            processing is required. Defaults to False.

    Returns:
        None: This function does not return a value. It dynamically builds UI inputs 
        using the `build_input` function and updates the session state.
    """
    gws = st.session_state["GWStreamlit"]
    for ui_item in (gws.yaml_model.inputs or []):
        build_input(ui_item, gws.input_values, fields=fields)


def build_input(ui_item, storage_dict, *, dialog=None, location=None, fields=False):
    """
    Builds a UI input element based on the type of the provided `ui_item`.

    This function dynamically generates various types of input elements 
    and updates the `storage_dict` with the corresponding key-value pair 
    for the `ui_item`. It supports multiple input types such as text, 
    code, date, selectbox, image, graphviz, checkbox, toggle, integer, 
    percentage, money, file upload, multiselect, and table.

    Args:
        ui_item (object): An object representing the UI element to be created. 
                          Must have attributes `key` and `type`.
        storage_dict (dict): A dictionary to store the state or value of the 
                             created UI element. The `ui_item.key` is used 
                             as the dictionary key.
        dialog (optional): An optional dialog object for additional context 
                           or configuration. Defaults to None.
        location (optional): An optional location parameter for positioning 
                             or context. Defaults to None.
        fields (bool, optional): A flag indicating whether to include fields 
                                 for table generation. Defaults to False.

    Returns:
        str: The key of the `ui_item` that was processed.

    Raises:
        ValueError: If the `ui_item.type` is not recognized or unsupported.

    Notes:
        - The function uses helper functions like `generate_text_input`, 
          `generate_code_input`, `generate_date_input`, etc., to create 
          specific types of UI elements.
        - Some input types, such as `toggle` and `multiselect`, are handled 
          as variations of other input types (e.g., checkbox and selectbox).
    """

    if ui_item.key not in storage_dict.keys():
        storage_dict[ui_item.key] = None

    if ui_item.type == "text_input":
        generate_text_input(ui_item, storage_dict, dialog=dialog, location=location)

    if ui_item.type == "source_code":
        generate_source_code_input(
            ui_item, storage_dict, dialog=dialog, location=location
        )

    if ui_item.type == "code":
        generate_code_input(ui_item, storage_dict, dialog=dialog, location=location)

    if ui_item.type == "code_input":
        generate_text_input(
            ui_item, storage_dict, dialog=dialog, code_input=True, location=location
        )

    if ui_item.type == "text_area":
        generate_text_input(
            ui_item, storage_dict, text_area=True, dialog=dialog, location=location
        )

    if ui_item.type == "date_input":
        generate_date_input(ui_item, storage_dict, dialog=dialog, location=location)

    if ui_item.type == "selectbox":
        generate_selectbox(ui_item, storage_dict, dialog=dialog, location=location)

    if ui_item.type == "image":
        generate_image(ui_item, dialog=dialog, location=location)

    if ui_item.type == "graphviz":
        generate_graphviz(ui_item, dialog=dialog, location=location)

    if ui_item.type == "checkbox":
        generate_checkbox(ui_item, storage_dict, dialog=dialog, location=location)

    if ui_item.type == "toggle":
        generate_checkbox(
            ui_item, storage_dict, toggle=True, dialog=dialog, location=location
        )

    if ui_item.type == "integer_input":
        generate_integer_input(ui_item, storage_dict, dialog=dialog, location=location)

    if ui_item.type == "percentage_input":
        generate_percentage_input(
            ui_item, storage_dict, dialog=dialog, location=location
        )

    if ui_item.type == "money_input":
        generate_money_input(ui_item, storage_dict, dialog=dialog, location=location)

    if ui_item.type == "file_upload":
        generate_file_upload(ui_item, storage_dict, dialog=dialog, location=location)

    if ui_item.type == "multiselect":
        generate_selectbox(
            ui_item, storage_dict, multiselect=True, dialog=dialog, location=location
        )

    if ui_item.type == "table":
        generate_table(ui_item, location=location, dialog=dialog, fields=fields)

    return ui_item.key
