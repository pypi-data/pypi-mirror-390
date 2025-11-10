import re
from typing import Optional

import streamlit as st

from gw_ui_streamlit.constants import KeyType
from gw_ui_streamlit.utils import fetch_tab
from gw_ui_streamlit.yaml_model import YamlModelInput


def options_list(item: YamlModelInput):
    """
    Generates a dictionary containing options and a default value based on the provided `YamlModelInput`.

    Args:
        item (YamlModelInput): An object containing options and a default value. 
            - `item.options`: A list of options, each with a `value` and an optional `option_function`.
            - `item.default`: The default value for the options.

    Returns:
        dict: A dictionary with the following keys:
            - `options`: A list of option values. If `option_function` is defined, it is used to generate the options.
            - `default_value`: The default value for the options. If the provided default value is not in the options list, 
              the first option's value is used as the default.
    """
    if item.options is None:
        return {}
    defined_option_function = item.options[0].option_function
    default_value: Optional[str] = item.default
    if defined_option_function is None:
        options = [option.value for option in item.options]
        if item.default not in options:
            default_value = item.options[0].value
    else:
        options = defined_option_function()
    return {"options": options, "default_value": default_value}


def get_location(*, dialog=None, item=None, location=None):
    """
    Determines the location based on the provided arguments.

    Parameters:
    dialog (optional): An object representing a dialog. If provided, it may influence the location determination.
    item (optional): An item used to fetch the tab location if no other location is specified.
    location (optional): A predefined location. If provided, this will be returned directly.

    Returns:
    The determined location based on the provided arguments. If `location` is specified, it is returned.
    If `dialog` is provided, it returns `st`. Otherwise, it fetches the tab location using `item`.
    """
    if location is not None:
        return location
    if dialog is not None:
        return st
    else:
        return fetch_tab(item)


def codify_string(input_string: str):
    """
    Converts a given string into a codified format by replacing spaces with underscores,
    converting the string to lowercase, and removing specific patterns.

    Args:
        input_string (str): The input string to be codified. If None, the function returns None.

    Returns:
        str: The codified string with spaces replaced by underscores, converted to lowercase,
             and specific patterns removed. Returns None if the input is None.
    """
    if input_string is None:
        return None
    new_string = input_string.replace(' ', '_').lower().replace("_/_", "_")
    return new_string


def codify_string_title(input_string: str):
    """
    Converts a given string into a codified title format.

    The function performs the following transformations:
    1. Capitalizes the input string using the `capital_case` function.
    2. Replaces the '&' character with 'And'.
    3. Removes all spaces.
    4. Removes all underscores.

    Args:
        input_string (str): The string to be transformed.

    Returns:
        str: The transformed string in codified title format.
    """
    new_string = capital_case(input_string)
    new_string = new_string.replace("&", "And")
    new_string = new_string.replace(' ', '')
    new_string = new_string.replace("_", "")
    return new_string


def type_to_key_type(yaml_type) -> KeyType:
    """
    Maps a given YAML type to a corresponding KeyType enumeration.

    Args:
        yaml_type (str): The type specified in YAML configuration. 
                         Expected values include input types such as "text_input", "text_area", 
                         "code_input", "integer_input", "selectbox", "checkbox", "toggle", 
                         "date_input", "source_code", "code", "graphviz", as well as 
                         other types like "button", "tab", "storage", and "table".

    Returns:
        KeyType: The corresponding KeyType enumeration value. 
                 Returns KeyType.INPUT for input-related types, KeyType.BUTTON for "button", 
                 KeyType.TAB for "tab", KeyType.STORAGE for "storage", KeyType.TABLE for "table", 
                 and KeyType.OTHER for unrecognized types.
    """
    input_type = ["text_input", "text_area", "code_input", "integer_input", "selectbox", "checkbox", "toggle",
                  "date_input", "source_code", "code", "graphviz"]
    if yaml_type in input_type:
        return KeyType.INPUT
    elif yaml_type == "button":
        return KeyType.BUTTON
    elif yaml_type == "tab":
        return KeyType.TAB
    elif yaml_type == "storage":
        return KeyType.STORAGE
    elif yaml_type == "table":
        return KeyType.TABLE
    else:
        return KeyType.OTHER


def capital_case(value: str) -> str:
    """
    Converts a given string to capital case format.

    If the input string contains uppercase letters indicating word boundaries,
    it splits the string into words based on those boundaries and capitalizes
    each word. If no uppercase letters are found, the entire string is converted
    to title case.

    Args:
        value (str): The input string to be converted. If None, an empty string
                     is returned.

    Returns:
        str: The string converted to capital case format.
    """
    new_value = ""
    if value is None:
        return new_value
    value_list = re.findall(r'[A-Z][^A-Z]*', value)
    if len(value_list) == 0:
        return value.title()
    for word in value_list:
        new_value = f"{new_value}{word.title()}"
    return new_value


def code_format(item):
    """
    Formats the value associated with the given item's key in the Streamlit session state.

    If the item's key exists in the Streamlit session state and has a non-empty value,
    this function converts the value to lowercase and replaces spaces with underscores,
    updating the session state with the formatted value.

    Args:
        item: An object with a `key` attribute representing the key in the Streamlit session state.

    Returns:
        None
    """
    if item.key in st.session_state.keys():
        code_value = st.session_state[item.key]
        if code_value:
            st.session_state[item.key] = code_value.lower().replace(" ", "_")
