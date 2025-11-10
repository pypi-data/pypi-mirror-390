import streamlit as st
from streamlit_ace import st_ace

from gw_ui_streamlit.independent_utils import get_location
from gw_ui_streamlit.utils import cache_item, build_label

def generate_code_input(item, storage_dict, *, dialog=None, location=None):
    """Generates a code input field in a Streamlit application with custom styling and functionality.

    Args:
        item (object): An object containing metadata for the code input, including `key` and `language`.
        storage_dict (dict): A dictionary to store the input value associated with the `item.key`.
        dialog (optional): A dialog object used for determining the location of the input field. Defaults to None.
        location (optional): A specific location object to override the default location. Defaults to None.

    Functionality:
        - Applies custom CSS styling to the input field for improved appearance and focus behavior.
        - Displays a code input field with syntax highlighting based on the specified language.
        - Stores the input value in `storage_dict` using the `item.key`.
        - Caches the `item` for future use.
        - Provides an "Edit Source" button to open a dialog for editing the source code, if the `item` is not immutable.

    Raises:
        Exception: Captures and displays any errors that occur during the execution of the function."""

    st_location = get_location(dialog=dialog, item=item, location=location)
    st_location.markdown(
        """
        <style>
        /* Apply to both input and textarea */
        div[data-baseweb="base-input"] input,
        div[data-baseweb="base-input"] textarea {
            background-color: #fff !important;
            border: 1px solid #bfc5d2 !important;
            border-radius: 8px !important; /* increase for more visible corners */
            padding: 0.5rem !important;
            font-size: 1rem !important;
            box-shadow: none !important;
            transition: box-shadow 0.2s ease-in-out;
        }

        /* Focus style for both input and textarea */
        div[data-baseweb="base-input"] input:focus,
        div[data-baseweb="base-input"] textarea:focus {
            outline: none !important;
            border-color: #8fa1b2 !important; /* Darken border on focus */
            box-shadow: 0 0 3px rgba(0, 0, 0, 0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    try:
        storage_dict[item.key] = st_location.code(
            st.session_state.get(item.key),
            language=item.language,
        )
        cache_item(item)
        if not item.immutable:
            if st_location.button("Edit Source", icon=":material/code:"):
                source_code_dialog(item, storage_dict)
    except Exception as e:
        st.write(e)



def generate_source_code_input(item, storage_dict, *, dialog=None, location=None):
    """
    Generates a Streamlit button for editing source code and triggers a dialog for source code editing.

    Args:
        item (Any): The item associated with the source code input.
        storage_dict (dict): A dictionary used for storing or managing data related to the source code.
        dialog (Optional[Any]): An optional dialog object for managing UI interactions. Defaults to None.
        location (Optional[Any]): An optional location object for specifying the placement of the button. Defaults to None.

    Returns:
        None: This function does not return a value. It creates a button in the Streamlit UI and triggers a dialog when clicked.
    """
    st_location = get_location(dialog=dialog, item=item, location=location)
    if st_location.button("Edit Source Code", icon=":material/code:"):
        source_code_dialog(item, storage_dict)

@st.dialog(title="Source Code", width="large")
def source_code_dialog(item, storage_dict):
    """Displays a dialog for editing source code using the Streamlit Ace editor.

    Args:
        item (object): An object containing configuration for the dialog. 
            Expected attributes include:
            - `default`: The default value for the code.
            - `default_function`: A boolean indicating if a default function is provided.
            - `default_function_function`: A callable function to generate the default value.
            - `key`: A unique key for the session state.
            - `source_function`: A callable function to generate the source code.
            - `hidden`: A boolean indicating if the item should be hidden.
            - `language`: The programming language for the code editor (default is "python").
        storage_dict (dict): A dictionary to store the code associated with the item's key.

    Behavior:
        - Initializes the code value from session state, source function, or default value.
        - Updates the session state with the code value.
        - Displays the code editor using the Streamlit Ace editor.
        - Applies custom styling to the dialog container and nested blocks.
        - Stores the edited code in the provided storage dictionary.

    Notes:
        - If the item is marked as hidden, the function caches the item and exits without displaying the editor.
        - Custom styling is applied using inline HTML and CSS to adjust the dialog's appearance.

    Returns:
        None"""
    default_value = item.default
    if item.default_function:
        defined_function = item.default_function_function
        default_value = defined_function()

    code = ""
    if item.key in st.session_state:
        code = st.session_state[item.key]
    elif item.source_function:
        source_function = item.source_function
        code = source_function()

    if item.key not in st.session_state.keys():
        st.session_state[item.key] = default_value
    if item.hidden:
        cache_item(item)
        return
    st.write(build_label(item))
    language = "python"
    if item.language:
        language = item.language
    st.session_state[item.key] = code
    with st.empty():
        st.markdown(
            """
            <style>
            /* Override the outer dialog container */
            div[role="dialog"] {
                width: 60% !important;     /* Set a fixed width */
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
            unsafe_allow_html=True
        )
        storage_dict[item.key] = st_ace(key=item.key,
                                        value=code,
                                        language=language,
                                        auto_update=True,
                                        show_gutter=True)

    cache_item(item)