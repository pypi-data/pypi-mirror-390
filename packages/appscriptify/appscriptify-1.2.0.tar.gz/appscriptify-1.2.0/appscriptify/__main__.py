import os
import shutil
import argparse
import pkg_resources
import textwrap

# Optional colored output: use colorama when available (works well on Windows).
try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    CYAN = Fore.CYAN
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL
except Exception:
    # Fallback to no-op strings if colorama isn't installed
    GREEN = YELLOW = RED = CYAN = BOLD = RESET = ""

def main():
    # Try to read the package version for the --version flag
    try:
        _version = pkg_resources.get_distribution('appscriptify').version
    except Exception:
        _version = '0.0.0'

    examples = textwrap.dedent('''
        Examples:

          # Create a project interactively (will prompt for name)
          appscriptify create

          # Create a project with a name and template in a specific path
          appscriptify create --name MyApp --template login --path C:\\projects

          # Show version
          appscriptify --version
    ''')

    parser = argparse.ArgumentParser(
        prog="appscriptify",
        description="AppScriptify CLI — Create ready-to-use app templates 🚀",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples
    )

    # Global version flag
    parser.add_argument('--version', action='version', version=f'appscriptify {_version}')

    subparsers = parser.add_subparsers(dest="command")

    # -------------------------------
    # CREATE COMMAND
    # -------------------------------
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new project from a template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Create a ready-to-run project folder from one of the built-in templates.",
        epilog="If --name is omitted the CLI will prompt for the project name interactively."
    )

    create_parser.add_argument("--name", help="Project name (if omitted you'll be prompted)", metavar='NAME')
    create_parser.add_argument("--template", help="Template to use (default: login)", default="login", metavar='TEMPLATE')
    create_parser.add_argument("--path", help="Destination path (default: current dir)", default=os.getcwd(), metavar='PATH')

    args = parser.parse_args()

    # Handle commands
    if args.command == "create":
        handle_create(args)
    else:
        parser.print_help()

# ---------------------------------------------------
# Core Logic
# ---------------------------------------------------
def handle_create(args):
    print(f"\n{BOLD}{CYAN}📦 Welcome to AppScriptify Project Creator!{RESET}\n")

    # Interactive mode if not passed
    project_name = args.name or input(f"{BOLD}🧱 Enter project name: {RESET}").strip()
    if not project_name:
        print(f"{RED}❌ Project name cannot be empty.{RESET}")
        return

    target_path = args.path or os.getcwd()
    template_name = args.template or "login"

    print(f"\n{BOLD}📂 Location:{RESET} {target_path}")
    print(f"{BOLD}🧩 Template:{RESET} {template_name}")
    print(f"{BOLD}📁 Project Name:{RESET} {project_name}\n")

    # Resolve paths
    try:
        template_dir = pkg_resources.resource_filename('appscriptify', f'templates/{template_name}')
    except Exception:
        template_dir = None

    # Validate template exists inside package resources
    if not template_dir or not os.path.isdir(template_dir):
        try:
            available = pkg_resources.resource_listdir('appscriptify', 'templates')
        except Exception:
            available = []

        if available:
            print(f"{RED}❌ Template '{template_name}' not found.{RESET} Available templates: {', '.join(available)}")
        else:
            print(f"{RED}❌ Template '{template_name}' not found and no templates could be discovered in the package.{RESET}")
        return

    dest_dir = os.path.join(target_path, project_name)

    # Check if folder exists
    if os.path.exists(dest_dir):
        if input(f"{YELLOW}⚠️  Directory '{dest_dir}' already exists. Do you want to overwrite? (y/n){RESET}").lower() in ('y', 'yes'):
            try:
                shutil.rmtree(dest_dir)
                print(f"{YELLOW}🗑️  Existing directory removed.{RESET}")
            except Exception as e:
                print(f"{RED}❌ Could not remove existing directory: {e}{RESET}")
                return
        else:
            print(f"{RED}❌ Operation cancelled by user.{RESET}")
            return

    def copy_with_progress(src, dst):
        """Recursively copy files while printing each file."""
        if os.path.isdir(src):
            if not os.path.exists(dst):
                os.makedirs(dst)
            for item in os.listdir(src):
                copy_with_progress(os.path.join(src, item), os.path.join(dst, item))
        else:
            shutil.copy2(src, dst)
            print(f"{GREEN}Created:{RESET} {os.path.relpath(dst, dest_dir)}", flush=True)

    try:
        print(f"{BOLD}🛠 Creating project structure...{RESET}")
        copy_with_progress(template_dir, dest_dir)
        print(f"{GREEN}✅ Project '{project_name}' created successfully at:{RESET}")
        print(f"   {dest_dir}\n")
        print(f"{BOLD}🚀 Next steps:{RESET}")
        print(f"   cd {dest_dir}")
        print("   python app.py\n")
    except Exception as e:
        print(f"{RED}❌ Error creating project: {e}{RESET}")


if __name__ == "__main__":
    main()
