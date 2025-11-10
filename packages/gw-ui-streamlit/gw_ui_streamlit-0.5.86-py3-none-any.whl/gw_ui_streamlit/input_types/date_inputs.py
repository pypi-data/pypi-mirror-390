import streamlit as st

from gw_ui_streamlit.independent_utils import get_location
from gw_ui_streamlit.constants import DIALOG_TYPE, DEFAULT_DATE_FORMAT
from gw_ui_streamlit.utils import disabled, build_label, cache_item


def generate_date_input(item, storage_dict, *, dialog=None, location=None):
    """
    Generates a date input widget for Streamlit based on the provided item configuration.

    Args:
        item (object): An object containing configuration for the date input, including 
            default value, key, date format, and other properties.
        storage_dict (dict): A dictionary used to store and retrieve values associated 
            with the input widget.
        dialog (str, optional): Specifies the dialog type (e.g., "edit"). Defaults to None.
        location (object, optional): Specifies the location where the widget should be rendered. 
            Defaults to None.

    Returns:
        None: The function updates `storage_dict` and `st.session_state` with the input value.

    Raises:
        Exception: Captures and writes any exceptions that occur during the creation of the 
            date input widget.

    Notes:
        - If `item.default_function` is provided, it is used to compute the default value.
        - The widget's state is synchronized with `st.session_state` and optionally with 
          `common_storage` for shared access.
        - The `date_format` is set to a default value if not explicitly provided in `item`.
    """
    default_value = item.default
    if item.default_function:
        defined_function = item.default_function_function
        default_value = defined_function()

    if storage_dict.get(item.key) is not None and (dialog is None or dialog == DIALOG_TYPE["edit"]):
        default_value = storage_dict[item.key]

    on_change = item.on_change_function
    disabled_input = disabled(item)
    date_format = item.date_format
    if date_format is None:
        date_format = DEFAULT_DATE_FORMAT
    if item.key not in st.session_state.keys():
        st.session_state[item.key] = default_value

    st_location = get_location(dialog=dialog, item=item, location=location)
    try:
        storage_dict[item.key] = st_location.date_input(
            build_label(item),
            key=item.key,
            on_change=on_change,
            disabled=disabled_input,
            help=item.help,
            format=date_format,
        )
        cache_item(item)
    except Exception as e:
        st.write(e)
    if item.short_key in st.session_state.get("common_storage", {}):
        st.session_state["common_storage"][item.short_key] = st.session_state[item.key]
