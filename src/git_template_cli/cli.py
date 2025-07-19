# git_template_cli.py
import click
import os
import shutil
import re
import sys
from datetime import datetime

# Define the base directory for your templates
TEMPLATE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# --- Helper functions (pascal_case, kebab_case, list_templates) remain the same ---

def pascal_case(name):
    """Converts a string to PascalCase (e.g., my-component -> MyComponent)."""
    return "".join(word.capitalize() for word in re.split(r'[-_]', name))

def kebab_case(name):
    """Converts a string to kebab-case (e.g., MyComponent -> my-component)."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

def list_templates():
    """Helper function to list available templates."""
    if not os.path.isdir(TEMPLATE_BASE_DIR):
        click.echo(click.style(f"Error: Template base directory '{TEMPLATE_BASE_DIR}' does not exist.", fg='red'))
        return []

    templates = [d for d in os.listdir(TEMPLATE_BASE_DIR) if os.path.isdir(os.path.join(TEMPLATE_BASE_DIR, d))]
    if templates:
        click.echo(click.style("\nAvailable templates:", fg='cyan'))
        for t in sorted(templates):
            click.echo(f"  - {t}")
    else:
        click.echo(click.style("\nNo templates found in the template directory.", fg='yellow'))
    return templates


# --- Main CLI Group with Welcome Message ---

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
    click.echo(click.style("  • git template create   [OPTIONS]", fg='green'))
    click.echo("    - Create a new item (e.g., component, service) from a specified template.")
    click.echo("    - Example: git template create react-component MyButton --path src/components")
    click.echo("    - Options: --path, --no-git-add, --no-git-branch")
    click.echo(click.style("  • git template list", fg='green'))
    click.echo("    - Lists all available templates.")
    click.echo("    - Example: git template list")
    click.echo(click.style("\nTo get help for a specific command:", fg='magenta'))
    click.echo("  git template  --help")
    click.echo("  Example: git template create --help")
    click.echo(click.style("\nPress Enter to continue or Ctrl+C to exit...", fg='yellow'))
    click.pause(info="")  # Waits for user to press Enter



@click.group(invoke_without_command=True) # <--- IMPORTANT CHANGE 1
@click.pass_context                 # <--- IMPORTANT CHANGE 2
def cli(ctx):
    """
    A Git CLI tool to create new repositories or branches from predefined templates.
    """
    if ctx.invoked_subcommand is None: # <--- IMPORTANT CHANGE 3
        display_welcome_page()

# --- create command remains the same ---

@cli.command()
@click.argument('template_name', type=str)
@click.argument('new_item_name', type=str)
@click.option('--path', '-p', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              default='.', help="The destination path to create the new item. Defaults to current directory.")
@click.option('--no-git-add', is_flag=True, help="Do not automatically `git add` the new files.")
@click.option('--no-git-branch', is_flag=True, help="Do not automatically create a new Git branch.")
def create(template_name, new_item_name, path, no_git_add, no_git_branch):
    """
    Creates a new item (e.g., component, service) from a specified template.

    Example: git template create react-component MyButton --path src/components
    """
    template_path = os.path.join(TEMPLATE_BASE_DIR, template_name)
    destination_path = os.path.join(path, new_item_name)

    if not os.path.isdir(template_path):
        click.echo(click.style(f"Error: Template '{template_name}' not found at '{template_path}'.", fg='red'), err=True)
        list_templates()
        sys.exit(1)

    if os.path.exists(destination_path):
        click.echo(click.style(f"Error: Destination '{destination_path}' already exists.", fg='red'), err=True)
        sys.exit(1)

    click.echo(f"Creating '{new_item_name}' from template '{template_name}' in '{destination_path}'...")

    try:
        shutil.copytree(template_path, destination_path)
    except Exception as e:
        click.echo(click.style(f"Error copying template files: {e}", fg='red'), err=True)
        sys.exit(1)

    # Placeholder replacement logic
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

    # Git integration
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

# --- list command remains the same ---

@cli.command()
def list():
    """Lists all available templates."""
    list_templates()

if __name__ == '__main__':
    cli()
