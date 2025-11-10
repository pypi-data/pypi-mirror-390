import json
import math

import requests
from gw_settings_management.setting_management import get_endpoint

import gw_ui_streamlit._create_ui as create_ui
import gw_ui_streamlit.core as gws
from gw_ui_streamlit.constants import DIALOG_TYPE
from gw_ui_streamlit.utils import (
    construct_function,
    find_yaml_ui,
    build_model,
    update_session,
    dialog_css,
)
from gw_ui_streamlit.yaml_model import YamlModelTable


@gws.st.dialog(title="Add Row", width="large")
def table_row_add_dialog(table_input, dialog_values={}):
    """
    Displays a dialog for adding a new row to a table and processes user inputs.

    Args:
        table_input (object): The table object containing column definitions and dialog settings.
        dialog_values (dict, optional): A dictionary to store user input values. Defaults to an empty dictionary.

    Behavior:
        - Initializes dialog inputs from the session state if available.
        - Sets the dialog anchor to the first column if not already set.
        - Constructs input fields for each column in the table, excluding the anchor column.
        - Handles special cases for columns of type "table" by creating nested table inputs.
        - Adds a submit button at the bottom of the dialog to process and update the table data.

    Returns:
        None: The function modifies the session state and table data directly.
    """
    if "dialog_inputs" not in gws.st.session_state:
        dialog_inputs = []
    else:
        dialog_inputs = gws.st.session_state["dialog_inputs"]
    if dialog_values is None:
        return
    #
    # Set the Dialog Anchor to the first column if it is not set
    #
    if table_input.dialog_anchor is not None:
        column = next(
            item
            for item in table_input.columns
            if item.code == table_input.dialog_anchor
        )
        create_ui.build_input(column, dialog_values, dialog=DIALOG_TYPE["add"])
        process_dialog_inputs(table_input)
    #
    # Construct the placeholders for the rest of the inputs
    #
    placeholder = gws.st.empty()
    container = placeholder.container(border=True)
    #
    # Generate the rest of the inputs in the container
    #
    for column in table_input.columns:
        if table_input.dialog_inputs is not None:
            if dialog_inputs == "all" or column.code in dialog_inputs:
                if column.code != table_input.dialog_anchor:
                    create_ui.build_input(
                        column,
                        dialog_values,
                        dialog=DIALOG_TYPE["add"],
                        location=container,
                    )
        else:
            if column.code != table_input.dialog_anchor:
                if column.type == "table":
                    table_model = YamlModelTable(column.yaml_input_dict)
                    create_ui.build_input(
                        table_model,
                        dialog_values,
                        dialog=DIALOG_TYPE["add"],
                        location=container,
                    )
                else:
                    create_ui.build_input(
                        column,
                        dialog_values,
                        dialog=DIALOG_TYPE["add"],
                        location=container,
                    )
    #
    # Add the submit button to the bottom of the dialog
    #
    if gws.st.button("Submit"):
        update_df(table_input, dialog_values)
        gws.st.rerun()


@gws.st.dialog(title="Edit Row", width="large")
def table_row_edit_dialog(table_input, row, selected_index, dialog_values):
    """
    Displays a dialog for editing a row in a table and updates the table data upon submission.

    Args:
        table_input (Table): The table object containing the data and column definitions.
        row (dict): The data of the row to be edited, represented as a dictionary.
        selected_index (int): The index of the row being edited in the table.
        dialog_values (dict or None): A dictionary containing the initial values for the dialog inputs.
                                      If None, the dialog will be initialized with values from the row.

    Behavior:
        - Initializes dialog input values based on the row data and column definitions if `dialog_values` is None.
        - Builds UI inputs for each column using the `create_ui.build_input` method.
        - Updates the table data with the edited values when the "Submit" button is clicked.
        - Calls `process_dialog_inputs` to handle additional dialog input processing.

    Notes:
        - The function uses `gws.st.rerun()` to refresh the Streamlit app state after updates.
        - The `convert_value` function is used to ensure proper formatting of values for the dialog inputs.
    """
    if dialog_values is None:
        gws.st.rerun()
    for column in table_input.columns:
        if column.key not in dialog_values:
            value = row.get(column.label)
            value = convert_value(column, value)
            dialog_values[column.key] = value
        create_ui.build_input(column, dialog_values, dialog=DIALOG_TYPE["edit"])

    if gws.st.button("Submit"):
        update_df(table_input, dialog_values, selected_index)
        gws.st.rerun()

    process_dialog_inputs(table_input)


