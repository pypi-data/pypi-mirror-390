from pathlib import Path
from subprocess import TimeoutExpired

from .go_ui_session import GoUISession
from ..service import GenerateTestService


class GenerateTestsUI:
    def __init__(self):
        self.test_service = GenerateTestService()
        self.go_ui_session = GoUISession()
        self.go_ui_session.start()
        self._fastapi_analysis_data = None
    
    def show(self):
        """Main test generation flow"""
        while True:
            result = self._show_file_selection()
            if result == "back":
                return "back"
            elif result == "exit":
                return "exit"

    def _show_file_selection(self):
        """Show file selection interface"""
        python_files = self._get_user_python_files()
        
        if not python_files:
            self.go_ui_session.show_no_items("Python files")
            return "back"
        
        items = [
            {"name": file.name, "path": str(file.parent)}
            for file in python_files
        ]

        selected_name = self.go_ui_session.show_list_view("Select Python File", items)

        if selected_name == "back":
                return "back"
            
        selected_file = None
        for file in python_files:
            if file.name == selected_name:
                    selected_file = str(file)
                    break

        if not selected_file:
                return "back"
        
        return self._show_methods_for_file(selected_file)

    def _show_methods_for_file(self, file_path):
        """Show methods for a specific file"""
        methods = self._get_file_methods(file_path)

        if not methods:
            self.go_ui_session.show_no_items("methods")
            return self._show_file_selection()

        file_name = Path(file_path).name
        items = [{"name": method['display'], "path": f"Method in {file_name}"} for method in methods]

        selected_display = self.go_ui_session.show_list_view(f"Select Method for {file_name}", items)

        if selected_display == "back":
                return self._show_file_selection()

        if selected_display:
            # Find the method object that matches the selected display name
            selected_method = None
            for method in methods:
                if method['display'] == selected_display:
                    selected_method = method
                    break

            if selected_method:
                result = self._generate_tests_for_method(file_path, selected_method)
                if result and result.get('file_path') and not result.get('error'):
                    self._show_post_generation_menu(result)
            return self._show_file_selection()
        else:
            return self._show_file_selection()

    def _generate_tests_for_method(self, file_path, selected_method):
        """Generate tests for selected method using Go UI progress"""
        file_name = Path(file_path).name

        # Create display name: class_name#method_name or filename#method_name
        if selected_method.get('class'):
            display_name = f"{selected_method['class']}#{selected_method['name']}"
        else:
            display_name = f"{file_name}#{selected_method['name']}"

        def progress_handler(progress):
            progress.update("Submitting request to API...")

            # Progress callback that receives status messages and percentage from service
            def handle_progress(message, percent=None):
                if isinstance(message, str):
                    progress.update(message, percent)

            print(f"[DEBUG] Calling generate_test_for_method with analysis_data: {bool(self._fastapi_analysis_data)}")
            gen_result = self.test_service.generate_test_for_method(
                selected_method['name'],
                file_path,
                progress_callback=handle_progress,
                analysis_data=self._fastapi_analysis_data
            )

            if gen_result and gen_result.get('error'):
                progress.error("Test generation failed. Please try again.")
                return {"result": gen_result}
            elif gen_result and gen_result.get('success'):
                progress.update("Saving test file...")
                file_info = self.test_service.save_test_file(gen_result.get('result', ''))

                if file_info:
                    test_count = self._count_test_methods(file_info.get('absolute_path', ''))
                    count_msg = "1 test" if test_count == 1 else f"{test_count} tests"

                    elapsed = gen_result.get('elapsed', 0)
                    time_msg = f" in {elapsed:.1f}s" if elapsed > 0 else ""

                    return {
                        "message": f"Generated {count_msg}{time_msg}!",
                        "result": file_info
                    }
                else:
                    progress.error("Failed to save test file")
                    return {"result": {"error": "Failed to save test file"}}
            else:
                progress.error("Test generation failed. Please try again.")
                return {"result": {"error": "Unknown error"}}

        result = self.go_ui_session.show_progress(
            f"Generating test for {display_name}",
            progress_handler
        )

        if result and result.get('result') and not result['result'].get('error'):
            return result['result']
        return None

    def _show_post_generation_menu(self, file_info):
        """Show post-generation menu (like Ruby implementation)"""
        file_path = file_info.get('file_path') or file_info.get('absolute_path')
        run_command = file_info.get('run_command', f'pytest {file_path}')

        while True:
            choice = self.go_ui_session.show_post_generation_menu(file_path, run_command)

            if choice == "run_tests":
                self._run_and_show_test_results(run_command)
            elif choice == "copy_command":
                self._copy_command_and_show_success(run_command)
            elif choice == "back":
                break
            else:
                break

    def _copy_command_and_show_success(self, command):
        """Copy command to clipboard and show success"""
        import subprocess
        import sys

        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['pbcopy'], input=command.encode('utf-8'), check=True)
                self.go_ui_session.show_clipboard_success(command)
            elif sys.platform.startswith('linux'):  # Linux
                try:
                    subprocess.run(['xclip', '-selection', 'clipboard'],
                                   input=command.encode('utf-8'), check=True)
                    self.go_ui_session.show_clipboard_success(command)
                except FileNotFoundError:
                    print(f"\n📋 Copy this command:\n{command}\n")
                    input("Press Enter to continue...")
            else:  # Windows or other
                print(f"\n📋 Copy this command:\n{command}\n")
                input("Press Enter to continue...")
        except Exception as e:
            print(f"\n📋 Copy this command:\n{command}\n")
            input("Press Enter to continue...")

    def _run_and_show_test_results(self, command):
        """Run tests and show results using Go UI"""
        import subprocess

        # Run tests with spinner
        def spinner_handler():
            output = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            return {
                "success": True,
                "message": "Tests completed",
                "output": output.stdout + output.stderr,
                "exit_code": output.returncode
            }

        test_output = self.go_ui_session.show_spinner("Running tests...", spinner_handler)

        passed, failed, errors, total = self._parse_test_output(
            test_output.get('output', ''),
            test_output.get('exit_code', 1)
        )

        self.go_ui_session.show_test_results(
            "Test Results",
            passed,
            failed,
            errors,
            total,
            []  # No detailed results for now
        )

    def _parse_test_output(self, output, exit_code):
        """Parse pytest output to extract test counts"""
        import re

        passed = failed = errors = 0

        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        error_match = re.search(r'(\d+) error', output)

        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
        if error_match:
            errors = int(error_match.group(1))

        total = passed + failed + errors

        if total == 0:
            if exit_code == 0:
                passed = 1
                total = 1
            else:
                failed = 1
                total = 1

        return passed, failed, errors, total

    def _get_user_python_files(self):
        """Get Python files that belong to the user's project (not dependencies)"""
        current_dir = Path.cwd()
        python_files = []
        
        exclude_dirs = {
            'venv', 'env', '.venv', '.env',
            'site-packages', 'dist-packages',
            '__pycache__', '.git', '.pytest_cache',
            'node_modules', 'target', 'build', 'dist',
            '.mypy_cache', '.tox', 'htmlcov',
            'tests', 'test', 'spec'
        }
        
        for py_file in current_dir.rglob("*.py"):
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue
            
            if py_file.stat().st_size < 10:
                continue
            
            python_files.append(py_file)
        
        # Sort by name for consistent ordering
        return sorted(python_files, key=lambda x: x.name)

    def _get_file_methods(self, file_path):
        """Get method info from Python file using enhanced logic."""
        try:
            import tng_utils
            from ..config import get_enabled_config

            # Check if we should use FastAPI analysis
            config = get_enabled_config()
            print(f"[DEBUG] Config loaded: {config}")
            print(f"[DEBUG] Current working directory: {__import__('os').getcwd()}")
            framework = config.get('framework') if config else None
            fastapi_app_path = config.get('fastapi_app_path') if config else None
            print(f"[DEBUG] Framework: {framework}, FastAPI path: {fastapi_app_path}")

            if framework == 'fastapi' and fastapi_app_path:
                # Use dynamic FastAPI analysis
                print(f"[DEBUG] Using FastAPI analysis for {file_path}")
                analysis = tng_utils.analyze_python_file_with_fastapi_config(file_path, config)
                self._fastapi_analysis_data = analysis.get('fastapi_dynamic')
                print(f"[DEBUG] FastAPI analysis data: {bool(self._fastapi_analysis_data)}")
            else:
                # Use regular static analysis
                print(f"[DEBUG] Using regular analysis for {file_path}")
                analysis = tng_utils.analyze_python_file(file_path)
                self._fastapi_analysis_data = None

            methods = []

            # Extract methods based on analysis (same logic as main.py)
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
                                    if isinstance(base, str) and ('ModelForm' in base or 'Form' in base):
                                        is_django_form = True

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

            return methods

        except Exception:
            return []

    def _count_test_methods(self, test_file_path):
        """Count the number of actual test cases using pytest collection (matches pytest output)"""
        try:
            import subprocess
            from pathlib import Path

            import tng_utils

            file_path = Path(test_file_path).resolve()

            if not file_path.exists():
                return 0

            pytest_cmd = None
            for cmd_path in ["pytest", "./venv/bin/pytest"]:
                try:
                    subprocess.run([cmd_path, "--version"], capture_output=True, timeout=5)
                    pytest_cmd = [cmd_path]
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not pytest_cmd:
                try:
                    subprocess.run(["python", "-m", "pytest", "--version"], capture_output=True, timeout=5)
                    pytest_cmd = ["python", "-m", "pytest"]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass

            if not pytest_cmd:
                count = tng_utils.count_test_methods(str(file_path))
                return count

            result = subprocess.run(
                pytest_cmd + ["--collect-only", "-q", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')

                for line in lines:
                    line = line.strip()
                    if '.py:' in line and line.split(':')[-1].strip().isdigit():
                        parts = line.split(':')
                        if len(parts) >= 2:
                            count_str = parts[-1].strip()
                            try:
                                return int(count_str)
                            except ValueError:
                                continue

                test_count = 0
                for line in lines:
                    line = line.strip()
                    if '::' in line and ('test_' in line or 'Test' in line):
                        # Skip summary lines
                        if not any(skip in line.lower() for skip in
                                   ['collected', 'test session', 'platform', 'rootdir', 'plugins']):
                            test_count += 1

                if test_count == 0:
                    for line in lines:
                        if 'collected' in line.lower():
                            import re
                            match = re.search(r'collected (\d+) items?', line.lower())
                            if match:
                                test_count = int(match.group(1))
                                break

                return test_count if test_count > 0 else 1  # At least 1 if file exists
            else:
                count = tng_utils.count_test_methods(str(file_path))
                return count

        except TimeoutExpired:
            return self._fallback_count_test_methods(test_file_path)
        except Exception:
            return self._fallback_count_test_methods(test_file_path)

    def _fallback_count_test_methods(self, test_file_path):
        """Fallback method to count test methods using Python AST"""
        try:
            import ast
            from pathlib import Path

            file_path = Path(test_file_path).resolve()
            if not file_path.exists():
                return 0

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            count = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    count += 1

            return count
        except Exception:
            return 0
