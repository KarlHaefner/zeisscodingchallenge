"""
Utility for loading and rendering Jinja2 templates.

This module provides functions to create a configured Jinja2 environment
and render templates with provided context variables. It's primarily used
for loading system prompts and other text templates for the LLM services.

Dependencies:
    - jinja2: For template loading and rendering
"""
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

def get_template_env(**options):
    """Returns a configured Jinja2 Environment.

    Creates and configures a Jinja2 environment pointing to the prompt_templates
    directory, with appropriate settings for template rendering.

    Args:
        **options: Optional keyword arguments to be compatible with Django's Jinja2 backend.

    Returns:
        Environment: A configured Jinja2 Environment instance.
    """
    templates_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'prompt_templates'
    )
    
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    return env

def render_template(template_path, **context):
    """Renders a Jinja2 template with the given context.

    Loads the specified template from the prompt_templates directory
    and renders it with the provided context variables.

    Args:
        template_path (str): Path to the template relative to the templates directory.
        **context: Variables to pass to the template for rendering.

    Returns:
        str: The rendered template as a string.
    """
    env = get_template_env()
    template = env.get_template(template_path)
    return template.render(**context)