@gws.st.dialog(title="Search", width="large")
def search_dialog(yaml_file_code: str, dialog_values={}):
    """
    Builds and displays a search dialog UI based on a YAML configuration file.

    Args:
        yaml_file_code (str): The code or identifier for the YAML file containing the UI configuration.
        dialog_values (dict, optional): A dictionary of pre-filled values for the dialog inputs. Defaults to an empty dictionary.

    Functionality:
        - Parses the YAML file to extract UI configuration.
        - Constructs a model based on the parsed YAML object.
        - Discovers and registers functions for the UI components.
        - Stores the constructed model in the Streamlit session state.
        - Creates UI buttons based on the model's button definitions.
        - Builds input fields for the dialog using the model's input definitions.
        - Handles table input selection, fetches the selected row data from a REST endpoint, and triggers a Streamlit rerun.

    Notes:
        - The function assumes the existence of helper functions such as `find_yaml_ui`, `build_model`, `create_ui.discover_functions`,
          `create_ui.create_ui_buttons`, `create_ui.build_input`, and `fetch_selected_row`.
        - The function interacts with Streamlit's session state for storing and retrieving data.
        - REST endpoint construction is based on the model's `rest` and `rest_get` attributes.
    """
    yaml_object = find_yaml_ui(yaml_file_code)
    model = build_model(yaml_object)
    create_ui.discover_functions(alternative_model=model)
    gws.get_streamlit().session_state["search_model"] = model
    create_ui.create_ui_buttons(alternate_buttons=model.buttons)
    for item_input in model.inputs:
        create_ui.build_input(
            item_input, dialog_values, dialog=DIALOG_TYPE["search"], fields=True
        )

    model = gws.get_streamlit().session_state["search_model"]
    model_input = next(item for item in model.inputs if item.type == "table")
    key = model_input.key
    if (
        key in gws.get_streamlit().session_state
        and gws.get_streamlit().session_state[key] is not None
    ):
        selected = gws.get_streamlit().session_state[key].selection
        if len(selected["rows"]) > 0:
            rest_endpoint = f"/{gws.model().rest}/"
            if gws.model().rest_get is not None:
                rest_endpoint = f"/{gws.model().rest}/{gws.model().rest_get}/"
            fetch_selected_row(rest_endpoint)
            gws.st.rerun()


@gws.st.dialog(title="Individual", width="large")
def individual_dialog(yaml_file_code: str, dialog_values={}):
    """
    Constructs and displays a dialog UI based on a YAML configuration file.

    Args:
        yaml_file_code (str): The code or identifier for the YAML file containing the UI configuration.
        dialog_values (dict, optional): A dictionary of pre-filled values for the dialog inputs. Defaults to an empty dictionary.

    Functionality:
        - Parses the YAML file to extract UI configuration.
        - Builds a model representation of the UI using the extracted YAML object.
        - Discovers and registers functions associated with the model.
        - Stores the model in the Streamlit session state under the key "individual_model".
        - Creates UI buttons based on the model's button definitions.
        - Iterates through the model's inputs and builds corresponding UI elements, using the provided dialog values.

    Note:
        This function is designed to work with Streamlit and assumes the presence of specific modules and utilities such as `find_yaml_ui`, `build_model`, `create_ui`, and `gws.get_streamlit()`.
    """
    yaml_object = find_yaml_ui(yaml_file_code)
    model = build_model(yaml_object)
    create_ui.discover_functions(alternative_model=model)
    gws.get_streamlit().session_state["individual_model"] = model
    create_ui.create_ui_buttons(alternate_buttons=model.buttons)
    for item_input in model.inputs:
        create_ui.build_input(
            item_input, dialog_values, dialog=DIALOG_TYPE["individual"]
        )


