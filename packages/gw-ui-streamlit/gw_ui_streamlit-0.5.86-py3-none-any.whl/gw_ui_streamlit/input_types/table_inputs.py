from gw_ui_streamlit.input_types.button_inputs import create_table_buttons
import streamlit as st
import pandas as pd

from gw_ui_streamlit.constants import DIALOG_TYPE, DEFAULT_DATE_FORMAT
from gw_ui_streamlit.independent_utils import  get_location, options_list
from gw_ui_streamlit.utils import construct_function, cache_item
from gw_ui_streamlit.yaml_model import YamlModelTable, YamlModelTableColumn


def generate_table(item: YamlModelTable, *, dialog=None, location=None, fields=False):
    """
    Generates a table based on the provided item and optional parameters.

    Args:
        item (YamlModelTable): The table model containing metadata and configuration for the table.
        dialog (str, optional): Specifies the dialog type. Can be one of the following:
            - None: Default behavior.
            - DIALOG_TYPE["search"]: Indicates a search dialog.
            - DIALOG_TYPE["add"]: Indicates an add dialog.
            - DIALOG_TYPE["individual"]: Indicates an individual dialog.
            Defaults to None.
        location (str, optional): Specifies the location for the table generation. Defaults to None.
        fields (bool, optional): Indicates whether to include fields in the table generation. Defaults to False.

    Returns:
        None: The function modifies the session state and generates a dataframe for the table.
    """
    gws = st.session_state["GWStreamlit"]
    if item.default_function:
        defined_function = item.default_function_function
        default_rows = defined_function()
    else:
        if dialog is None:
            default_rows = gws.default_rows.get(item.label, dict())
        elif dialog == DIALOG_TYPE["search"]:
            default_rows = {}
        elif dialog == DIALOG_TYPE["add"]:
            default_rows = {}
        elif dialog == DIALOG_TYPE["individual"]:
            default_rows = default_rows = {}
    generate_dataframe(item, default_rows, dialog=dialog, location=location, fields=fields)


def build_columns(item: YamlModelTable, *, fields=False):
    """
    Constructs a list of column names or labels based on the provided `YamlModelTable` object.

    Args:
        item (YamlModelTable): An object containing metadata about table columns and an optional function.
        fields (bool, optional): Determines whether to use database field names (`db_field`) or labels 
            for the columns. Defaults to `False`, which uses labels.

    Returns:
        list: A list of column names or labels. If `item.function` is defined, the columns are generated 
        by invoking the constructed function. Otherwise, the columns are derived from the `item.columns` 
        attribute, excluding columns of type "table".
    """
    if item.function:
        defined_function = construct_function(item.function)
        columns = defined_function()
    else:
        if fields:
            columns = [entity_item.db_field for entity_item in item.columns if entity_item.type != "table"]
        else:
            columns = [entity_item.label for entity_item in item.columns if entity_item.type != "table"]
    return columns


def build_dataframe(item, columns, default_rows):
    """
    Constructs a pandas DataFrame with specified columns and default rows, 
    and optionally sorts the DataFrame based on the order attribute of the given item.

    Args:
        item (object): An object that may contain an `order` attribute specifying 
                       the column name to sort the DataFrame by.
        columns (list): A list of column names for the DataFrame.
        default_rows (list): A list of default row data to populate the DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame constructed with the specified columns and 
                          default rows, optionally sorted by the `order` attribute 
                          of the item.
    """
    df = pd.DataFrame(columns=columns, data=default_rows)
    if item.order:
        df.sort_values(by=[item.order], inplace=True, ignore_index=True)
    return df


def generate_dataframe(item: YamlModelTable, default_rows: dict, *, dialog=None, location=None, fields=False):
    """
    Generates and displays a Streamlit DataFrame or Data Editor based on the provided item configuration.

    Args:
        item (YamlModelTable): The table configuration object containing metadata about columns, labels, and behavior.
        default_rows (dict): A dictionary specifying default rows to populate the DataFrame.
        dialog (optional): The dialog object used to determine the location for rendering the DataFrame. Defaults to None.
        location (optional): The location object used to determine where to render the DataFrame. Defaults to None.
        fields (bool, optional): A flag indicating whether to include additional fields in the column configuration. Defaults to False.

    Returns:
        None: The function modifies the Streamlit session state and renders the DataFrame or Data Editor directly.

    Raises:
        Exception: Captures and displays any errors that occur during rendering.

    Notes:
        - If `item.columns` is None, the function returns immediately without rendering.
        - The function uses `st.session_state` to store and retrieve the DataFrame for persistence across user interactions.
        - Depending on the `item.immutable` flag, either a read-only DataFrame or an editable Data Editor is displayed.
        - The `cache_item` function is called to cache the item state after rendering.
    """
    if item.columns is None:
        return

    columns = build_columns(item, fields=fields)

    df_key = f"{item.key}_df"
    if df_key in st.session_state.keys():
        df = st.session_state[df_key]
    else:
        df = build_dataframe(item, columns, default_rows)

    column_config = create_column_config(item.columns)
    column_order = [column.label for column in item.columns if not column.hidden]
    if not column_order:
        column_order = None
    st_location = get_location(dialog=dialog, item=item, location=location)
    st_location.markdown(f"**{item.label}**")
    if item.on_select_function is not None:
        select_function = item.on_select_function
    else:
        select_function = "ignore"
    st.session_state[df_key] = df
    try:
        if item.immutable:
            st_location.dataframe(
                st.session_state[df_key],
                hide_index=True,
                column_config=column_config,
                width="stretch",
                key=item.key,
                selection_mode=item.selection_mode,
                on_select=select_function,
                column_order=column_order,
            )
            if st.session_state.get(item.key) is not None:
                cache_item(item, value=st.session_state[item.key].selection)
        else:
            st_location.data_editor(
                st.session_state[df_key],
                num_rows="dynamic",
                column_config=column_config,
                width="stretch",
                key=item.key,
            )
        cache_item(item)
    except Exception as e:
        st.write(e)


