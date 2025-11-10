import gw_ui_streamlit._create_ui as _create_ui
import gw_ui_streamlit.input_types.table_inputs as table_inputs
import streamlit as st

from gw_ui_streamlit.constants import LOGO_LOCATION

"""Exposes some of the private _create_ui functions"""

def build_dataframe(item, columns, default_rows):
    df = table_inputs.build_dataframe(item, columns, default_rows)
    return df

def discover_functions(*, alternative_model=None):
    """
    Discover and register functions for the UI.

    This function utilizes the `_create_ui.discover_functions` method to 
    discover and register functions that are used in the UI. It optionally 
    accepts an alternative model to be used during the discovery process.

    Args:
        alternative_model (optional): An alternative model object to be 
            used for function discovery. Defaults to None.

    Returns:
        None
    """
    _create_ui.discover_functions(alternative_model=alternative_model)


def create_logo():
    """
    Displays a logo in the Streamlit application.

    This function constructs the file path to the logo image using the 
    predefined `LOGO_LOCATION` variable and displays the logo using 
    Streamlit's `st.logo()` method.

    Raises:
        NameError: If `LOGO_LOCATION` is not defined.
    """
    path = f"{LOGO_LOCATION}/logo.png"
    st.logo(path)

