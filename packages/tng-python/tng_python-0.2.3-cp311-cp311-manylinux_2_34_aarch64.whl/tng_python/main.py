#!/usr/bin/env python3
"""
TNG Python - Main CLI Entry Point using Typer
Much cleaner than manual argument preprocessing!
"""

from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console

from .version import __version__
from .cli import init_config
from .interactive import TngInteractive
from .service import GenerateTestService
from .ui.theme import TngTheme

# Create Typer app
app = typer.Typer(
    name="tng",
    help="TNG Python - LLM-Powered Test Generation for Python Applications",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()


def find_python_file(file_arg: str) -> Path:
    """Find Python file based on argument"""
    current_dir = Path.cwd()

    # If it's already a full path, use it
    if file_arg.endswith('.py'):
        file_path = Path(file_arg)
        if file_path.exists():
            return file_path
        # Try relative to current directory
        file_path = current_dir / file_arg
        if file_path.exists():
            return file_path

    # Try with .py extension
    filename = file_arg if file_arg.endswith('.py') else f"{file_arg}.py"

    # Search in current directory first
    file_path = current_dir / filename
    if file_path.exists():
        return file_path

    # Search recursively in project
    for file_path in current_dir.rglob(filename):
        # Skip common exclude directories
        if any(excluded in file_path.parts for excluded in [
            'venv', 'env', '.venv', '.env', 'site-packages',
            '__pycache__', '.git', 'node_modules', 'target', 'build', 'dist',
            'tests', 'test', 'spec'
        ]):
            continue
        return file_path

    raise FileNotFoundError(f"Could not find Python file: {file_arg}")


@app.command()
def generate(
        file: str = typer.Option(
            None,
            "-f", "--file",
            help="File name or path to generate tests for"
        ),
        method: Optional[str] = typer.Option(
            None,
            "-m", "--method",
            help="Specific method name to generate tests for"
        ),
):
    """Generate tests for Python files and methods"""

    if not file:
        print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Error: --file is required[/{TngTheme.Colors.ERROR}]")
        print("Use 'tng --help' for usage information")
        raise typer.Exit(1)

    try:
        # Find the file
        file_path = find_python_file(file)
        print(f"{TngTheme.Icons.SEARCH} Found file: {file_path}")

        # Get methods from file
        try:
            import tng_utils
            from .config import get_enabled_config

            # Check if we should use dynamic FastAPI loading
            config = get_enabled_config()
            framework = config.get('framework')
            fastapi_app_path = config.get('fastapi_app_path')

            if framework == 'fastapi' and fastapi_app_path:
                # Use dynamic FastAPI analysis
                analysis = tng_utils.analyze_python_file_with_fastapi_config(str(file_path), config)
                print(f"{TngTheme.Icons.ROCKET} Loaded FastAPI app from: {fastapi_app_path}")
            else:
                # Use regular static analysis
                analysis = tng_utils.analyze_python_file(str(file_path))

            methods = []

            # Extract methods based on analysis
            if 'classes' in analysis and isinstance(analysis['classes'], dict):
                for class_name, class_info in analysis['classes'].items():
                    if isinstance(class_info, dict):
                        # Check various class types
                        is_django_form = False
                        is_callable_class = False
                        has_custom_methods = False

                        # Check base classes for Django forms
                        if 'base_classes' in class_info:
                            base_classes = class_info['base_classes']
                            if isinstance(base_classes, list):
                                for base in base_classes:
                                    if isinstance(base, str):
                                        if 'ModelForm' in base or 'Form' in base:
                                            is_django_form = True
                                        # Could add more framework detection here

                        # Check if class has __call__ method (callable class)
                        if 'methods' in class_info and '__call__' in class_info['methods']:
                            is_callable_class = True

                        # Add methods within classes (ALL methods from Rust analyzer)
                        if 'methods' in class_info:
                            for method_name, method_info in class_info['methods'].items():
                                has_custom_methods = True
                                method_type = 'method'
                                if method_info.get('decorators') and 'staticmethod' in method_info['decorators']:
                                    method_type = 'static_method'
                                elif method_info.get('decorators') and 'classmethod' in method_info['decorators']:
                                    method_type = 'class_method'

                                methods.append({
                                    'name': method_name,
                                    'class': class_name,
                                    'display': f"{class_name}.{method_name}",
                                    'type': method_type,
                                    'info': method_info
                                })

                        # Add special class types as testable units
                        if is_django_form and not has_custom_methods:
                            methods.append({
                                'name': class_name,
                                'class': None,
                                'display': class_name,
                                'type': 'django_form',
                                'info': class_info
                            })
                        elif is_callable_class and not has_custom_methods:
                            methods.append({
                                'name': class_name,
                                'class': None,
                                'display': class_name,
                                'type': 'callable_class',
                                'info': class_info
                            })

            if 'functions' in analysis and isinstance(analysis['functions'], dict):
                for func_name, func_info in analysis['functions'].items():
                    # Include ALL functions from Rust analyzer
                    # Determine function type
                    func_type = 'function'
                    if func_info.get('is_async'):
                        func_type = 'async_function'
                    elif func_info.get('has_yield'):
                        func_type = 'generator_function'

                    methods.append({
                        'name': func_name,
                        'class': None,
                        'display': func_name,
                        'type': func_type,
                        'info': func_info
                    })

            if not methods:
                print(
                    f"[{TngTheme.Colors.WARNING}]{TngTheme.Icons.ERROR} No methods found in {file_path.name}[/{TngTheme.Colors.WARNING}]")
                raise typer.Exit(1)

            # Filter by method name if specified
            if method:
                matching_methods = [
                    m for m in methods
                    if m['name'].lower() == method.lower() or
                       m['display'].lower() == method.lower()
                ]
                if not matching_methods:
                    print(
                        f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Method '{method}' not found in {file_path.name}[/{TngTheme.Colors.ERROR}]")
                    print(f"Available methods: {', '.join([m['display'] for m in methods])}")
                    raise typer.Exit(1)
                methods = matching_methods

            # Generate tests
            test_service = GenerateTestService()

            print(f"{TngTheme.Icons.ROCKET} Generating tests for {len(methods)} method(s)...")

            for method_item in methods:
                print(f"  {TngTheme.Icons.WRITE} Processing: {method_item['display']}")
                result = test_service.generate_test_for_method(method_item['name'], str(file_path), analysis_data=analysis)

                if result.get('success'):
                    print(
                        f"  [{TngTheme.Colors.SUCCESS}]{TngTheme.Icons.SUCCESS} Generated test for {method_item['display']}[/{TngTheme.Colors.SUCCESS}]")
                else:
                    print(
                        f"  [{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Failed to generate test for {method_item['display']}: {result.get('error', 'Unknown error')}[/{TngTheme.Colors.ERROR}]")

            print(
                f"[{TngTheme.Colors.SUCCESS}]{TngTheme.Icons.COMPLETE} Test generation completed![/{TngTheme.Colors.SUCCESS}]")

        except Exception as e:
            print(
                f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Error analyzing file: {str(e)}[/{TngTheme.Colors.ERROR}]")
            raise typer.Exit(1)

    except FileNotFoundError as e:
        print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} {str(e)}[/{TngTheme.Colors.ERROR}]")
        raise typer.Exit(1)
    except Exception as e:
        print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Error: {str(e)}[/{TngTheme.Colors.ERROR}]")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Launch interactive mode"""
    try:
        app = TngInteractive()
        app.show_main_menu()
    except KeyboardInterrupt:
        try:
            app = TngInteractive()
            app.exit_ui.show()
        except:
            print(f"\n[{TngTheme.Colors.WARNING}]{TngTheme.Icons.GOODBYE}[/{TngTheme.Colors.WARNING}]")
        raise typer.Exit(0)
    except Exception as e:
        print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Error: {str(e)}[/{TngTheme.Colors.ERROR}]")
        raise typer.Exit(1)


@app.command()
def init():
    """Generate TNG configuration file"""
    init_config()



@app.callback(invoke_without_command=True)
def main(
        ctx: typer.Context,
        file: Optional[str] = typer.Option(
            None,
            "-f", "--file",
            help="File name or path to generate tests for"
        ),
        method: Optional[str] = typer.Option(
            None,
            "-m", "--method",
            help="Specific method name to generate tests for"
        ),
        version: bool = typer.Option(
            False,
            "--version", "-v",
            help="Show version and exit"
        )
):
    """
    TNG Python - LLM-Powered Test Generation for Python Applications
    
    Examples:
    
        [bold]tng[/bold]                          # Interactive mode
        [bold]tng -f users.py[/bold]              # Generate tests for all methods in file  
        [bold]tng -f users.py -m save[/bold]      # Generate test for specific method
        [bold]tng init[/bold]                     # Generate configuration file
    
    You can also use short syntax:
    
        [bold]tng f=users.py m=save[/bold]        # Same as above but shorter!
    """

    if version:
        print(f"TNG Python version: {__version__}")
        raise typer.Exit()

    # If a subcommand was invoked, don't run the main logic
    if ctx.invoked_subcommand is not None:
        return

    # If file argument provided, run generate command
    if file:
        ctx.invoke(generate, file=file, method=method)
        return

    # Otherwise run interactive mode
    ctx.invoke(interactive)


if __name__ == "__main__":
    app()