def dialog_search(yaml_code: str):
    """
    Handles the dialog search functionality by either resetting inputs with an existing search model
    or building a new model from the provided YAML code. It also applies custom CSS styling and
    initializes the search dialog.

    Args:
        yaml_code (str): A string containing the YAML code used to define the UI structure.

    Behavior:
        - If a "search_model" exists in the Streamlit session state, it resets the inputs using the
          alternate model.
        - If no "search_model" exists, it parses the YAML code to create a new model.
        - Applies custom CSS styling for the dialog UI.
        - Initializes the search dialog with the provided YAML code and dialog values.

    Returns:
        None
    """
    if "search_model" in gws.st.session_state:
        model = gws.get_streamlit().session_state["search_model"]
        gws.reset_inputs(alternate_model=model)
    else:
        yaml_object = find_yaml_ui(yaml_code)
        model = build_model(yaml_object)
    dialog_values = {}
    css = dialog_css(model)
    gws.st.markdown(css, unsafe_allow_html=True)
    search_dialog(yaml_code, dialog_values)


def dialog_individual(yaml_code: str):
    """
    Handles the creation and display of an individual dialog UI based on the provided YAML code.

    This function checks if an "individual_model" exists in the Streamlit session state. If it does,
    it retrieves the model and resets the inputs using the alternate model. Otherwise, it parses the
    provided YAML code to build a new model. The function then applies custom CSS styling and renders
    the individual dialog UI.

    Args:
        yaml_code (str): A string containing the YAML code that defines the UI structure.

    Returns:
        None
    """
    if "individual_model" in gws.st.session_state:
        model = gws.get_streamlit().session_state["individual_model"]
        gws.reset_inputs(alternate_model=model)
    else:
        yaml_object = find_yaml_ui(yaml_code)
        model = build_model(yaml_object)
    dialog_values = {}
    css = dialog_css(model)
    gws.st.markdown(css, unsafe_allow_html=True)
    individual_dialog(yaml_code, dialog_values)


def convert_value(column, value):
    """
    Converts and updates the value based on the column type and its expected format.

    Args:
        column (object): An object representing the column, expected to have attributes `key` and `type`.
        value (any): The value to be converted. Can be of various types such as float, integer, string, or boolean.

    Returns:
        any: The converted value based on the column type. If no conversion is performed, the original value is returned.

    Behavior:
        - If the value is a float and NaN, it is converted to `None` and stored in the session state.
        - For columns of type "integer_input", the value is converted to an integer if not `None` and stored in the session state.
        - For columns of type "checkbox", the value is converted to a boolean based on its string representation or numeric value
          and stored in the session state.
        - If no specific conversion is applicable, the original value is returned.
    """
    if type(value) is float and math.isnan(value):
        value = None
        gws.st.session_state[column.key] = value
    if column.type == "integer_input" and value is not None:
        value = int(value)
        gws.st.session_state[column.key] = value
        return value

    if column.type == "checkbox" and value is not None:
        if type(value) is bool:
            ...
        elif value.lower() == "false" or value.lower() == "no" or value == "0":
            value = False
        elif value.lower() == "true" or value.lower() == "yes" or value == "1":
            value = True
        gws.st.session_state[column.key] = value
        return value

    return value


def update_df(process_input, dialog_values, index=-1, *, use_fields=False):
    """
    Updates a DataFrame stored in the session state with new or modified data.
    Args:
        process_input (object): An object containing metadata about the DataFrame,including its columns and key for session state lookup.
        dialog_values (dict): A dictionary of values to update in the DataFrame, where keys correspond to column keys and values are the new data.
        index (int, optional): The index of the row to update. Defaults to -1, which appends a new row to the DataFrame.
        use_fields (bool, optional): If True, uses the `db_field` attribute of columns for key mapping instead of their labels. Defaults to False.
    Returns:
        None: The function modifies the DataFrame in place within the session state.
    Notes:
        - The `process_input.columns` attribute is expected to contain column metadata with `key`, `label`, and optionally `db_field` attributes.
        - The DataFrame is retrieved from the session state using the key `"{process_input.key}_df"`.
        - If `index` is -1, a new row is appended to the DataFrame. Otherwise, the row at the specified index is updated.
    """

    key_mapping = {}
    for column in process_input.columns:
        key_mapping[column.key] = column.label
        if use_fields and column.db_field is not None:
            key_mapping[column.key] = column.db_field

    updated_data = {
        key_mapping.get(key, key): value for key, value in dialog_values.items()
    }
    df = gws.st.session_state[f"{process_input.key}_df"]
    if index == -1:
        df.loc[len(df)] = updated_data
    else:
        df.loc[index] = updated_data


