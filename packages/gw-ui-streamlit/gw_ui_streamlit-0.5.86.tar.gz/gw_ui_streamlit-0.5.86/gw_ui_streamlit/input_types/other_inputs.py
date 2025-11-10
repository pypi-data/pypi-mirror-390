import streamlit as st
import pandas as pd

from gw_ui_streamlit.independent_utils import get_location, options_list
from gw_ui_streamlit.constants import DIALOG_TYPE
from gw_ui_streamlit.utils import disabled, build_label, cache_item, fetch_boolean
from gw_ui_streamlit import core as gws
from gw_ui_streamlit.yaml_model import YamlModelInput
from gw_ui_streamlit.markdown import MarkdownStyles


def generate_checkbox(item: YamlModelInput, storage_dict, *, toggle=False, dialog=None, location=None):
    """
    Generates a checkbox or toggle input element in a Streamlit application.

    Args:
        item (YamlModelInput): An object containing metadata about the input, including its key, default value, 
            default function, and optional on-change function.
        storage_dict (dict): A dictionary used to store the state of the input element.
        toggle (bool, optional): If True, generates a toggle input instead of a checkbox. Defaults to False.
        dialog (str, optional): Specifies the dialog type, which can affect the behavior of the input. Defaults to None.
        location (str, optional): Specifies the location where the input element should be rendered. Defaults to None.

    Returns:
        None: Updates the `storage_dict` with the state of the checkbox or toggle input.

    Raises:
        Exception: Captures and writes any exceptions that occur during the rendering of the input element.

    Notes:
        - The function initializes the default value of the input based on the `item` metadata or session state.
        - If a `default_function` is provided in `item`, it is executed to determine the default value.
        - The input element is rendered using Streamlit's `checkbox` or `toggle` method, depending on the `toggle` flag.
        - The `on_change_function` from `item` is passed to the input element to handle state changes.
        - The `disabled` state of the input is determined by the `disabled` function.
        - The `cache_item` function is called to cache the `item` after rendering.
    """
    if item.default is None:
        default_value = False
    else:
        default_value = item.default
    if item.default_function:
        defined_function = item.default_function
        default_value = defined_function()
    if storage_dict.get(item.key) is not None and (
        dialog is None or dialog == DIALOG_TYPE["edit"]
    ):
        default_value = storage_dict[item.key]
    on_change = item.on_change_function
    disabled_input = disabled(item)
    st_location = get_location(dialog=dialog, item=item, location=location)
    if item.key not in st.session_state.keys() or (
        default_value is not None and st.session_state[item.key] is None
    ):
        st.session_state[item.key] = default_value
    try:
        if not toggle:
            storage_dict[item.key] = st_location.checkbox(
                build_label(item),
                key=item.key,
                on_change=on_change,
                disabled=disabled_input,
            )
        else:
            storage_dict[item.key] = st_location.toggle(
                build_label(item),
                key=item.key,
                on_change=on_change,
                disabled=disabled_input,
            )
        cache_item(item)
    except Exception as e:
        st.write(e)


