"""Go UI Session - Python wrapper for unified Go UI binary"""

import json
import os
import platform
import subprocess
import tempfile
import time
from pathlib import Path


class GoUISession:
    """Wrapper for calling go-ui binary from Python"""

    def __init__(self):
        self._binary_path = self._find_go_ui_binary()
        self._running = False

    def start(self):
        """Mark session as running"""
        self._running = True

    def stop(self):
        """Mark session as stopped"""
        self._running = False

    def running(self):
        """Check if session is running"""
        return self._running

    def show_menu(self):
        """Show main menu and return selected choice"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_file = f.name

        try:
            # Run Go UI with full terminal access
            result = subprocess.run(
                [self._binary_path, "menu", "--output", output_file],
                check=False
            )

            # Check if output file has content
            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                return "exit"  # User cancelled or interrupted

            with open(output_file, 'r') as f:
                choice = f.read().strip()
                return choice if choice else "exit"
        except Exception as e:
            return "exit"
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def show_list_view(self, title, items):
        """
        Show searchable list view for any component (files, controllers, models, services, etc)
        
        Args:
            title: List title (e.g., "Select File")
            items: List of dicts with 'name' and 'path' keys
        
        Returns:
            Selected item name or "back"
        """
        # Convert to JSON string
        data_json = json.dumps({"title": title, "items": items})

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            output_file = f.name

        try:
            subprocess.run(
                [self._binary_path, "list-view", "--data", data_json, "--output", output_file],
                check=False
            )

            # Read plain text output (not JSON)
            with open(output_file, 'r') as f:
                selected = f.read().strip()
                return selected if selected else "back"
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def show_spinner(self, message, func):
        """
        Show spinner while executing func, then complete with its message.

        Args:
            message: Spinner message
            func: Callable returning a dict: { success: bool, message: str, ... }

        Returns:
            The dict returned by func
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            control_file = f.name

        process = subprocess.Popen(
            [self._binary_path, "spinner", "--message", message, "--control", control_file],
            stdin=None,
            stdout=None,
            stderr=None
        )

        try:
            result = func()

            # Write completion status
            status = {
                "status": "success" if result and result.get("success") else "error",
                "message": (result or {}).get("message", "Done!")
            }
            with open(control_file, 'w') as f:
                json.dump(status, f)

            process.wait()
            return result
        except Exception as e:
            # Write error status
            status = {"status": "error", "message": str(e)}
            try:
                with open(control_file, 'w') as f:
                    json.dump(status, f)
                process.wait()
            finally:
                pass
            raise
        finally:
            if os.path.exists(control_file):
                os.unlink(control_file)

    def execute_with_spinner(self, message, func):
        """
        Execute a function with spinner display
        
        Args:
            message: Spinner message
            func: Callable that returns dict with 'success', 'message', and other data
        
        Returns:
            Result from func
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            control_file = f.name

        # Start spinner in background
        process = subprocess.Popen(
            [self._binary_path, "spinner", "--message", message, "--control", control_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        try:
            # Execute the function
            result = func()

            # Write completion status
            status = {
                "status": "success" if result.get("success") else "error",
                "message": result.get("message", "Done")
            }
            with open(control_file, 'w') as f:
                json.dump(status, f)

            # Wait for spinner to finish
            process.wait()

            return result
        except Exception as e:
            # Write error status
            status = {"status": "error", "message": str(e)}
            with open(control_file, 'w') as f:
                json.dump(status, f)
            process.wait()
            raise
        finally:
            if os.path.exists(control_file):
                os.unlink(control_file)

    def show_progress(self, title, func):
        """
        Show progress bar with steps
        
        Args:
            title: Progress title
            func: Callable that receives ProgressUpdater and returns dict with 'message' and 'result'
        
        Returns:
            Result dict from func
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            control_file = f.name

        # Start progress in background (inherit TTY so Bubble Tea can render)
        process = subprocess.Popen(
            [self._binary_path, "progress", "--title", title, "--control", control_file],
            stdin=None,
            stdout=None,
            stderr=None
        )

        try:
            # Create progress updater
            updater = ProgressUpdater(control_file)

            # Execute the function with updater
            result = func(updater)

            # Write completion status
            if result.get("result") and result["result"].get("error"):
                # Error case
                pass  # Error already written by updater.error()
            else:
                # Success case
                completion = {
                    "type": "complete",
                    "message": result.get("message", "Done!")
                }
                with open(control_file, 'w') as f:
                    json.dump(completion, f)

            # Wait for progress to finish
            process.wait()

            return result
        except Exception as e:
            # Write error status
            error = {
                "type": "error",
                "message": f"Error: {str(e)}"
            }
            with open(control_file, 'w') as f:
                json.dump(error, f)
            process.wait()
            raise
        finally:
            if os.path.exists(control_file):
                os.unlink(control_file)

    def show_no_items(self, item_type):
        """
        Show 'no items found' message
        
        Args:
            item_type: Type of items (e.g., "controllers", "models graphql, services, etc")
        """
        subprocess.run(
            [self._binary_path, "no-items", "--type", item_type],
            check=True
        )

    def show_stats(self, stats_data):
        """
        Show user statistics
        
        Args:
            stats_data: Dict with statistics data
        """
        # Convert stats data to JSON string
        stats_json = json.dumps(stats_data) if stats_data else "{}"

        try:
            subprocess.run(
                [self._binary_path, "stats", "--data", stats_json],
                check=False
            )
        except Exception as e:
            print(f"Stats error: {e}")

    def show_about(self):
        """Show about screen"""
        try:
            subprocess.run([self._binary_path, "about"], check=False)
        except Exception as e:
            print(f"About error: {e}")

    def show_system_status(self, status):
        """
        Show system status
        
        Args:
            status: Dict with status information
        """
        # Convert to JSON string
        data_json = json.dumps(status) if status else "{}"

        try:
            subprocess.run(
                [self._binary_path, "system-status", "--data", data_json],
                check=False
            )
        except Exception as e:
            print(f"System status error: {e}")

    def show_config_error(self, missing):
        """
        Show configuration error
        
        Args:
            missing: List of missing configuration items
        """
        # Convert to JSON string
        data_json = json.dumps({"missing": missing})

        try:
            subprocess.run(
                [self._binary_path, "config-error", "--data", data_json],
                check=False
            )
        except Exception as e:
            print(f"Config error: {e}")

    def show_post_generation_menu(self, file_path, run_command):
        """
        Show post-generation menu
        
        Args:
            file_path: Generated test file path
            run_command: Command to run tests
        
        Returns:
            Selected choice ("run_tests", "copy_command", "back")
        """
        # Convert to JSON string
        data_json = json.dumps({"file_path": file_path, "run_command": run_command})

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            output_file = f.name

        try:
            subprocess.run(
                [self._binary_path, "post-generation-menu", "--data", data_json, "--output", output_file],
                check=False
            )

            # Read plain text output (not JSON)
            with open(output_file, 'r') as f:
                choice = f.read().strip()
                return choice if choice else "back"
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def show_clipboard_success(self, command):
        """
        Show clipboard success message
        
        Args:
            command: Command that was copied
        """
        subprocess.run(
            [self._binary_path, "clipboard-success", "--command", command],
            check=True
        )

    def show_test_results(self, title, passed, failed, errors, total, results=None):
        """
        Show test results
        
        Args:
            title: Results title
            passed: Number of passed tests
            failed: Number of failed tests
            errors: Number of errors
            total: Total number of tests
            results: List of individual test results (optional)
        """
        if results is None:
            results = []

        data = {
            "title": title,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total": total,
            "results": results
        }

        # Convert to JSON string
        data_json = json.dumps(data)

        try:
            subprocess.run(
                [self._binary_path, "test-results", "--data", data_json],
                check=False
            )
        except Exception as e:
            print(f"Test results error: {e}")

    def _find_go_ui_binary(self):
        """Find the correct go-ui binary for current platform"""
        # Detect platform
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Map platform to binary name
        if system == "darwin":
            if machine in ["arm64", "aarch64"]:
                binary_name = "go-ui-darwin-arm64"
            else:
                binary_name = "go-ui-darwin-amd64"
        elif system == "linux":
            if machine in ["arm64", "aarch64"]:
                binary_name = "go-ui-linux-arm64"
            else:
                binary_name = "go-ui-linux-amd64"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

        # Try package bundled binary first (from tng_python/ui/ -> ../../binaries/)
        package_dir = Path(__file__).parent.parent
        package_binary = package_dir / "binaries" / binary_name
        if package_binary.exists():
            return str(package_binary)

        # Try site-packages binaries (when installed via pip/poetry/uv)
        try:
            import site
            # Check virtualenv/global site-packages
            site_packages_dirs = site.getsitepackages()
            for site_dir in site_packages_dirs:
                site_binary = Path(site_dir) / "binaries" / binary_name
                if site_binary.exists():
                    return str(site_binary)

            # Check user site-packages (pip install --user)
            if site.ENABLE_USER_SITE:
                user_site = site.getusersitepackages()
                user_binary = Path(user_site) / "binaries" / binary_name
                if user_binary.exists():
                    return str(user_binary)
        except:
            pass

        # Development fallback - sibling go-ui project
        dev_binary = package_dir.parent.parent / "go-ui" / "binaries" / binary_name
        if dev_binary.exists():
            return str(dev_binary)

        raise RuntimeError(
            f"go-ui binary not found for {system} ({machine}). "
            f"Expected: {package_binary}, site-packages/binaries/{binary_name}, "
            f"user-site-packages/binaries/{binary_name}, or {dev_binary}. "
            f"Please ensure tng-python is installed with binaries included."
        )


class ProgressUpdater:
    """Helper class for updating progress bar from within a function"""

    def __init__(self, control_file):
        self.control_file = control_file
        self.step = 0

    def update(self, message, percent=None):
        """
        Update progress with a new step
        
        Args:
            message: Progress message
            percent: Optional percentage (0-100)
        """
        data = {
            "type": "step",
            "step": self.step,
            "message": message
        }
        if percent is not None:
            data["percent"] = percent

        with open(self.control_file, 'w') as f:
            json.dump(data, f)
        
        self.step += 1
        time.sleep(0.1)  # Give UI time to update

    def error(self, message):
        """
        Report an error
        
        Args:
            message: Error message
        """
        data = {
            "type": "error",
            "message": message
        }
        with open(self.control_file, 'w') as f:
            json.dump(data, f)
        time.sleep(0.1)  # Give UI time to update
