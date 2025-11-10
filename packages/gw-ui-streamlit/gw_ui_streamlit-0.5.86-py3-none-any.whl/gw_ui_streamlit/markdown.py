from gw_ui_streamlit import core as gws

text_markdown = """
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
        """

selectbox_markdown = """
        <style>
        /* Style for the select container */
        div[data-baseweb="select"] {
            background-color: #fff !important;
            border: 1px solid #bfc5d2 !important;  /* Medium gray border */
            border-radius: 8px !important;          /* Increased for more noticeable rounding */
            padding: 0.5rem !important;
            font-size: 1rem !important;
            transition: box-shadow 0.2s ease-in-out;
        }

        /* Style for the inner input of the select */
        div[data-baseweb="select"] input {
            background-color: #fff !important;
            border: none !important;
            color: #333 !important;
            outline: none !important;
        }

        /* Focus effect for the select component */
        div[data-baseweb="select"]:focus-within {
            border-color: #8fa1b2 !important;  /* Slightly darker on focus */
            box-shadow: 0 0 3px rgba(0, 0, 0, 0.1) !important;
        }
        </style>
        """

class MarkdownStyles: 
    """
    MarkdownStyles is a class designed to manage and apply custom CSS styles to a Streamlit application 
    using markdown. It provides functionality to apply specific styles based on the type of markdown.

    Attributes:
        text_markdown (str): A string containing the CSS styles for text markdown.
        selectbox_markdown (str): A string containing the CSS styles for selectbox markdown.

    Methods:
        apply_markdown(style_type: str):
            Apply custom CSS styles to the Streamlit app based on the type of markdown.
            Args:
                style_type (str): The type of markdown to apply styles to. 
                                Acceptable values are "text" and "selectbox".
            Raises:
                ValueError: If an unsupported style_type is provided.
    """

    def __init__(self):
        self.text_markdown = text_markdown
        self.selectbox_markdown = selectbox_markdown

    def apply_markdown(self, style_type: str):
        """
        Applies a markdown style to the Streamlit interface based on the specified style type.

        Parameters:
        style_type (str): The type of style to apply. 
                  Accepted values are:
                  - "text": Applies the `text_markdown` style.
                  - "selectbox": Applies the `selectbox_markdown` style.

        Returns:
        None
        """
        if style_type == "text":
            gws.st.markdown(self.text_markdown, unsafe_allow_html=True)
        elif style_type == "selectbox":
            gws.st.markdown(self.selectbox_markdown, unsafe_allow_html=True)
