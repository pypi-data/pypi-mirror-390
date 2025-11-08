"""This module provides a CLI tool to generate a new feature."""
import os
import re
import shutil
from importlib.resources import files as resources_files

import click


def to_snake_case(name):
    """Converts a string to snake_case.

    Args:
        name: The string to convert.

    Returns:
        The snake_cased string.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(" ", "_").replace("-", "_")


def to_pascal_case(name):
    """Converts a string to PascalCase.

    Args:
        name: The string to convert.

    Returns:
        The PascalCased string.
    """
    return "".join(word.capitalize() for word in to_snake_case(name).split("_"))


def to_camel_case(name):
    """Converts a string to camelCase.

    Args:
        name: The string to convert.

    Returns:
        The camelCased string.
    """
    snake_case = to_snake_case(name)
    parts = snake_case.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def create_feature(feature_name) -> bool:
    """Creates a new feature.

    This function copies the template_feature directory to a new feature directory
    and replaces the placeholders with the new feature name.

    Args:
        feature_name: The name of the feature to create.
    """
    project_root = os.getcwd()
    app_dir = os.path.join(project_root, 'app')
    features_dir = os.path.join(app_dir, 'features')

    snake_case_name = to_snake_case(feature_name)
    pascal_case_name = to_pascal_case(feature_name)
    camel_case_name = to_camel_case(feature_name)

    feature_dir = os.path.join(features_dir, snake_case_name)

    # Safety check: abort if feature directory already exists
    if os.path.exists(feature_dir):
        click.echo(f"Error: A feature with the name '{feature_name}' already exists at {feature_dir}. Aborting.",
                   err=True)
        return False

    # Copy template_feature
    template_dir = str(resources_files('fastfeatures') / 'template_feature')
    shutil.copytree(template_dir, feature_dir)

    # Rename files
    os.rename(os.path.join(feature_dir, 'models', 'feature_name.py'),
              os.path.join(feature_dir, 'models', f'{snake_case_name}.py'))
    os.rename(os.path.join(feature_dir, 'services', 'feature_name_services.py'),
              os.path.join(feature_dir, 'services', f'{snake_case_name}_services.py'))

    # Replace placeholders
    for root, dirs, files in os.walk(feature_dir):
        for file in files:
            if file.endswith('.pyc'):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
            except UnicodeDecodeError:
                click.echo(f"Warning: Could not decode file {file_path} as UTF-8. Skipping.", err=True)
                continue
            content = content.replace('feature_name', snake_case_name)
            content = content.replace('FeatureName', pascal_case_name)
            content = content.replace('featureName', camel_case_name)
            with open(file_path, 'w') as f:
                f.write(content)

    return True


@click.command()
def generate_feature_cli():
    """CLI tool to generate a new feature."""
    feature_name = ""
    while not feature_name:
        feature_name = click.prompt('Feature name', type=str)
        if not feature_name:
            click.echo("Feature name cannot be empty. Please provide a value.", err=True)

    if create_feature(feature_name):
        click.echo(f"Successfully created feature '{feature_name}'")
    else:
        click.echo(
            message=f"Error creating feature '{feature_name}'",
            err = True,
        )

if __name__ == '__main__':
    generate_feature_cli()