def process_dialog_inputs(table_input):
    """
    Processes dialog inputs from the given table input and executes a constructed function
    if applicable. The function is cached in the session state to avoid redundant construction.

    Args:
        table_input: An object containing dialog inputs. It is expected to have a
                     `dialog_inputs` attribute.

    Behavior:
        - If `table_input.dialog_inputs` is not None:
            - Checks if "dialog_input_function" exists in the session state.
            - If not, constructs a function using `construct_function` and stores it in the session state.
            - Executes the constructed function if it is not None.
        - If `table_input.dialog_inputs` is None:
            - Sets `gws.st.session_state["dialog_inputs"]` to "all".
    """
    if table_input.dialog_inputs is not None:
        if "dialog_input_function" not in gws.st.session_state:
            function = construct_function(table_input.dialog_inputs)
            gws.st.session_state["dialog_input_function"] = function
        else:
            function = gws.st.session_state["dialog_input_function"]
        if function is not None:
            function()
    else:
        gws.st.session_state["dialog_inputs"] = "all"


def build_query():
    """
    Constructs a query based on the current session state and model inputs.

    This function retrieves the search model from the session state and builds
    a query selector and fields list based on the model's inputs. It processes
    inputs of different types (non-table and table) to generate a dictionary
    containing the selector and fields, which is then serialized into a JSON string.

    Returns:
        str: A JSON string representing the query selector and fields.
    """
    model = gws.get_streamlit().session_state["search_model"]
    selector = {}
    fields = []
    for model_input in [item for item in model.inputs if item.type != "table"]:
        value = gws.get_streamlit().session_state.get(model_input.key)
        field = model_input.db_field
        if field is None:
            field = model_input.code
        if value is not None:
            selector[field] = value

    for model_input in [item for item in model.inputs if item.type == "table"]:
        for column in model_input.columns:
            if column.db_field is not None:
                fields.append(column.db_field)
            else:
                fields.append(column.code)

    selector_dict = {"fields": fields, "selector": selector}

    selector_json = json.dumps(selector_dict)
    return selector_json


def dialog_perform_search():
    """
    Executes a search operation using a specified query and updates the associated data table.

    This function builds a query using `build_query()`, retrieves the search model from the
    Streamlit session state, and performs a REST API call to fetch search results. The results
    are processed and used to update the corresponding data table in the session state.

    Steps:
    1. Build a query using `build_query()`.
    2. Retrieve the search model and its associated table input from the Streamlit session state.
    3. Clear the existing data in the table's DataFrame.
    4. Perform a REST API call to fetch search results based on the query.
    5. Process the search results to include `id` and `rev` fields if present.
    6. Update the table's DataFrame with the processed search results.

    Note:
    - The function assumes the presence of a `search_model` in the Streamlit session state.
    - The REST endpoint for the search operation is derived from the model's `rest` attribute.
    - The function modifies the DataFrame associated with the table input directly.

    Raises:
    - KeyError: If required keys are missing in the session state or search results.
    - ValueError: If the search results cannot be parsed or processed.

    Dependencies:
    - `build_query()`: Constructs the query for the search operation.
    - `get_endpoint()`: Resolves the REST endpoint URL.
    - `update_df()`: Updates the DataFrame with new data.

    """
    selector_json = build_query()
    model = gws.get_streamlit().session_state["search_model"]
    model_input = next(item for item in model.inputs if item.type == "table")
    rest_endpoint = gws.model().rest
    df = gws.get_streamlit().session_state[f"{model_input.key}_df"]
    df.drop(list(df.index.values), inplace=True)
    endpoint_rest = get_endpoint(f"{rest_endpoint}/search/{selector_json}")
    results = requests.get(endpoint_rest)
    results_list = json.loads(results.text)
    for process_item in results_list:
        if "_id" in process_item:
            process_item["id"] = process_item["_id"]
        if "_rev" in process_item:
            process_item["rev"] = process_item["_rev"]
    process_input = next((item for item in model.inputs if item.type == "table"), None)
    for result_item in results_list:
        update_df(process_input, result_item, use_fields=True)