def create_column_config(columns: list[YamlModelTableColumn]):
    """
    Generates a configuration dictionary for table columns based on the provided list of column definitions.

    Args:
        columns (list[YamlModelTableColumn]): A list of column definitions, where each item is an instance of 
            `YamlModelTableColumn`. Each column definition may include attributes such as `label`, `options`, 
            and other properties.

    Returns:
        dict: A dictionary representing the column configuration. The keys are column labels, and the values 
        are Streamlit column configurations such as `SelectboxColumn`, `CheckboxColumn`, `DateInputColumn`, 
        `IntegerInputColumn`, or `MultiselectColumn`.

    Notes:
        - If a column's `label` attribute is `None`, the column itself is used as the key in the configuration.
        - The function delegates the creation of specific column types (e.g., checkbox, date input, integer input, 
          multiselect) to helper functions such as `create_column_config_checkbox`, `create_column_config_date_input`, 
          etc.
        - For columns with `options`, the `options_list` function is used to extract the options and default value 
          for the column configuration.
    """
    column_config = {}
    for column_item in columns:
        column = column_item.label
        if column is None:
            column = column_item
        if column_item.options:
            options_dict = options_list(column_item)
            options = options_dict.get("options")
            default_value = options_dict.get("default_value")
            column_config[column] = st.column_config.SelectboxColumn(
                options=options, default=default_value
            )
        create_column_config_checkbox(column, column_item, column_config)
        create_column_config_date_input(column, column_item, column_config)
        create_column_config_integer_input(column, column_item, column_config)
        create_column_config_multiselect(column, column_item, column_config)
    return column_config


def create_column_config_multiselect(column, column_item, column_config):
    """
    Configures a column in a Streamlit table as a multiselect column.

    This function checks if the `column_item` type is "multiselect" and, if so,
    updates the `column_config` dictionary to configure the specified `column`
    as a ListColumn in Streamlit.

    Args:
        column (str): The name of the column to configure.
        column_item (object): An object containing metadata about the column,
            including its type.
        column_config (dict): A dictionary where column configurations are stored.

    Returns:
        None: The function modifies the `column_config` dictionary in place.
    """
    if column_item.type == "multiselect":
        column_config[column] = st.column_config.ListColumn()


def create_column_config_checkbox(column, column_item, column_config):
    """
    Configures a column as a checkbox in the Streamlit column configuration.

    This function checks if the `column_item` type is "checkbox" and updates the 
    `column_config` dictionary to set the specified `column` as a checkbox column 
    with a default value of `False`.

    Args:
        column (str): The name of the column to configure.
        column_item (object): An object containing the type information for the column.
                              It must have a `type` attribute.
        column_config (dict): A dictionary representing the column configuration 
                              where the checkbox column will be added.

    Returns:
        None: The function modifies the `column_config` dictionary in place.
    """
    if column_item.type == "checkbox":
        column_config[column] = st.column_config.CheckboxColumn(default=False)


def create_column_config_date_input(column, column_item, column_config):
    """
    Configures a Streamlit column for date input based on the provided column item.

    Args:
        column (str): The name of the column to configure.
        column_item (object): An object containing the type and date format for the column.
                              Expected to have attributes `type` and `date_format`.
        column_config (dict): A dictionary to store the column configuration.

    Returns:
        None: Updates the `column_config` dictionary in-place with the date input configuration.

    Notes:
        - If `column_item.date_format` is None, a default date format (`DEFAULT_DATE_FORMAT`) is used.
        - The column is configured using `st.column_config.DatetimeColumn` with the specified or default format.
    """
    if column_item.type == "date_input":
        date_format = column_item.date_format
        if date_format is None:
            date_format = DEFAULT_DATE_FORMAT
        column_config[column] = st.column_config.DatetimeColumn(format=date_format)


def create_column_config_integer_input(column, column_item, column_config):
    """
    Configures a column for integer input in a Streamlit application.

    This function checks the type of the column item and, if it is "integer_input",
    sets up the column configuration using Streamlit's `NumberColumn`. It defines
    the minimum and maximum values for the input based on the `Min` and `Max`
    attributes of the `column_item`. If these attributes are not provided, default
    values are used (0 for minimum and 100 for maximum). The step size is set to 1,
    and the default value is set to -1.

    Args:
        column (str): The name of the column to configure.
        column_item (object): An object representing the column item, which must
            have a `type` attribute and optionally `Min` and `Max` attributes.
        column_config (dict): A dictionary to store the column configuration.

    Returns:
        None: The function modifies the `column_config` dictionary in place.
    """
    if column_item.type == "integer_input":
        if column_item.Min is None:
            min_value = 0
        else:
            min_value = column_item.Min
        if column_item.Max is None:
            max_value = 100
        else:
            max_value = column_item.Min
        column_config[column] = st.column_config.NumberColumn(
            max_value=max_value, min_value=min_value, step=1, default=-1
        )
