import streamlit as st

from gw_ui_streamlit.independent_utils import get_location
from gw_ui_streamlit.utils import disabled, fetch_boolean, build_label, cache_item
from gw_ui_streamlit.yaml_model import YamlModelInput


def generate_integer_input(item: YamlModelInput, storage_dict, *, dialog=None, location=None):
    """
    Generates a Streamlit integer input field based on the provided configuration.

    Args:
        item (YamlModelInput): The input configuration object containing properties such as 
            `min`, `max`, `key`, `on_change_function`, `immutable`, and `help`.
        storage_dict (dict): A dictionary to store the value of the input field.
        dialog (optional): An optional dialog object used to determine the location of the input field.
        location (optional): An optional location object used to determine the placement of the input field.

    Raises:
        Exception: If an error occurs during the creation of the input field, the exception is caught 
            and displayed using `st.write`.

    Notes:
        - The `min_value` and `max_value` are derived from the `item` object, defaulting to 0 and 100 
          respectively if not provided.
        - The `disabled` state of the input field is determined by the `item.immutable` property.
        - The `on_change` callback function is executed when the input value changes.
        - The input field is cached using the `cache_item` function for optimization.
    """
    on_change = item.on_change_function
    disabled_input = disabled(item)

    if item.min:
        min_value = item.min
    else:
        min_value = 0

    if item.max:
        max_value = item.max
    else:
        max_value = 100

    st_location = get_location(dialog=dialog, item=item, location=location)

    try:
        on_change = item.on_change_function
        disabled_field = fetch_boolean(item.immutable)
        storage_dict[item.key] = st_location.number_input(
            build_label(item),
            key=item.key,
            step=1,
            min_value=min_value,
            max_value=max_value,
            on_change=on_change,
            disabled=disabled_field,
            help=item.help,
        )
        cache_item(item)
    except Exception as e:
        st.write(e)


def generate_percentage_input(item: YamlModelInput, storage_dict, *, dialog=None, location=None):
    """
    Generates a percentage input field using Streamlit's number_input widget.

    Args:
        item (YamlModelInput): An object containing metadata for the input field, 
            including label, min/max values, help text, and on-change function.
        storage_dict (dict): A dictionary to store the value of the input field, 
            keyed by `item.key`.
        dialog (optional): An optional dialog object for context-specific input placement.
        location (optional): An optional location object for input placement.

    Raises:
        Exception: Captures and displays any errors that occur during the creation 
            of the input field.

    Notes:
        - The `min_value` defaults to 0.00 if not specified in `item.min`.
        - The `max_value` defaults to 100.00 if not specified in `item.max`.
        - The `disabled` state of the input field is determined by the `item.immutable` property.
        - The `on_change` function is triggered when the input value changes.
    """
    on_change = item.on_change_function
    disabled_input = disabled(item)

    if item.min:
        min_value = float(item.min)
    else:
        min_value = float(0.00)

    if item.max:
        max_value = item.max
    else:
        max_value = float(100.00)

    st_location = get_location(dialog=dialog, item=item, location=location)

    try:
        on_change = item.on_change_function
        disabled_field = fetch_boolean(item.immutable)
        storage_dict[item.key] = st_location.number_input(
            build_label(item),
            key=item.key,
            step=float(1),
            min_value=min_value,
            max_value=max_value,
            on_change=on_change,
            disabled=disabled_field,
            help=item.help,
        )
        cache_item(item)
    except Exception as e:
        st.write(e)


def generate_money_input(item: YamlModelInput, storage_dict, *, dialog=None, location=None):
    """
    Generates a numeric input field for monetary values in a Streamlit application.

    Args:
        item (YamlModelInput): An object containing metadata for the input field, such as 
            its key, label, minimum and maximum values, and other properties.
        storage_dict (dict): A dictionary to store the value of the input field, keyed by `item.key`.
        dialog (Optional): An optional dialog object for contextual input placement. Defaults to None.
        location (Optional): An optional location object for contextual input placement. Defaults to None.

    Raises:
        Exception: Captures and writes any exception that occurs during the creation of the input field.

    Notes:
        - The `item.min` and `item.max` properties are used to define the range of acceptable values.
        - The `item.on_change_function` is executed when the input value changes.
        - The `item.immutable` property determines whether the input field is disabled.
        - The `item.help` property provides a tooltip or help text for the input field.
        - The `cache_item` function is called to cache the input metadata for later use.
    """
    on_change = item.on_change_function
    disabled_input = disabled(item)

    if item.min:
        min_value = float(item.min)
    else:
        min_value = float(0.00)

    if item.max:
        max_value = item.max
    else:
        max_value = None

    st_location = get_location(dialog=dialog, item=item, location=location)

    try:
        on_change = item.on_change_function
        disabled_field = fetch_boolean(item.immutable)
        storage_dict[item.key] = st_location.number_input(
            build_label(item),
            key=item.key,
            step=float(1),
            min_value=min_value,
            max_value=max_value,
            on_change=on_change,
            disabled=disabled_field,
            help=item.help,
        )
        cache_item(item)
    except Exception as e:
        st.write(e)
