
# src/git_template_cli/cli.py
import click
import os
import shutil
import re
import sys
from datetime import datetime
import importlib.resources as pkg_resources # <-- Crucial import for package data
from importlib.abc import Traversable # <-- Crucial import for robust copying


# Define the logical path to your templates *within the installed package*
# This means it expects 'templates' to be directly inside your 'git_template_cli' Python package
TEMPLATES_RESOURCE_PATH = "git_template_cli.templates"

# --- Helper functions (pascal_case, kebab_case) remain the same ---
def pascal_case(name):
    """Converts a string to PascalCase (e.g., my-component -> MyComponent)."""
    return "".join(word.capitalize() for word in re.split(r'[-_]', name))

def kebab_case(name):
    """Converts a string to kebab-case (e.g., MyComponent -> my-component)."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

# --- NEW: Robust Resource Copying Function ---
def copy_resource_dir(source_traversable: Traversable, destination_path: str):
    """
    Copies the contents of a Traversable directory (resource) to a filesystem path.
    This handles resources that might be inside zip files (like wheels).
    """
    os.makedirs(destination_path, exist_ok=True)
    for item in source_traversable.iterdir():
        dest_item_path = os.path.join(destination_path, item.name)
        if item.is_dir():
            copy_resource_dir(item, dest_item_path)
        else:
            with item.open('rb') as src_file:
                with open(dest_item_path, 'wb') as dst_file:
                    shutil.copyfileobj(src_file, dst_file)

# --- NEW: Helper to get the base directory for *listing* templates ---
def get_templates_base_dir_for_listing():
    """
    Returns the Traversable object for the templates directory within the package.
    Used for iterating and listing contents. Includes a fallback for local development.
    """
    try:
        # This is the primary way to access templates when installed
        return pkg_resources.files(TEMPLATES_RESOURCE_PATH)
    except FileNotFoundError:
        # Fallback for local development if running directly from source
        # and templates are not yet "packaged" via a local install.
        # This path assumes cli.py is in src/git_template_cli/ and templates is parallel to it.
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_file_dir, "templates")


# --- list_templates function updated to use Traversable for listing ---
def list_templates():
    """Lists all available templates."""
    templates_resource = get_templates_base_dir_for_listing()

    # Determine if we got a filesystem path (dev mode) or a Traversable object (installed mode)
    if isinstance(templates_resource, str):
        templates_dir_path = templates_resource
        if not os.path.isdir(templates_dir_path):
            click.echo(click.style(f"Error: Template base directory '{templates_dir_path}' does not exist. "
                                   "Please ensure 'templates/' is correctly packaged with the tool or present in source.", fg='red'), err=True)
            return []
        templates = [d for d in os.listdir(templates_dir_path) if os.path.isdir(os.path.join(templates_dir_path, d))]
    else: # It's a Traversable object from an installed package
        templates = []
        try:
            for item in templates_resource.iterdir():
                if item.is_dir():
                    templates.append(item.name)
        except Exception as e:
            click.echo(click.style(f"Error reading templates from resource: {e}", fg='red'), err=True)
            return []


    if templates:
        click.echo(click.style("\nAvailable templates:", fg='cyan'))
        for t in sorted(templates):
            click.echo(f"  - {t}")
    else:
        click.echo(click.style("\nNo templates found in the template directory.", fg='yellow'))
    return templates


# --- Main CLI Group with Welcome Message (unchanged ASCII art) ---
def display_welcome_page():
    """Displays the welcome page for the CLI tool."""
    click.clear()  # Clears the terminal screen

    # Corrected ASCII Art for "GIT TEMPLATE"
    click.echo(click.style(" ██████╗ ██╗████████╗      ", fg='green'))
    click.echo(click.style("██╔════╝ ██║╚══██╔══╝      ", fg='green'))
    click.echo(click.style("██║  ███╗██║   ██║         ", fg='green'))
    click.echo(click.style("██║   ██║██║   ██║         ", fg='green'))
    click.echo(click.style("╚██████╔╝██║   ██║         ", fg='green'))
    click.echo(click.style(" ╚═════╝ ╚═╝   ╚═╝         ", fg='green'))
    click.echo(click.style("████████╗███████╗███╗   ███╗██████╗ ██╗      █████╗ ████████╗███████╗", fg='cyan'))
    click.echo(click.style("╚══██╔══╝██╔════╝████╗ ████║██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔════╝", fg='cyan'))
    click.echo(click.style("   ██║   █████╗  ██╔████╔██║██████╔╝██║     ███████║   ██║   █████╗  ", fg='cyan'))
    click.echo(click.style("   ██║   ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██║     ██╔══██║   ██║   ██╔══╝  ", fg='cyan'))
    click.echo(click.style("   ██║   ███████╗██║ ╚═╝ ██║██║     ███████╗██║  ██║   ██║   ███████╗", fg='cyan'))
    click.echo(click.style("   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝", fg='cyan'))
    click.echo(click.style("                                                                     ", fg='cyan'))
    click.echo(click.style("                                        - By BUBU                    ", fg='green'))
    click.echo(click.style("                                                                     ", fg='cyan'))

    click.echo(click.style("\nWelcome to the Git Template CLI Tool! 🚀", fg='white'))
    click.echo("Easily generate new projects, components, or services from predefined structures.")
    click.echo(click.style("\nAvailable Commands:", fg='cyan'))
    click.echo(click.style("  • git template create <template-name> <new-item-name> [OPTIONS]", fg='green')) # Corrected display
    click.echo("    - Create a new item (e.g., component, service) from a specified template.")
    click.echo("    - Example: git template create react-component MyButton --path src/components")
    click.echo("    - Options: --path, --no-git-add, --no-git-branch")
    click.echo(click.style("  • git template list", fg='green'))
    click.echo("    - Lists all available templates.")
    click.echo("    - Example: git template list")
    click.echo(click.style("\nTo get help for a specific command:", fg='magenta'))
    click.echo("  git template <command> --help")
    click.echo("  Example: git template create --help")
    click.echo(click.style("\nPress Enter to continue or Ctrl+C to exit...", fg='yellow'))
    click.pause(info="")  # Waits for user to press Enter


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    A Git CLI tool to create new repositories or branches from predefined templates.
    """
    if ctx.invoked_subcommand is None:
        display_welcome_page()

