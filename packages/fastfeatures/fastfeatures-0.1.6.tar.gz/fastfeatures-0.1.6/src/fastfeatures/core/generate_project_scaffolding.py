"""This module provides a CLI tool to generate a new FastAPI project scaffold."""
import os
import shutil
from importlib.resources import files as resources_files

import click

from fastfeatures.core.generate_settings import _generate_settings_file


def create_project_scaffold(project_name, project_description):
    """Creates the project scaffold.

    This function creates the project structure and copies the template files.

    Args:
        project_name: The name of the project.
        project_description: The description of the project.

    Returns:
        True if the project was created successfully, False otherwise.
    """
    project_root = os.getcwd()
    app_dir = os.path.join(project_root, 'app')

    # Copy template_base
    template_dir = str(resources_files('fastfeatures') / 'template_base')
    app_template_dir = os.path.join(template_dir, 'app')
    env_template_file = os.path.join(template_dir, 'env_template')

    shutil.copytree(app_template_dir, app_dir, dirs_exist_ok=True)
    shutil.copy(env_template_file, project_root)
    os.rename(os.path.join(project_root, 'env_template'), os.path.join(project_root, '.env'))

    # Replace placeholders
    for root, dirs, files in os.walk(app_dir):
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
            content = content.replace('{%PROJECT_NAME%}', project_name)
            content = content.replace('{%PROJECT_DESCRIPTION%}', project_description)
            with open(file_path, 'w') as f:
                f.write(content)

    # Create other directories
    features_dir = os.path.join(app_dir, 'features')

    dirs = [
        features_dir,
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Files to create
    files = {
        os.path.join(app_dir, '__init__.py'): '',
        os.path.join(features_dir, '__init__.py'): '',
    }

    for file_path, content in files.items():
        with open(file_path, 'w') as f:
            f.write(content)

    # Generate settings file
    env_file = os.path.join(project_root, '.env')
    output_path = os.path.join(app_dir, 'core', 'settings.py')
    _generate_settings_file(env_file, output_path, '__')

    return True


@click.command()
def generate_project_scaffolding_cli():
    """CLI tool to generate a new FastAPI project scaffold."""
    project_root = os.getcwd()
    app_dir = os.path.join(project_root, 'app')

    # Safety check: abort if 'app' folder already exists
    if os.path.exists(app_dir):
        click.echo(
            f"Error: An 'app' directory already exists in the current directory ({project_root}). Aborting "
            f"scaffolding to prevent data loss.",
            err=True)
        return

    click.echo("This command will create a new FastAPI project scaffold in the current directory.")
    if not click.confirm("Do you want to continue?"):
        return

    project_name = ""
    while not project_name:
        project_name = click.prompt('Project name', type=str)
        if not project_name:
            click.echo("Project name cannot be empty. Please provide a value.", err=True)

    project_description = ""
    while not project_description:
        project_description = click.prompt('Project description', type=str)
        if not project_description:
            click.echo("Project description cannot be empty. Please provide a value.", err=True)

    if create_project_scaffold(project_name, project_description):
        click.echo(f"Successfully created project scaffold for '{project_name}'")


if __name__ == '__main__':
    generate_project_scaffolding_cli()