def generate_selectbox(item: YamlModelInput, storage_dict, *, multiselect=False, dialog=None, location=None):
    """
    Generates a Streamlit selectbox or multiselect widget based on the provided configuration.

    Args:
        item (YamlModelInput): The input model containing metadata for the selectbox.
        storage_dict (dict): A dictionary to store the selected value(s) from the widget.
        multiselect (bool, optional): If True, creates a multiselect widget instead of a selectbox. Defaults to False.
        dialog (optional): Dialog object for determining widget placement. Defaults to None.
        location (optional): Location object for determining widget placement. Defaults to None.

    Returns:
        None: The function updates the `storage_dict` with the selected value(s) and manages Streamlit session state.

    Notes:
        - If `options` is a pandas DataFrame, it processes the DataFrame to extract actual options.
        - Handles default values and updates Streamlit session state accordingly.
        - Applies markdown styles for the widget label.
        - Supports optional `on_change` callback and `help` text for the widget.
        - Ensures immutability of the widget if specified in the `item` metadata.
    """
    options_dict = options_list(item)
    options = options_dict.get("options")
    default_value = options_dict.get("default_value")
    on_change = item.on_change_function
    index_value = None
    actual_options = options
    if isinstance(options, pd.DataFrame):
        actual_options = gws.process_selectbox_dataframe(item, options)
        index_value = 0
    else:
        if options is not None and len(options) > 0 and default_value is not None:
            index_value = options.index(default_value)

    disabled_field = fetch_boolean(item.immutable)
    if item.key in storage_dict.keys():
        st.session_state[item.key] = st.session_state.get(item.key)
    if st.session_state.get(item.key) is None and default_value is not None:
        st.session_state[item.key] = default_value

    st_location = get_location(dialog=dialog, item=item, location=location)
    MarkdownStyles().apply_markdown("selectbox")
    # st.markdown(
    #     selectbox_markdown,
    #     unsafe_allow_html=True
    # )
    if multiselect:
        storage_dict[item.key] = st_location.multiselect(
            build_label(item),
            actual_options,
            key=item.key,
            on_change=on_change,
            disabled=disabled_field,
            help=item.help,
        )
    else:
        storage_dict[item.key] = st_location.selectbox(
            build_label(item),
            actual_options,
            index=index_value,
            key=item.key,
            on_change=on_change,
            disabled=disabled_field,
            help=item.help,
        )
    cache_item(item)


def generate_file_upload(item, storage_dict, *, dialog=None, location=None):
    """
    Generates a file upload widget using Streamlit and stores the uploaded file in the provided storage dictionary.

    Args:
        item (object): An object containing configuration for the file upload widget, including:
            - `key` (str): A unique key for the widget.
            - `extension` (str or list): Allowed file extensions for the upload.
            - `on_change_function` (callable, optional): A function to be called when the file upload changes.
            - `help` (str, optional): Help text to display alongside the widget.
        storage_dict (dict): A dictionary to store the uploaded file associated with the widget's key.
        dialog (object, optional): An optional dialog object used to determine the widget's location.
        location (str, optional): A string specifying the location for the widget.

    Returns:
        None: The function modifies the `storage_dict` in place to store the uploaded file.

    Raises:
        Exception: If an error occurs during the creation of the file upload widget, the exception is caught and displayed using Streamlit's `st.write`.

    Notes:
        - The function uses `get_location` to determine the widget's placement.
        - The `cache_item` function is called to cache the item after the widget is created.
    """
    st_location = get_location(dialog=dialog, item=item, location=location)
    try:
        on_change = item.on_change_function
        storage_dict[item.key] = st_location.file_uploader(
            build_label(item),
            type=item.extension,
            accept_multiple_files=False,
            key=item.key,
            on_change=on_change,
            help=item.help,
        )
        cache_item(item)
    except Exception as e:
        st.write(e)


def generate_image(item, dialog=None, location=None):
    """
    Displays an image associated with the given item in a Streamlit application.

    Args:
        item: An object containing an `Image` attribute and other relevant data.
        dialog (optional): A dialog object used to determine the location for displaying the image.
        location (optional): A specific location to override the default location for displaying the image.

    Returns:
        None: This function directly displays the image in the Streamlit application.
    """
    if item.Image is not None:
        st_location = get_location(dialog=dialog, item=item, location=location)
        caption = f"{build_label(item)} - {item.Image}"
        st_location.image(item.Image, caption=caption)


def generate_graphviz(item, dialog=None, location=None):
    """
    Generates and displays a Graphviz chart for the given item.

    Args:
        item: The item containing the key used to retrieve the graph data from the session state.
        dialog (optional): An optional dialog object used to determine the location.
        location (optional): An optional location object to override the default location.

    Returns:
        None: If the graph data is not found in the session state, the function returns without displaying anything.
    """
    st_location = get_location(dialog=dialog, item=item, location=location)
    graph = gws.st.session_state.get(item.key)
    if graph is None:
        return
    st_location.graphviz_chart(graph)
