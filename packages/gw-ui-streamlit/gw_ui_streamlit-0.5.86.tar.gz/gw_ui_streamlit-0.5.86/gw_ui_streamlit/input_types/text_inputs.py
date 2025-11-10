import streamlit as st

from gw_ui_streamlit.independent_utils import get_location, code_format
from gw_ui_streamlit.constants import DIALOG_TYPE
from gw_ui_streamlit.utils import disabled, cache_item, build_label, missing_required
from gw_ui_streamlit.yaml_model import YamlModelInput
from gw_ui_streamlit.markdown import MarkdownStyles


def generate_text_input(item: YamlModelInput, storage_dict, *, text_area=False, dialog=None, code_input=False, location=None):
    """
    Generates a Streamlit text input or text area based on the provided parameters.

    Args:
        item (YamlModelInput): The input model containing metadata for the text input.
        storage_dict (dict): A dictionary to store the input value.
        text_area (bool, optional): If True, generates a text area instead of a text input. Defaults to False.
        dialog (str, optional): Specifies the dialog type, e.g., "edit". Defaults to None.
        code_input (bool, optional): If True, applies code formatting to the input. Defaults to False.
        location (str, optional): Specifies the location for rendering the input. Defaults to None.

    Returns:
        None: Updates the `storage_dict` with the input value and manages Streamlit session state.

    Raises:
        Exception: Captures and displays any errors that occur during input generation.

    Notes:
        - If `item.hidden` is True, the input is cached but not displayed.
        - Applies markdown styles to the input label using `MarkdownStyles`.
        - Handles default values and on-change functions based on `item` attributes.
    """
    default_value = item.default
    if item.default_function:
        defined_function = item.default_function_function
        default_value = defined_function()

    if storage_dict.get(item.key) is not None and (dialog is None or dialog == DIALOG_TYPE["edit"]):
        default_value = storage_dict[item.key]

    on_change = item.on_change_function
    if code_input:
        on_change = code_format(item)
    disabled_input = disabled(item)
    st_location = get_location(dialog=dialog, item=item, location=location)
    if item.key not in st.session_state.keys():
        st.session_state[item.key] = default_value
    if item.hidden and (dialog is not DIALOG_TYPE["edit"] and dialog is not DIALOG_TYPE["add"]):
        cache_item(item)
        return

    MarkdownStyles().apply_markdown("text")
    try:
        if text_area:
            storage_dict[item.key] = st_location.text_area(
                build_label(item),
                key=item.key,
                on_change=on_change,
                disabled=disabled_input,
                help=item.help,
            )
        else:
            storage_dict[item.key] = st_location.text_input(
                build_label(item),
                key=item.key,
                on_change=on_change,
                disabled=disabled_input,
                help=item.help,
            )
        cache_item(item)
    except Exception as e:
        st.write(e)