def fetch_selected_row(endpoint: str):
    """
    Fetches the selected row from a table in the Streamlit session state and retrieves
    additional data from a specified endpoint based on the primary code of the selected row.

    Args:
        endpoint (str): The base URL of the endpoint to fetch additional data.

    Returns:
        None: Updates the Streamlit session state with the fetched data.

    Behavior:
        - Retrieves the table input model from the Streamlit session state.
        - Identifies the selected row in the table.
        - Extracts the primary code from the selected row.
        - Constructs the endpoint URL using the primary code.
        - Sends a GET request to the constructed endpoint URL.
        - Parses the response JSON and updates the Streamlit session state with the fetched data.

    Notes:
        - If no row is selected or the response from the endpoint is empty, the function returns without updating the session state.
        - Handles both list and dictionary responses from the endpoint.
    """
    model = gws.get_streamlit().session_state["search_model"]
    model_input = next(item for item in model.inputs if item.type == "table")
    key = model_input.key
    selected = gws.get_streamlit().session_state[key].selection
    if selected is None or len(selected["rows"]) == 0:
        return
    selected_index = selected["rows"][0]
    df = gws.get_streamlit().session_state[f"{key}_df"]
    row = df.iloc[selected_index].to_dict()
    primary_code = gws.get_primary_code(model)
    if endpoint.endswith("/"):
        endpoint_rest = get_endpoint(f"{endpoint}{row.get(primary_code)}")
    else:
        endpoint_rest = get_endpoint(f"{endpoint}/{row.get(primary_code)}")
    document = requests.get(endpoint_rest)
    document_list = json.loads(document.text)
    if document_list is None or len(document_list) == 0:
        return
    if isinstance(document_list, list):
        document_dict = document_list[0]
    if isinstance(document_list, dict):
        document_dict = document_list
    update_session(document_dict, using_code=True)


def add_table_row_dialog(table_code: str):
    """
    Opens a dialog for adding a row to a table based on the provided table code.

    This function initializes dialog values, retrieves the search model from the
    session state if available, and identifies the table input process associated
    with the given table code. It sets up the session state for each column in the
    table input process and applies custom CSS styling for the dialog. Finally, it
    invokes the `table_row_add_dialog` function to display the dialog.

    Args:
        table_code (str): The code identifying the table to which a row will be added.

    Returns:
        None
    """
    dialog_values = {}
    if "search_model" in gws.get_streamlit().session_state:
        model = gws.get_streamlit().session_state["search_model"]
    else:
        model = None
    process_input = next(
        (
            item
            for item in gws.model().inputs
            if item.code == table_code and item.type == "table"
        ),
        None,
    )
    if process_input is not None:
        for column in process_input.columns:
            if column.type != "table":
                gws.st.session_state[column.key] = None
    css = dialog_css(model)
    gws.st.markdown(css, unsafe_allow_html=True)
    table_row_add_dialog(process_input, dialog_values)


def edit_table_row_dialog(table_code: str):
    """Opens a dialog for editing a selected row in a table.

    This function retrieves the selected row from a table based on the provided table code,
    populates the session state with the row's data, and displays a dialog for editing the row.
    It also applies custom styling to the dialog for better appearance.

    Args:
        table_code (str): The code identifying the table to edit.

    Returns:
        None: If no row is selected or the selection is empty, the function exits early.

    Notes:
        - The function assumes the existence of a session state key for the table's selection
          and data frame (`<key>` and `<key>_df`).
        - Custom CSS is injected to override the dialog's width and styling.
        - The `table_row_edit_dialog` function is called to handle the actual editing process."""
    dialog_values = {}
    key = gws.fetch_key(table_code)
    selected = gws.st.session_state[key].selection
    if selected is None or len(selected["rows"]) == 0:
        return
    selected_index = selected["rows"][0]
    df = gws.st.session_state[f"{key}_df"]
    row = df.iloc[selected_index].to_dict()
    model = gws.get_model()
    process_input = None
    for model_input in model.inputs:
        if model_input.type == "table" and model_input.code == table_code:
            process_input = model_input
    for column in process_input.columns:
        gws.st.session_state[column.key] = row.get(column.label)
    gws.st.markdown(
        """
        <style>
        /* Override the outer dialog container */
        div[role="dialog"] {
            width: 30% !important;     /* Set a fixed width */
            max-width: 90% !important;   /* Or use a percentage if you prefer */
        }

        /* Override nested blocks with fixed width attributes */
        div[data-testid="stVerticalBlock"] {
            width: 100% !important;      /* Use full available width */
        }
        /* If there are other elements with a fixed width attribute, adjust them as well.
           For example, if a specific element has width="704", you might override it like this: */
        div[data-testid="stVerticalBlock"][width] {
            width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    table_row_edit_dialog(process_input, row, selected_index, dialog_values)
