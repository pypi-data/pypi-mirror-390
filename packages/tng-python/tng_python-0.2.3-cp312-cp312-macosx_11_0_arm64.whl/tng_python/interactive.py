"""Main interactive interface for TNG Python"""

import sys
from enum import Enum

from rich import print

from .ui import GenerateTestsUI, GoUISession


class MenuAction(Enum):
    GENERATE_TESTS = "generate_tests"
    STATS = "stats"
    OPTIONS = "options"
    ABOUT = "about"
    HELP = "help"
    EXIT = "exit"


class TngInteractive:
    def __init__(self):
        self.generate_tests_ui = GenerateTestsUI()
        self.go_ui_session = GoUISession()
        self.go_ui_session.start()

    def check_configuration(self):
        """Check if configuration is valid"""
        from .config import get_api_key, get_base_url

        missing = []

        try:
            api_key = get_api_key()
            if not api_key:
                missing.append("API_KEY")

            base_url = get_base_url()
            if not base_url:
                missing.append("BASE_URL")
        except FileNotFoundError:
            missing.append("Configuration file (tng_config.py)")
        except Exception as e:
            missing.append(f"Configuration: {str(e)}")

        if missing:
            self.go_ui_session.show_config_error(missing)
            return False

        return True

    def check_system_status(self):
        """Check system health and API connectivity"""
        from .config import get_base_url
        from .http_client import get_http_client
        from .version import __version__

        try:
            client = get_http_client()
            ping_response = client.ping()

            if not ping_response:
                status = {
                    "status": "error",
                    "message": "Unable to connect to TNG service",
                    "error_type": "connection_error"
                }
                self.go_ui_session.show_system_status(status)
                sys.exit(1)

            current_version = ping_response.get('current_version', {})
            api_version = current_version.get('pip_version')
            server_base_url = ping_response.get('base_url')
            user_base_url = get_base_url()

            if api_version and api_version > __version__:
                status = {
                    "status": "version_mismatch",
                    "message": "Version mismatch detected",
                    "current_version": api_version,
                    "local_version": __version__,
                    "error_type": "version_mismatch",
                    "fixes": [
                        {"title": f"pip install tng-python=={api_version}",
                         "description": "Update to the latest version"},
                        {"title": "pip install --upgrade tng-python", "description": "Upgrade to the newest version"}
                    ]
                }
                self.go_ui_session.show_system_status(status)
                sys.exit(1)

            if server_base_url and user_base_url and server_base_url.rstrip('/') != user_base_url.rstrip('/'):
                status = {
                    "status": "base_url_mismatch",
                    "message": "Base URL mismatch detected",
                    "server_base_url": server_base_url,
                    "user_base_url": user_base_url,
                    "current_version": api_version,
                    "local_version": __version__,
                    "error_type": "base_url_mismatch",
                    "fixes": [
                        {"title": "Edit tng_config.py", "description": "Open your TNG configuration file"},
                        {"title": f"Set BASE_URL = '{server_base_url}'",
                         "description": "Update to the correct server URL"}
                    ]
                }
                self.go_ui_session.show_system_status(status)
                sys.exit(1)


        except Exception as e:
            status = {
                "status": "error",
                "message": "System check failed",
                "details": str(e),
                "error_type": "unknown_error"
            }
            self.go_ui_session.show_system_status(status)
            sys.exit(1)

    def show_main_menu(self):
        """Display main interactive menu with arrow key navigation"""
        if not self.check_configuration():
            sys.exit(1)

        self.check_system_status()

        while True:
            choice = self.go_ui_session.show_menu()

            if choice == "tests" or choice == "generate_tests":
                self.generate_tests_ui.show()
            elif choice == "stats":
                try:
                    from .http_client import get_http_client
                    client = get_http_client()
                    stats_data = client.get_user_stats()
                    if stats_data:
                        self.go_ui_session.show_stats(stats_data)
                    else:
                        print("⚠️  Unable to fetch stats from API")
                except Exception as e:
                    print(f"❌ Error fetching stats: {e}")
            elif choice == "about":
                self.go_ui_session.show_about()
            elif choice == "exit" or choice is None:
                sys.exit(0)


def main():
    """Main entry point for interactive mode"""
    try:
        app = TngInteractive()
        app.show_main_menu()
    except KeyboardInterrupt:
        try:
            app = TngInteractive()
            app.exit_ui.show()
        except:
            print("\n[yellow]Goodbye! 👋[/yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
