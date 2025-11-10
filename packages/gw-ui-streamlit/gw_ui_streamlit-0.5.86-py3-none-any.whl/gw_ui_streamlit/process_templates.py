from jinja2 import FileSystemLoader, Environment, select_autoescape, TemplateNotFound

from gw_ui_streamlit.utils import fetch_tab


def _process_template_by_name(template_name, input_dict: dict, location):
    """
    Processes a template by its name using the Jinja2 templating engine.

    Args:
        template_name (str): The name of the template file to be processed.
        input_dict (dict): A dictionary containing the data to be rendered into the template.
        location (str): The directory path where the template files are located.

    Returns:
        str: The rendered template as a string, or None if the template is not found.

    Raises:
        TemplateNotFound: If the specified template cannot be found in the given location.
    """
    env = Environment(
            loader=FileSystemLoader(location),
            autoescape=select_autoescape(),
            trim_blocks=True,
    )
    template_result = None
    try:
        template = env.get_template(template_name)
        template_result = template.render(input_dict)
    except TemplateNotFound:
        fetch_tab("Output").warning(f"Template - {template_name} was not found")

    return template_result
