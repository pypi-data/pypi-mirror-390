import streamlit as st

from gw_ui_streamlit.independent_utils import get_location
from gw_ui_streamlit.constants import ButtonLevel
from gw_ui_streamlit.utils import fetch_tab, construct_function


def create_ui_buttons(*, alternate_buttons=None):
    """
    Creates a set of UI buttons within a Streamlit container. The buttons are displayed in a row of columns,
    and their behavior and appearance are determined by the provided or default configuration.

    Args:
        alternate_buttons (list, optional): A list of button objects to be used instead of the default buttons
            from the Streamlit session state. Each button object should have attributes such as `label`, `key`,
            `on_click_function`, `variant`, `icon`, and `level`.

    Raises:
        Exception: If an error occurs while rendering a button, the exception is displayed using `st.exception`.

    Notes:
        - If `alternate_buttons` is not provided, the function retrieves the default buttons from the 
          `GWStreamlit` object stored in the Streamlit session state.
        - Buttons with a `level` equal to `ButtonLevel.tab.value` are excluded from rendering.
        - Each button is displayed in one of the columns, and the layout adjusts based on the number of buttons.
        - The `icon` attribute of a button is prefixed with `:material/` if it is not `None`.

    Example:
        create_ui_buttons(alternate_buttons=my_custom_buttons)
    """
    with st.container():
        columns = st.columns([1, 1, 1, 1, 1])
        column_index = 0
        if alternate_buttons is not None:
            buttons = alternate_buttons
        else:
            gws = st.session_state["GWStreamlit"]
            buttons = [item for item in gws.yaml_model.buttons if item.level != ButtonLevel.tab.value]
        for button in buttons:
            with columns[column_index]:
                try:
                    on_click = button.on_click_function
                    if button.icon is None:
                        icon = None
                    else:
                        icon = f":material/{button.icon}:"
                    st.button(
                        f"{button.label}",
                        key=button.key,
                        on_click=on_click,
                        type=button.variant.value,
                        width="content",
                        icon=icon
                    )
                except Exception as e:
                    st.exception(e)
            column_index += 1


def create_tab_buttons():
    """
    Creates tab-specific buttons in a Streamlit application based on the configuration 
    provided in the session state. Buttons are grouped by tabs and displayed in a 
    container with columns.

    The function retrieves button definitions from the `GWStreamlit` object stored in 
    the session state, filters them by their level and tab, and dynamically generates 
    buttons with specified properties such as label, icon, and click behavior.

    Returns:
        None: If no buttons are defined for tabs, the function exits early.

    Notes:
        - Buttons are displayed in reverse order within each tab.
        - Duplicate tabs are removed from the list before processing.
        - Each button's click behavior is constructed using the `construct_function` utility.

    Raises:
        KeyError: If the `GWStreamlit` object is not found in the session state.

    Dependencies:
        - `fetch_tab`: A utility function to fetch or create a tab container.
        - `construct_function`: A utility function to construct the button's click behavior.
        - `ButtonLevel`: Enum defining button levels (e.g., tab level).
        - `st`: Streamlit module for UI components.

    Example:
        # Assuming `GWStreamlit` is properly initialized in the session state:
        create_tab_buttons()
    """
    gws = st.session_state["GWStreamlit"]
    button_tab_list = [
        item.tab for item in gws.yaml_model.buttons if item.level == ButtonLevel.tab.value
    ]
    button_tab_list = list(set(button_tab_list))  # Remove the duplicates
    if len(button_tab_list) == 0:
        return
    for tab in button_tab_list:
        with fetch_tab(tab):
            with st.empty():
                with st.container():
                    columns = st.columns([1, 1, 1, 1, 1])
                    column_index = 4
                    button_list = [
                        item
                        for item in gws.yaml_model.buttons
                        if item.tab == tab and item.level == ButtonLevel.tab.value
                    ]
                    for button in list(reversed(button_list)):
                        with columns[column_index]:
                            if button.icon is None:
                                icon = None
                            else:
                                icon = f":material/{button.icon}:"
                            on_click = button.on_click_function
                            st.button(
                                f"{button.label}",
                                key=button.key,
                                on_click=on_click,
                                type=button.variant.value,
                                width="content",
                                icon=icon
                            )
                        column_index -= 1


def create_table_buttons(*, table_item, dialog=None, location):
    """
    Creates a set of buttons for a table item and displays them in a Streamlit application.

    Args:
        table_item (object): The table item containing button definitions. 
                             Expected to have a `Buttons` attribute which is a list of button objects.
                             Each button object should have attributes like `Level`, `icon`, `label`, `key`, 
                             `OnClick`, and `variant`.
        dialog (object, optional): An optional dialog object used to determine the location of the buttons.
                                   Defaults to None.
        location (object): The location object used to determine where the buttons should be displayed.

    Behavior:
        - Filters the buttons from `table_item.Buttons` based on their `Level` attribute, 
          ensuring only buttons with `Level == ButtonLevel.table` are included.
        - Displays the buttons in a row of columns using Streamlit's `st.columns`.
        - Each button is configured with its label, key, click handler, type, container width, and icon.
        - The `get_location` function is used to determine the Streamlit location for each button.
        - The `construct_function` function is used to construct the click handler for each button.

    Notes:
        - The `icon` attribute of a button is prefixed with `:material/` if it is not None.
        - Buttons are displayed in reverse order of their appearance in the `button_list`.
        - The `column_index` determines the column placement of each button, starting from the last column.

    Raises:
        Any exceptions raised by `get_location` or `construct_function` will propagate to the caller.

    Returns:
        None
    """
    columns = st.columns([1, 1, 1, 1, 1])
    column_index = 4
    button_list = [
        item
        for item in table_item.buttons if item.Level == ButtonLevel.table.value
    ]

    for button in list(reversed(button_list)):
        st_location = get_location(dialog=dialog, item=button, location=location)
        with columns[column_index]:
            if button.icon is None:
                icon = None
            else:
                icon = f":material/{button.icon}:"
            on_click = construct_function(button.OnClick)
            st_location.button(
                f"{button.label}",
                key=button.key,
                on_click=on_click,
                type=button.variant.value,
                width="content",
                icon=icon
            )
        column_index -= 1
