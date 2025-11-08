import unittest
from unittest import mock

from tng_python.cli import SUPPORTED_MOCK_LIBRARIES, SUPPORTED_HTTP_MOCK_LIBRARIES, SUPPORTED_FACTORY_LIBRARIES, \
    SUPPORTED_AUTH_LIBRARIES, SUPPORTED_AUTHORIZATION_LIBRARIES


class TestCliDetectMockLibrary(unittest.TestCase):
    def test_detect_mock_library(self) -> None:
        tested_libraries = SUPPORTED_MOCK_LIBRARIES + ["", None]
        expected_results = SUPPORTED_MOCK_LIBRARIES + [None, None]

        for library, expected in zip(tested_libraries, expected_results):
            with self.subTest(library=library, expected=expected):
                with mock.patch("tng_python.cli.importlib.import_module"):
                    with mock.patch("tng_python.cli.get_dependency_content", return_value=f"{library}\n") as mock_content:
                        from tng_python.cli import detect_mock_library
                        detected_library = detect_mock_library(mock_content.return_value)
                        assert detected_library == expected

    def test_detect_http_mock_library(self) -> None:
        tested_libraries = SUPPORTED_HTTP_MOCK_LIBRARIES + ["", None]
        expected_results = SUPPORTED_HTTP_MOCK_LIBRARIES + [None, None]

        for library, expected in zip(tested_libraries, expected_results):
            with self.subTest(library=library, expected=expected):
                with mock.patch("tng_python.cli.importlib.import_module"):
                    with mock.patch("tng_python.cli.get_dependency_content", return_value=f"{library}\n") as mock_content:
                        from tng_python.cli import detect_http_mock_library
                        detected_library = detect_http_mock_library(mock_content.return_value)
                        assert detected_library == expected

    def test_detect_factory_library(self) -> None:
        tested_libraries = SUPPORTED_FACTORY_LIBRARIES + ["", None]
        expected_results = SUPPORTED_FACTORY_LIBRARIES + [None, None]

        for library, expected in zip(tested_libraries, expected_results):
            with self.subTest(library=library, expected=expected):
                with mock.patch("tng_python.cli.importlib.import_module"):
                    with mock.patch("tng_python.cli.get_dependency_content", return_value=f"{library}\n") as mock_content:
                        from tng_python.cli import detect_factory_library
                        detected_library = detect_factory_library(mock_content.return_value)
                        assert detected_library == expected

    def test_detect_auth_library(self) -> None:
        tested_libraries = SUPPORTED_AUTH_LIBRARIES + ["", None]
        expected_results = SUPPORTED_AUTH_LIBRARIES + [None, None]

        for library, expected in zip(tested_libraries, expected_results):
            with self.subTest(library=library, expected=expected):
                with mock.patch("tng_python.cli.importlib.import_module"):
                    with mock.patch("tng_python.cli.get_dependency_content", return_value=f"{library}\n") as mock_content:
                        from tng_python.cli import detect_auth_library
                        detected_library = detect_auth_library(mock_content.return_value)
                        assert detected_library == expected

    def test_detect_authorization_library(self) -> None:
        tested_libraries = SUPPORTED_AUTHORIZATION_LIBRARIES + ["", None]
        expected_results = SUPPORTED_AUTHORIZATION_LIBRARIES + [None, None]

        for library, expected in zip(tested_libraries, expected_results):
            with self.subTest(library=library, expected=expected):
                with mock.patch("tng_python.cli.importlib.import_module"):
                    with mock.patch("tng_python.cli.get_dependency_content", return_value=f"{library}\n") as mock_content:
                        from tng_python.cli import detect_authz_library
                        detected_library = detect_authz_library(mock_content.return_value)
                        assert detected_library == expected