# --- create command updated to use copy_resource_dir ---
@cli.command()
@click.argument('template_name', type=str)
@click.argument('new_item_name', type=str)
@click.option('--path', '-p', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              default='.', help="The destination path to create the new item. Defaults to current directory.")
@click.option('--no-git-add', is_flag=True, help="Do not automatically `git add` the new files.")
@click.option('--no-git-branch', is_flag=True, help="Do not automatically create a new Git branch.")
def create(template_name, new_item_name, path, no_git_add, no_git_branch): # Fixed order of args to match options
    """
    Creates a new item (e.g., component, service) from a specified template.

    Example: git template create react-component MyButton --path src/components
    """
    # Get the Traversable object for the specific template resource
    try:
        source_template_resource = pkg_resources.files(TEMPLATES_RESOURCE_PATH) / template_name
        if not source_template_resource.is_dir(): # Check if the specific template exists as a directory resource
            raise FileNotFoundError(f"Template '{template_name}' not found as a directory resource.")
    except (FileNotFoundError, ModuleNotFoundError) as e:
        # Fallback for local development if resources not packaged, or template just doesn't exist.
        # This will present the error message using the os.path approach.
        templates_base_local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        template_path_local = os.path.join(templates_base_local_path, template_name)
        click.echo(click.style(f"Error: Template '{template_name}' not found at '{template_path_local}'. "
                               f"Details: {e}", fg='red'), err=True)
        list_templates() # Call list_templates to help user see available
        sys.exit(1)


    destination_path = os.path.join(path, new_item_name)

    if os.path.exists(destination_path):
        click.echo(click.style(f"Error: Destination '{destination_path}' already exists.", fg='red'), err=True)
        sys.exit(1)

    click.echo(f"Creating '{new_item_name}' from template '{template_name}' in '{destination_path}'...")

    try:
        # Use the new copy_resource_dir function here
        copy_resource_dir(source_template_resource, destination_path)
    except Exception as e:
        click.echo(click.style(f"Error copying template files: {e}", fg='red'), err=True)
        sys.exit(1)

    # Placeholder replacement logic (remains unchanged)
    placeholders = {
        "react-component": {
            "COMPONENT_NAME": pascal_case(new_item_name),
            "component_name_kebab": kebab_case(new_item_name)
        },
        "python-service": {
            "SERVICE_NAME": new_item_name,
            "service_name_snake": new_item_name.lower().replace('-', '_')
        },
        "basic": {
            "PROJECT_NAME": new_item_name,
            "LICENSE_TYPE": "MIT License",
            "YEAR": str(datetime.now().year)
        }
    }

    template_placeholders = placeholders.get(template_name, {})

    for root, _, files in os.walk(destination_path):
        for filename in files:
            filepath = os.path.join(root, filename)

            # Rename files containing placeholders
            for original_ph, replacement_val in template_placeholders.items():
                if original_ph in filename:
                    new_filename = filename.replace(original_ph, replacement_val)
                    os.rename(filepath, os.path.join(root, new_filename))
                    filepath = os.path.join(root, new_filename)

            # Replace content inside files
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    for original_ph, replacement_val in template_placeholders.items():
                        content = content.replace(original_ph, replacement_val)
                        content = content.replace(kebab_case(original_ph), kebab_case(replacement_val))
                        content = content.replace(original_ph.lower().replace('-', '_'), replacement_val.lower().replace('-', '_'))

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                except UnicodeDecodeError:
                    click.echo(click.style(f"Skipping binary file: {filepath}", fg='yellow'))
                except Exception as e:
                    click.echo(click.style(f"Error processing file '{filepath}': {e}", fg='red'), err=True)


    click.echo(click.style(f"Successfully created '{new_item_name}'!", fg='green'))

    # Git integration (remains unchanged)
    try:
        if not no_git_branch:
            git_root_process = os.system("git rev-parse --is-inside-work-tree > /dev/null 2>&1")
            if git_root_process == 0:
                branch_name = f"feat/{kebab_case(new_item_name)}"
                click.echo(f"Creating new branch: {branch_name}...")
                os.system(f"git checkout -b {branch_name}")
            else:
                click.echo(click.style("Not a Git repository. Skipping branch creation.", fg='yellow'))
        else:
            click.echo("Skipping branch creation (--no-git-branch flag set).")

        if not no_git_add:
            git_root_process = os.system("git rev-parse --is-inside-work-tree > /dev/null 2>&1")
            if git_root_process == 0:
                click.echo(f"Adding new files to Git: {destination_path}...")
                os.system(f"git add {destination_path}")
            else:
                click.echo(click.style("Not a Git repository. Skipping `git add`.", fg='yellow'))
        else:
            click.echo("Skipping `git add` (--no-git-add flag set).")

    except Exception as e:
        click.echo(click.style(f"Warning during Git operations: {e}", fg='yellow'), err=True)

# --- list command remains unchanged ---
@cli.command()
def list():
    """Lists all available templates."""
    list_templates()

if __name__ == '__main__':
    cli()