import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console

from ..config import get_api_key, get_enabled_config, get_base_url

DEBUG = os.getenv('DEBUG') == '1'


class GenerateTestService:
    """
    Service for generating tests using the TNG API
    """

    POLL_INTERVAL_SECONDS = 5  # Poll every 5 seconds
    MAX_POLL_DURATION_SECONDS = 420  # 7 minutes total
    
    def __init__(self):
        base_url = get_base_url()
        self.base_url = base_url
        self.console = Console()
        self.submit_url = f"{base_url}/cli/tng_python/contents/generate_tests/"
        self.status_url_template = f"{base_url}/cli/tng_python/content_responses/{{job_id}}"

    def generate_test_for_method(self, method: str, file_path: str, progress_callback=None, analysis_data=None) -> Dict[str, Any]:
        """
        Generate test for a specific method with Python-based polling

        Args:
            method: Method name to generate tests for
            file_path: Path to the source file
            progress_callback: Optional callback for progress updates
            analysis_data: Optional analysis data (e.g., FastAPI routes)

        Returns:
            Dictionary with success status and result/error
        """
        start_time = time.time()
        
        try:
            import tng_utils  # For send_async_job_request
            
            # Get configuration
            user_config = get_enabled_config()
            if not user_config:
                return {
                    "success": False,
                    "error": "No configuration found. Please run configuration setup first."
                }

            api_key = get_api_key()
            if not api_key:
                return {
                    "success": False,
                    "error": "No API key found. Please configure your API key first."
                }

            dependency_content, dependency_filename = self._get_dependency_content()

            # Process test examples - read file contents for LLM
            if 'test_examples' in user_config and user_config['test_examples']:
                processed_examples = []
                for example in user_config['test_examples'][:5]:  # Limit to 5 examples to avoid huge payloads
                    try:
                        example_path = Path(example['path'])
                        if example_path.exists():
                            with open(example_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                processed_examples.append({
                                    'name': example['name'],
                                    'path': example['path'],
                                    'content': content
                                })
                    except Exception as e:
                        if DEBUG:
                            print(f"[DEBUG] Failed to read test example {example['path']}: {e}")
                        continue

                user_config['test_examples'] = processed_examples
                if DEBUG:
                    print(f"[DEBUG] Included {len(processed_examples)} test examples in payload")

            # Call Rust to submit request
            submit_url = f"{self.base_url}/cli/tng_python/contents/generate_tests/"
            status_url_template = f"{self.base_url}/cli/tng_python/content_responses/{{job_id}}"
            headers = {"Authorization": f"Bearer {api_key}"}

            if DEBUG:
                print(f"\n[DEBUG] Submitting test generation job")
                print(f"[DEBUG] File: {file_path}")
                print(f"[DEBUG] Method: {method}")
                print(f"[DEBUG] Submit URL: {submit_url}")

            rust_result = tng_utils.send_async_job_request(
                submit_url,
                status_url_template,
                headers,
                file_path,
                method,
                user_config,
                dependency_content,
                dependency_filename,
                analysis_data,  # Pass analysis data (may include FastAPI routes)
                None  # progress_callback
            )

            if DEBUG:
                print(f"[DEBUG] Rust result: {rust_result}")

            if not rust_result.get("success"):
                return {
                    "success": False,
                    "error": rust_result.get("error", "Failed to submit request via Rust")
                }

            job_id = rust_result.get("job_id")
            if not job_id:
                return {
                    "success": False,
                    "error": "No job ID received from Rust"
                }

            if DEBUG:
                print(f"[DEBUG] Job ID: {job_id}")
                print(f"[DEBUG] Starting polling...")
            
            result = self._poll_for_completion(job_id, progress_callback)
            
            if not result:
                return {
                    "success": False,
                    "error": "Test generation failed"
                }
            
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "result": json.dumps(result),
                "elapsed": elapsed
            }

        except Exception as e:
            import traceback
            print(f"DEBUG: Exception in generate_test_for_method: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Generation failed: {str(e)}"
            }
    
    def _poll_for_completion(self, job_id: str, progress_callback=None) -> Optional[Dict]:
        """
        Poll for job completion
        
        Args:
            job_id: Job ID from initial request
            progress_callback: Optional callback for progress updates
            
        Returns:
            Result data if successful, None if failed
        """
        from ..http_client import get_http_client
        
        start_time = time.time()
        last_status_text = None
        poll_count = 0
        
        http_client = get_http_client()
        
        while True:
            seconds_elapsed = int(time.time() - start_time)
            
            if seconds_elapsed > self.MAX_POLL_DURATION_SECONDS:
                if progress_callback:
                    progress_callback(f"Test generation timed out after {self.MAX_POLL_DURATION_SECONDS // 60} minutes")
                return None
            
            # Update progress with percentage based on time (like Ruby)
            percent = min(int((seconds_elapsed / self.MAX_POLL_DURATION_SECONDS) * 100), 99)
            status_text = self._determine_status_text(seconds_elapsed)
            
            if status_text != last_status_text:
                if progress_callback:
                    progress_callback(status_text, percent)
                last_status_text = status_text
            
            time.sleep(self.POLL_INTERVAL_SECONDS)
            poll_count += 1
            
            # Poll API using Python HTTP client
            try:
                status_response = http_client._make_request(
                    f"cli/tng_python/content_responses/{job_id}",
                    method='GET'
                )
                
                if not status_response:
                    if DEBUG:
                        print(f"[DEBUG] Poll #{poll_count}: No response, continuing...")
                    continue  # Network error, keep polling
                
                status = status_response.get('status')
                
                if DEBUG and poll_count % 5 == 0:  # Log every 5th poll
                    print(f"[DEBUG] Poll #{poll_count}: status={status}, elapsed={seconds_elapsed}s")
                
                if status == 'completed':
                    result = status_response.get('result')
                    if DEBUG:
                        print(f"[DEBUG] Job completed! Result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
                    self._trigger_cleanup(job_id, http_client)
                    return result
                elif status == 'failed':
                    if progress_callback:
                        progress_callback("Test generation failed")
                    return None
                elif status in ['pending', 'processing']:
                    continue
                else:
                    continue  # Unknown status, keep polling
                    
            except Exception as e:
                # Continue polling on errors
                continue
    
    def _trigger_cleanup(self, job_id: str, http_client) -> None:
        """
        Trigger cleanup of content after successful generation
        
        Args:
            job_id: The job ID to cleanup
            http_client: HTTP client instance
        """
        try:
            http_client._make_request(
                f"cli/tng_python/content_responses/{job_id}/cleanup",
                method='PATCH'
            )
            if DEBUG:
                print(f"[DEBUG] Cleanup triggered for job {job_id}")
        except Exception as e:
            if DEBUG:
                print(f"[DEBUG] Cleanup request failed: {e}")
    
    def _determine_status_text(self, seconds_elapsed: int) -> str:
        """
        Determine status text based on time elapsed (like Ruby)
        
        Args:
            seconds_elapsed: Seconds elapsed since start
            
        Returns:
            Status message string
        """
        if seconds_elapsed <= 15:
            return "initializing..."
        elif seconds_elapsed <= 45:
            return "analyzing code structure..."
        elif seconds_elapsed <= 90:
            return "generating test cases..."
        elif seconds_elapsed <= 150:
            return "optimizing test logic..."
        elif seconds_elapsed <= 210:
            return "refining assertions..."
        elif seconds_elapsed <= 270:
            return "formatting output..."
        elif seconds_elapsed <= 330:
            return "finalizing tests..."
        else:
            return "completing generation..."

    def set_submit_url(self, url: str) -> None:
        """Set the submit URL for test generation"""
        self.submit_url = url

    def set_status_url_template(self, url_template: str) -> None:
        """Set the status URL template for polling"""
        self.status_url_template = url_template

    def save_test_file(self, test_content: str) -> Optional[Dict[str, Any]]:
        """
        Save test file from API response content
        
        Args:
            test_content: JSON string response from API
            
        Returns:
            Dictionary with file information or None if failed
        """
        try:
            parsed_response = json.loads(test_content)

            if parsed_response.get("error"):
                self.console.print(f"❌ API responded with an error: {parsed_response['error']}",
                                   style="bold red")
                return None

            # Support both shapes:
            # 1) Top-level fields: { file_content: "...", test_file_path: "..." }
            # 2) Nested object: { file_content: { file_content: "...", test_file_path: "..." } }
            # 3) Nested under test_file_content: { test_file_content: { ... same keys ... } }

            content_str = None
            meta_source = parsed_response

            fc = parsed_response.get("file_content")
            tfc = parsed_response.get("test_file_content")

            if isinstance(fc, dict):
                meta_source = fc
                content_str = meta_source.get("file_content") or meta_source.get("test_file_content")
            elif isinstance(tfc, dict):
                meta_source = tfc
                content_str = meta_source.get("file_content") or meta_source.get("test_file_content")
            else:
                # Assume top-level string content
                content_str = parsed_response.get("file_content") or parsed_response.get("test_file_content")

            if not content_str:
                self.console.print("❌ API response missing file content string",
                                   style="bold red")
                self.console.print(f"ℹ️ Response keys: {list(parsed_response.keys())}",
                                   style="bold cyan")
                return None

            # Resolve file path from the most specific source
            file_path = (meta_source.get("test_file_path") or
                         meta_source.get("file_path") or
                         meta_source.get("file_name") or
                         meta_source.get("file") or
                         parsed_response.get("test_file_path") or
                         parsed_response.get("file_path") or
                         parsed_response.get("file_name") or
                         parsed_response.get("file"))

            if not file_path:
                self.console.print("❌ API response missing test_file_path or file_path field",
                                   style="bold red")
                self.console.print(f"ℹ️ Response keys: {list(parsed_response.keys())}",
                                   style="bold cyan")
                return None

            # Create directory if it doesn't exist and write file
            file_path_obj = Path(file_path)
            if not str(file_path_obj).startswith("tests/"):
                file_path_obj = Path("tests") / file_path_obj.name

            # Ensure Python test files have .py extension
            if not file_path_obj.name.endswith('.py'):
                # Replace any other extension with .py
                stem = file_path_obj.stem
                if '.' in stem:
                    # Handle cases like "test.rb" -> "test.py"
                    stem = stem.split('.')[0]
                file_path_obj = file_path_obj.parent / f"{stem}.py"

            # Add timestamp prefix if filename doesn't have one
            filename = file_path_obj.name
            if not self._has_timestamp_prefix(filename):
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                new_filename = f"{timestamp}_{filename}"
                file_path_obj = file_path_obj.parent / new_filename

            # Write the file
            try:
                file_path_obj.write_text(content_str)
            except FileNotFoundError:
                # Create directory if it doesn't exist
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)
                file_path_obj.write_text(content_str)

            absolute_path = file_path_obj.resolve()

            # Run ruff validation on the saved file
            self._run_ruff_validation(str(absolute_path))

            return {
                "file_path": str(file_path_obj),  # Return actual saved path with timestamp
                "absolute_path": str(absolute_path),
                "test_class_name": meta_source.get("test_class_name") or parsed_response.get("test_class_name"),
                "method_name": meta_source.get("method_name") or parsed_response.get("method_name"),
                "framework": meta_source.get("framework") or parsed_response.get("framework", "pytest")
            }

        except json.JSONDecodeError as e:
            self.console.print(f"❌ Failed to parse API response as JSON: {e}",
                               style="bold red")
            self.console.print(f"📄 Raw response: {test_content[:200]}...",
                               style="dim white")
            raise
        except Exception as e:
            self.console.print(f"❌ Failed to save test file: {e}",
                               style="bold red")
            return None

    def get_test_frameworks(self) -> list:
        """Get list of supported test frameworks"""
        return ["pytest", "unittest"]

    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration"""
        config = get_enabled_config()
        api_key = get_api_key()

        issues = []
        if not config:
            issues.append("No configuration found")
        if not api_key:
            issues.append("No API key configured")
        if config and not config.get('base_url') and not config.get('submit_url'):
            issues.append("Base URL or Submit URL not configured")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": config,
            "has_api_key": bool(api_key)
        }

    def _get_dependency_content(self) -> tuple:
        """Get dependency file content and filename based on user configuration"""
        try:
            from ..config import get_config
            config = get_config()
            if hasattr(config, 'DEPENDENCY_FILE') and config.DEPENDENCY_FILE:
                dep_file_path = Path(config.DEPENDENCY_FILE)
                if dep_file_path.exists():
                    content = dep_file_path.read_text(encoding='utf-8')
                    filename = dep_file_path.name
                    return content, filename
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Could not read dependency file: {e}")

        return None, None

    def _has_timestamp_prefix(self, filename: str) -> bool:
        """
        Check if filename has numeric prefix (any numbers followed by underscore)

        Args:
            filename: The filename to check

        Returns:
            True if filename starts with numbers and underscore
        """
        import re
        # Pattern: one or more digits followed by underscore at start of filename
        numeric_pattern = r'^\d+_'
        return bool(re.match(numeric_pattern, filename))

    def _run_ruff_validation(self, file_path: str) -> None:
        """
        Run ruff validation on the saved test file
        
        Args:
            file_path: Absolute path to the test file
        """
        try:
            # Run ruff silently; perform safe fixes if needed, but do not print to user
            subprocess.run([
                "ruff", "check", file_path
            ], capture_output=True, text=True, timeout=30)

            subprocess.run([
                "ruff", "check", "--fix", file_path
            ], capture_output=True, text=True, timeout=30)

            subprocess.run([
                "ruff", "check", file_path
            ], capture_output=True, text=True, timeout=30)

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Intentionally suppress all output; ruff is best-effort
            pass
