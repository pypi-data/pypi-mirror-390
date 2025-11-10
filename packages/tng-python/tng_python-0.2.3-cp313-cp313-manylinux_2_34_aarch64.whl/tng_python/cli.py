import configparser
import importlib
import platform
from pathlib import Path
from typing import Optional, List

if platform.python_version_tuple()[1] >= "11":
    import tomllib  # Python 3.11+
else:
    import tomli as tomllib  # fallback for older Python versions


SUPPORTED_MOCK_LIBRARIES = [
    "pytest-mock",
    "doublex",
    "flexmock",
    "sure",
    "unittest.mock",
    "mock"
]

SUPPORTED_HTTP_MOCK_LIBRARIES = [
    "responses",
    "httpretty",
    "requests-mock",
    "vcr",
    "betamax",
    "httmock"
]

SUPPORTED_FACTORY_LIBRARIES = [
    "fixtures",
    "factory_boy",
    "mixer",
    "model_bakery",
    "faker",
    "hypothesis",
    "polyfactory",
    "mimesis"
]

SUPPORTED_AUTHORIZATION_LIBRARIES = [
    "django-guardian",
    "django-rules",
    "django-permission",
    "flask-principal",
    "flask-security",
    "casbin",
    "fastapi-permissions",
    "authlib"
]

SUPPORTED_AUTH_LIBRARIES = [
    "django-auth",
    "django-allauth",
    "djoser",
    "flask-login",
    "flask-user",
    "flask-security",
    "flask-jwt-extended",
    "fastapi-users",
    "fastapi-login",
    "authlib",
    "python-jose"
]

SUPPORTED_FRAMEWORKS = [
    # Web Frameworks
    "django", "flask", "fastapi", "tornado", "sanic", "pyramid",
    "bottle", "cherrypy", "falcon", "starlette",
    # ML/AI Frameworks
    "tensorflow", "pytorch", "scikit-learn", "transformers", "mlflow",
    "wandb", "jax", "xgboost", "lightgbm", "catboost", "jupyter", "ml-project",
    # Generic
    "generic"
]

SUPPORTED_TEST_FRAMEWORKS = [
    "pytest", "nose2", "robotframework", "behave", "lettuce",
    "testify", "green", "ward", "hypothesis"
]

SUPPORTED_DATABASES = [
    "postgresql", "mongodb", "mysql", "redis", "sqlite"
]

SUPPORTED_CACHE_SYSTEMS = [
    "redis", "memcached"
]

SUPPORTED_EMAIL_BACKENDS = [
    "django-email", "flask-mail", "fastapi-mail", "sendgrid",
    "mailgun", "postmark", "aws-ses", "smtplib"
]

SUPPORTED_JOB_SYSTEMS = [
    "celery", "rq", "dramatiq", "huey", "apscheduler",
    "django-q", "arq", "taskiq"
]

SUPPORTED_ORMS = [
    "django-orm", "sqlalchemy", "peewee", "tortoise-orm",
    "sqlmodel", "databases", "mongoengine", "beanie"
]


def format_options_list(options_list):
    """Format a list of options for display in comments"""
    if isinstance(options_list, list):
        return ", ".join(options_list)
    return str(options_list)


def get_dependency_content():
    content = ""

    # requirements.txt (pip)
    if Path("requirements.txt").exists():
        with open("requirements.txt") as f:
            content += f.read().lower() + "\n"

    # requirements-dev.txt, requirements-test.txt etc
    for req_file in Path(".").glob("requirements*.txt"):
        if req_file.exists():
            with open(req_file) as f:
                content += f.read().lower() + "\n"

    # pyproject.toml (poetry, uv, hatch, etc)
    if Path("pyproject.toml").exists() and tomllib:
        try:
            with open("pyproject.toml", "rb") as f:
                pyproject_data = tomllib.load(f)
                # Poetry dependencies
                if "tool" in pyproject_data and "poetry" in pyproject_data["tool"]:
                    deps = pyproject_data["tool"]["poetry"].get("dependencies", {})
                    dev_deps = pyproject_data["tool"]["poetry"].get("group", {}).get("dev", {}).get("dependencies", {})
                    content += " ".join(deps.keys()).lower() + "\n"
                    content += " ".join(dev_deps.keys()).lower() + "\n"
                # UV dependencies
                if "project" in pyproject_data:
                    deps = pyproject_data["project"].get("dependencies", [])
                    optional_deps = pyproject_data["project"].get("optional-dependencies", {})
                    content += " ".join(deps).lower() + "\n"
                    for group_deps in optional_deps.values():
                        content += " ".join(group_deps).lower() + "\n"
        except Exception:
            pass

    # Pipfile (pipenv)
    if Path("Pipfile").exists():
        try:
            with open("Pipfile") as f:
                pipfile_content = f.read().lower()
                content += pipfile_content + "\n"
        except Exception:
            pass

    # setup.py
    if Path("setup.py").exists():
        try:
            with open("setup.py") as f:
                setup_content = f.read().lower()
                content += setup_content + "\n"
        except Exception:
            pass

    # setup.cfg
    if Path("setup.cfg").exists():
        try:
            config = configparser.ConfigParser()
            config.read("setup.cfg")
            if "options" in config:
                install_requires = config["options"].get("install_requires", "")
                content += install_requires.lower() + "\n"
        except Exception:
            pass

    # environment.yml (conda)
    if Path("environment.yml").exists():
        try:
            with open("environment.yml") as f:
                env_content = f.read().lower()
                content += env_content + "\n"
        except Exception:
            pass

    return content


def init_config():
    """Initialize TNG configuration file"""
    config_path = Path("tng_config.py")

    if config_path.exists():
        response = input(f"Configuration file already exists at {config_path}. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Skipping configuration file creation.")
            return

    dependency_content = get_dependency_content()
    framework = detect_framework()
    test_framework = detect_test_framework()
    test_directory = detect_test_directory()
    mock_library = detect_mock_library(dependency_content)
    http_mock_library = detect_http_mock_library(dependency_content)
    factory_library = detect_factory_library(dependency_content)
    auth_library = detect_auth_library(dependency_content)
    authz_library = detect_authz_library(dependency_content)
    database_config = detect_database_config()
    email_config = detect_email_config()
    job_config = detect_job_config()
    dependency_file = detect_main_dependency_file()
    test_examples = detect_test_examples()
    fastapi_app_path = detect_fastapi_app_path()

    config_content = f'''# TNG Python Configuration
# This file was auto-generated based on your project setup.
# Edit the values below to customize TNG for your specific needs.

class TngConfig:
    # ==================== API Configuration ====================
    API_KEY = None  # Set your TNG API key here (get it from https://app.tng.sh)
    BASE_URL = "https://app.tng.sh/"  # Don't change unless instructed
    
    # ==================== Framework Detection ====================
    FRAMEWORK = "{framework}"        # Options: {format_options_list(SUPPORTED_FRAMEWORKS)} | Detected: {framework}
    TEST_FRAMEWORK = "{test_framework}"    # Options: {format_options_list(SUPPORTED_TEST_FRAMEWORKS)} | Detected: {test_framework}
    
    # Test Directory Configuration
    # Common Python patterns: tests/, test/, spec/, src/tests/, app/tests/, or "." for root
    # TNG will auto-detect your pattern, but you can override it here
    TEST_DIRECTORY = "{test_directory}"     # Detected: {test_directory}
    
    # ==================== Database & ORM Configuration ====================
    {generate_database_config(database_config)}
    
    # ==================== Email Configuration ====================
    {generate_email_config(email_config)}
    
    # ==================== Background Jobs Configuration ====================
    {generate_job_config(job_config)}
    
    # ==================== ML/AI Specific Settings ====================
    {generate_ml_config(framework)}
    
    # ==================== Testing Libraries ====================
    MOCK_LIBRARY = "{mock_library if mock_library else 'none'}"  # Options: {format_options_list(SUPPORTED_MOCK_LIBRARIES)}, none

    HTTP_MOCK_LIBRARY = "{http_mock_library if http_mock_library else 'none'}"  # Options: {format_options_list(SUPPORTED_HTTP_MOCK_LIBRARIES)}, none

    FACTORY_LIBRARY = "{factory_library if factory_library else 'none'}"  # Options: {format_options_list(SUPPORTED_FACTORY_LIBRARIES)}, none

    # ==================== Test Examples ====================
    # Example test files for LLM to learn patterns and reduce hallucinations
    # Format: [{{"name": "test_name", "path": "tests/test_file.py"}}]
    # Leave empty [] to auto-detect from project
    TEST_EXAMPLES = {test_examples}

    # ==================== Source Code Reading ====================
    # When enabled (True), TNG will only read the file where the method is located
    # and will not analyze other files in the project. This may increase the accuracy of the tests, but it may also increase the time it takes to generate the tests.
    READ_FILE_SOURCE_CODE = False

    # FastAPI App Path (for dynamic loading)
    # Specify the path to your FastAPI app for advanced introspection
    # Examples: "main.py", "app/main.py:app", "src/api.py:fastapi_app"
    FASTAPI_APP_PATH = "{fastapi_app_path}"  # Auto-detected FastAPI app location

    # ==================== Authentication & Authorization ====================
    AUTHENTICATION_ENABLED = {str(auth_library is not None and auth_library != "none")}
    
    AUTHENTICATION_LIBRARY = "{auth_library if auth_library else 'none'}"  # Options: {format_options_list(SUPPORTED_AUTH_LIBRARIES)}, custom, none

    # ⚠️  IMPORTANT: AUTHENTICATION CONFIGURATION REQUIRED ⚠️
    # You MUST configure your authentication methods below for TNG to work properly.
    # Uncomment and modify the authentication_methods configuration:

    # Authentication Methods (multiple methods supported)
    # Supported auth_types: session, jwt, token_auth, basic_auth, oauth, headers, custom
    # EXAMPLE: Uncomment and modify these examples to match your app's authentication:

    # AUTHENTICATION_METHODS = [
    {generate_auth_examples(framework)}
    # ]
    # Remember to configure your authentication methods above!

    AUTHORIZATION_LIBRARY = "{authz_library if authz_library else 'none'}"  # Options: {format_options_list(SUPPORTED_AUTHORIZATION_LIBRARIES)}, custom, none
    
    # ==================== DEPENDENCIES ====================
    # Main dependency file (auto-detected)
    # TNG will read this file to understand your project dependencies
    DEPENDENCY_FILE = "{dependency_file}"  # Detected: {dependency_file}

# Load configuration
config = TngConfig()

# ==================== USAGE NOTES ====================
# 1. Set your API_KEY above to start using TNG
# 2. Review detected settings - change any incorrect detections to 'none'
# 3. CONFIGURE AUTHENTICATION_METHODS if you have authentication
# 4. All "Options:" comments show available values you can use
# 5. Set AUTHENTICATION_ENABLED = False if you don't have authentication
# 6. Change database/email settings to 'none' if not applicable
# 7. TEST_DIRECTORY: Customize where TNG should place generated test files
#    - Use "tests" (most common), "test", "spec", or any custom path
#    - Use "." to place tests in the project root alongside source files
# 8. TEST_EXAMPLES: Configure example test files for LLM pattern learning
#    - Auto-detected from your test directory by default
#    - Add specific files: [{{"name": "auth_tests", "path": "tests/test_auth.py"}}]
#    - Leave empty [] to use auto-detection
'''

    with open(config_path, 'w') as f:
        f.write(config_content)

    print(f"✅ TNG configuration file created at {config_path}")
    print("📝 Please edit the file to configure your settings.")


def detect_framework():
    """Detect Python framework (web, ML/AI, or generic)"""
    # First check for ML/AI frameworks
    ml_framework = detect_ml_framework()
    if ml_framework != "generic":
        return ml_framework

    # Then check for web frameworks
    web_framework = detect_web_framework()
    if web_framework != "generic":
        return web_framework

    return "generic"


def detect_ml_framework():
    """Detect ML/AI framework"""
    frameworks_found = []

    # First check dependency files for ML frameworks (most reliable)
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        if "tensorflow" in content_lower or "keras" in content_lower:
            frameworks_found.append("tensorflow")
        if "torch" in content_lower or "pytorch" in content_lower:
            frameworks_found.append("pytorch")
        if "scikit-learn" in content_lower or "sklearn" in content_lower:
            frameworks_found.append("scikit-learn")
        if "transformers" in content_lower:
            frameworks_found.append("transformers")
        if "mlflow" in content_lower:
            frameworks_found.append("mlflow")
        if "wandb" in content_lower:
            frameworks_found.append("wandb")
        if "jax" in content_lower:
            frameworks_found.append("jax")
        if "xgboost" in content_lower:
            frameworks_found.append("xgboost")
        if "lightgbm" in content_lower:
            frameworks_found.append("lightgbm")
        if "catboost" in content_lower:
            frameworks_found.append("catboost")

    # Then check for imports as fallback
    ml_frameworks = [
        ("tensorflow", "tensorflow"),
        ("torch", "pytorch"),
        ("sklearn", "scikit-learn"),
        ("transformers", "transformers"),
        ("mlflow", "mlflow"),
        ("wandb", "wandb"),
        ("jax", "jax"),
        ("xgboost", "xgboost"),
        ("lightgbm", "lightgbm"),
        ("catboost", "catboost")
    ]

    for import_name, framework_name in ml_frameworks:
        try:
            __import__(import_name)
            if framework_name not in frameworks_found:
                frameworks_found.append(framework_name)
        except ImportError:
            pass

    if any(Path(".").glob("**/*.ipynb")):  # Jupyter notebooks
        frameworks_found.append("jupyter")

    if "transformers" in frameworks_found:
        return "transformers"  # NLP/LLM projects
    elif "tensorflow" in frameworks_found:
        return "tensorflow"
    elif "pytorch" in frameworks_found:
        return "pytorch"
    elif "scikit-learn" in frameworks_found:
        return "scikit-learn"
    elif any(fw in frameworks_found for fw in ["xgboost", "lightgbm", "catboost"]):
        return "gradient-boosting"
    elif "mlflow" in frameworks_found or "wandb" in frameworks_found:
        return "ml-experiment"
    elif "jupyter" in frameworks_found:
        return "jupyter-ml"
    elif frameworks_found:
        return "ml-project"

    return "generic"


def detect_web_framework():
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        # Check in order of specificity
        if "django" in content_lower:
            return "django"
        elif "fastapi" in content_lower:
            return "fastapi"
        elif "flask" in content_lower:
            return "flask"
        elif "tornado" in content_lower:
            return "tornado"
        elif "sanic" in content_lower:
            return "sanic"
        elif "pyramid" in content_lower:
            return "pyramid"
        elif "bottle" in content_lower:
            return "bottle"
        elif "cherrypy" in content_lower:
            return "cherrypy"
        elif "falcon" in content_lower:
            return "falcon"
        elif "starlette" in content_lower:
            return "starlette"

    # Then check for Django-specific files (most reliable)
    # Only check in project root, not recursively through venv or site-packages
    if Path("manage.py").exists():
        return "django"

    # Check for settings.py only in immediate subdirectories (not recursively)
    project_dirs = [d for d in Path(".").iterdir() if d.is_dir() and not d.name.startswith('.') and d.name not in ['venv', 'env', '.env', '__pycache__', 'node_modules', 'build', 'dist']]
    for dir_path in project_dirs:
        if (dir_path / "settings.py").exists():
            return "django"

    # Check for Pyramid config files
    if Path("development.ini").exists() or Path("production.ini").exists():
        return "pyramid"

    # Finally, try import checks as fallback
    frameworks_to_check = [
        "django", "fastapi", "flask", "tornado", "sanic",
        "pyramid", "bottle", "cherrypy", "falcon", "starlette"
    ]

    for framework in frameworks_to_check:
        try:
            __import__(framework)
            return framework
        except ImportError:
            continue

    return "generic"


def detect_test_framework():
    """Detect testing framework"""
    # First check dependency files for framework hints (most reliable)
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        if "pytest" in content_lower:
            return "pytest"
        elif "nose2" in content_lower:
            return "nose2"
        elif "robotframework" in content_lower or "robot-framework" in content_lower:
            return "robotframework"
        elif "behave" in content_lower:
            return "behave"
        elif "lettuce" in content_lower:
            return "lettuce"
        elif "testify" in content_lower:
            return "testify"
        elif "green" in content_lower:
            return "green"
        elif "ward" in content_lower:
            return "ward"
        elif "hypothesis" in content_lower:
            return "hypothesis"

    # Check for framework-specific config files
    # Only check in project root and immediate subdirectories, not venv
    if Path("pytest.ini").exists():
        return "pytest"

    project_dirs = [d for d in Path(".").iterdir() if d.is_dir() and not d.name.startswith('.') and d.name not in ['venv', 'env', '.env', '__pycache__', 'node_modules', 'build', 'dist']]
    if (Path(".") / "conftest.py").exists() or any((dir_path / "conftest.py").exists() for dir_path in project_dirs):
        return "pytest"

    if Path("nose2.cfg").exists() or Path("unittest.cfg").exists():
        return "nose2"

    if Path("behave.ini").exists():
        return "behave"

    # Check for framework-specific file patterns
    if any(Path(".").glob("**/*.robot")):
        return "robotframework"

    if any(Path(".").glob("**/features/*.feature")):
        # Could be behave or lettuce, try to distinguish
        if any(Path(".").glob("**/steps/*.py")):
            return "behave"
        else:
            return "lettuce"

    # Import checks as fallback
    frameworks_to_check = [
        "pytest", "nose2", "robot", "behave", "lettuce",
        "testify", "green", "ward", "hypothesis"
    ]

    for framework in frameworks_to_check:
        try:
            if framework == "robot":
                __import__("robot")
                return "robotframework"
            else:
                __import__(framework)
                return framework
        except ImportError:
            continue

    # Check for test files (last resort - could be any framework)
    if any(Path(".").glob("**/test_*.py")) or any(Path(".").glob("**/*_test.py")):
        return "pytest"  # Most common default

    # Final fallback
    return "pytest"


def detect_test_directory():
    """Detect test directory based on common Python conventions
    
    Python projects commonly use these test directory patterns:
    - tests/ (most common, plural form)
    - test/ (singular, but may conflict with Python's built-in test package)
    - spec/ (less common, borrowed from Ruby/RSpec conventions)
    - src/tests/, app/tests/ (nested within source directories)
    - Project root with test_*.py files (no separate directory)
    
    This function auto-detects the pattern used in your project.
    You can override this in tng_config.py by setting TEST_DIRECTORY.
    """
    # Check for existing test directories in order of preference
    test_dirs = ["tests", "test", "spec"]

    for test_dir in test_dirs:
        if Path(test_dir).exists() and Path(test_dir).is_dir():
            # Check if it actually contains test files
            test_files = (
                    list(Path(test_dir).glob("**/test_*.py")) +
                    list(Path(test_dir).glob("**/*_test.py")) +
                    list(Path(test_dir).glob("**/test*.py"))
            )
            if test_files:
                return test_dir

    # Check for nested test directories
    nested_patterns = [
        "src/tests", "app/tests", "lib/tests",
        "src/test", "app/test", "lib/test"
    ]

    for pattern in nested_patterns:
        if Path(pattern).exists() and Path(pattern).is_dir():
            test_files = (
                    list(Path(pattern).glob("**/test_*.py")) +
                    list(Path(pattern).glob("**/*_test.py")) +
                    list(Path(pattern).glob("**/test*.py"))
            )
            if test_files:
                return pattern

    # Check if test files are in project root
    root_test_files = (
            list(Path(".").glob("test_*.py")) +
            list(Path(".").glob("*_test.py"))
    )
    if root_test_files:
        return "."  # Current directory

    # Default fallback
    return "tests"


def contains_library(dependency_content: str, library: str) -> bool:
    return library in dependency_content


def detect_dependency(content: Optional[str], supported_options: List[str]) -> Optional[str]:
    if not content:
        return None

    for option in supported_options:
        if contains_library(content, option):
            try:
                # Verify if the detected library can be imported
                importlib.import_module(option)
                return option
            except ImportError:
                continue
    else:
        return None


def detect_mock_library(content: Optional[str]) -> Optional[str]:
    """Detect mocking library."""
    return detect_dependency(content, SUPPORTED_MOCK_LIBRARIES)


def detect_http_mock_library(content: Optional[str]) -> Optional[str]:
    """Detect HTTP mocking library."""
    return detect_dependency(content, SUPPORTED_HTTP_MOCK_LIBRARIES)


def detect_factory_library(content: Optional[str]) -> Optional[str]:
    """Detect factory/fixture library."""
    return detect_dependency(content, SUPPORTED_FACTORY_LIBRARIES)


def detect_auth_library(content: Optional[str]) -> Optional[str]:
    """Detect authentication library."""
    return detect_dependency(content, SUPPORTED_AUTH_LIBRARIES)


def detect_authz_library(content: Optional[str]) -> Optional[str]:
    """Detect authorization library."""
    return detect_dependency(content, SUPPORTED_AUTHORIZATION_LIBRARIES)


def detect_database_config():
    """Detect database and ORM configuration"""
    config = {
        'orm': detect_orm(),
        'databases': detect_databases(),
        'cache': detect_cache_systems(),
        'async_db': detect_async_db()
    }
    return config


def detect_orm():
    """Detect ORM/Database access layer"""
    orms_found = []

    # First check dependency files (most reliable)
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        if "django" in content_lower:
            orms_found.append("django-orm")
        if "sqlalchemy" in content_lower:
            orms_found.append("sqlalchemy")
        if "peewee" in content_lower:
            orms_found.append("peewee")
        if "tortoise-orm" in content_lower or "tortoise_orm" in content_lower:
            orms_found.append("tortoise-orm")
        if "sqlmodel" in content_lower:
            orms_found.append("sqlmodel")
        if "databases" in content_lower and ("asyncpg" in content_lower or "aiomysql" in content_lower):
            orms_found.append("databases")
        if "mongoengine" in content_lower:
            orms_found.append("mongoengine")
        if "beanie" in content_lower:
            orms_found.append("beanie")

    # Then check for imports as fallback
    orm_imports = [
        ("django", "django-orm"),
        ("sqlalchemy", "sqlalchemy"),
        ("peewee", "peewee"),
        ("tortoise", "tortoise-orm"),
        ("sqlmodel", "sqlmodel"),
        ("databases", "databases"),
        ("mongoengine", "mongoengine"),
        ("beanie", "beanie")
    ]

    for import_name, orm_name in orm_imports:
        try:
            __import__(import_name)
            if orm_name not in orms_found:
                orms_found.append(orm_name)
        except ImportError:
            pass

    return orms_found[0] if orms_found else "none"


def detect_databases():
    """Detect database systems"""
    databases_found = []

    # Database drivers mapping (excluding built-ins like sqlite3)
    drivers = {
        'psycopg2': 'postgresql',
        'psycopg': 'postgresql',
        'asyncpg': 'postgresql',
        'pymongo': 'mongodb',
        'motor': 'mongodb',
        'redis': 'redis',
        'aioredis': 'redis',
        'mysql-connector-python': 'mysql',
        'pymysql': 'mysql',
        'aiomysql': 'mysql'
        # Note: sqlite3 is built-in, only detect if explicitly used in dependencies
    }

    # First check dependency files (most reliable)
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        for driver, db in drivers.items():
            driver_variants = [
                driver.lower(),
                driver.replace('-', '_').lower(),
                driver.replace('-', '').lower()
            ]
            if any(variant in content_lower for variant in driver_variants):
                databases_found.append(db)

        # Also check for database names directly (only if explicitly mentioned)
        if "postgresql" in content_lower or "postgres" in content_lower:
            databases_found.append("postgresql")
        if "mongodb" in content_lower or "mongo" in content_lower:
            databases_found.append("mongodb")
        if "mysql" in content_lower:
            databases_found.append("mysql")
        # Only detect sqlite if explicitly mentioned in dependencies (not just sqlite3 import)
        if "sqlite" in content_lower and ("sqlite" in content_lower or "pysqlite" in content_lower):
            databases_found.append("sqlite")
        if "redis" in content_lower:
            databases_found.append("redis")

    # Then check for imports as fallback
    for driver, db in drivers.items():
        try:
            import_name = driver.replace('-', '_')
            __import__(import_name)
            if db not in databases_found:
                databases_found.append(db)
        except ImportError:
            pass

    return list(set(databases_found))


def detect_cache_systems():
    """Detect caching systems"""
    cache_systems = []

    # First check dependency files (most reliable)
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        if "redis" in content_lower or "aioredis" in content_lower:
            cache_systems.append("redis")
        if "memcached" in content_lower or "python-memcached" in content_lower or "pymemcache" in content_lower:
            cache_systems.append("memcached")

    # Then check for imports as fallback
    cache_imports = [
        ("redis", "redis"),
        ("memcache", "memcached"),
        ("pymemcache", "memcached")
    ]

    for import_name, cache_name in cache_imports:
        try:
            __import__(import_name)
            if cache_name not in cache_systems:
                cache_systems.append(cache_name)
        except ImportError:
            pass

    return cache_systems


def detect_async_db():
    """Detect async database support"""
    async_libs = []

    async_drivers = ['asyncpg', 'aiomysql', 'aioredis', 'motor', 'databases', 'tortoise']

    # First check dependency files (most reliable)
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        for driver in async_drivers:
            if driver in content_lower or driver.replace('_', '-') in content_lower:
                async_libs.append(driver)

    # Then check for imports as fallback
    for driver in async_drivers:
        try:
            __import__(driver)
            if driver not in async_libs:
                async_libs.append(driver)
        except ImportError:
            pass

    return len(async_libs) > 0


def detect_email_config():
    """Detect email sending libraries"""
    email_libs = []

    # First check dependency files (most reliable)
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        if "django" in content_lower:
            email_libs.append("django-email")
        if "flask-mail" in content_lower or "flask_mail" in content_lower:
            email_libs.append("flask-mail")
        if "fastapi-mail" in content_lower or "fastapi_mail" in content_lower:
            email_libs.append("fastapi-mail")
        if "sendgrid" in content_lower:
            email_libs.append("sendgrid")
        if "mailgun" in content_lower:
            email_libs.append("mailgun")
        if "postmarker" in content_lower:
            email_libs.append("postmark")
        if "boto3" in content_lower:
            email_libs.append("aws-ses")

    # Then check for imports as fallback (excluding built-ins like smtplib)
    email_imports = [
        ("django", "django-email"),
        ("flask_mail", "flask-mail"),
        ("fastapi_mail", "fastapi-mail"),
        ("sendgrid", "sendgrid"),
        ("mailgun", "mailgun"),
        ("postmarker", "postmark"),
        ("boto3", "aws-ses")
        # Note: smtplib is built-in, only detect if explicitly used in dependencies
    ]

    for import_name, email_name in email_imports:
        try:
            __import__(import_name)
            if email_name not in email_libs:
                email_libs.append(email_name)
        except ImportError:
            pass

    return list(set(email_libs))


def detect_job_config():
    """Detect background job systems"""
    job_systems = []

    # First check dependency files (most reliable)
    content = get_dependency_content()
    if content:
        content_lower = content.lower()
        if "celery" in content_lower:
            job_systems.append("celery")
        if "rq" in content_lower and "redis" in content_lower:
            job_systems.append("rq")
        if "dramatiq" in content_lower:
            job_systems.append("dramatiq")
        if "huey" in content_lower:
            job_systems.append("huey")
        if "apscheduler" in content_lower:
            job_systems.append("apscheduler")
        if "django-q" in content_lower or "django_q" in content_lower:
            job_systems.append("django-q")
        if "arq" in content_lower:
            job_systems.append("arq")
        if "taskiq" in content_lower:
            job_systems.append("taskiq")

    # Then check for imports as fallback
    job_imports = [
        ("celery", "celery"),
        ("rq", "rq"),
        ("dramatiq", "dramatiq"),
        ("huey", "huey"),
        ("apscheduler", "apscheduler"),
        ("django_q", "django-q"),
        ("arq", "arq"),
        ("taskiq", "taskiq")
    ]

    for import_name, job_name in job_imports:
        try:
            __import__(import_name)
            if job_name not in job_systems:
                job_systems.append(job_name)
        except ImportError:
            pass

    return list(set(job_systems))


def detect_main_dependency_file():
    """Detect the main dependency file to use"""
    # Check in order of preference (most specific to most generic)
    dependency_files = [
        "pyproject.toml",  # Modern Python standard
        "requirements.txt",  # Most common
        "Pipfile",  # Pipenv
        "setup.py",  # Legacy but still used
        "environment.yml",  # Conda
        "setup.cfg",  # Alternative setup
    ]

    for dep_file in dependency_files:
        if Path(dep_file).exists():
            return dep_file

    return None  # No dependency file found


def detect_fastapi_app_path():
    """Detect FastAPI app location for dynamic loading"""
    # Only detect if FastAPI is being used
    if detect_web_framework() != "fastapi":
        return None

    # Look for common FastAPI app files
    candidates = ['main.py', 'app.py', 'api.py', 'application.py']

    # Check root level first
    for candidate in candidates:
        app_file = Path(candidate)
        if app_file.exists():
            try:
                with open(app_file, 'r') as f:
                    content = f.read()
                    # Look for FastAPI instantiation
                    if 'FastAPI(' in content and 'from fastapi import' in content:
                        return candidate
            except:
                continue

    # Check in common subdirectories
    subdirs = ['app', 'src', 'api', 'fastapi_app']
    for subdir in subdirs:
        subdir_path = Path(subdir)
        if subdir_path.exists() and subdir_path.is_dir():
            for candidate in candidates:
                app_file = subdir_path / candidate
                if app_file.exists():
                    try:
                        with open(app_file, 'r') as f:
                            content = f.read()
                            if 'FastAPI(' in content and 'from fastapi import' in content:
                                return str(app_file)
                    except:
                        continue

    # Last resort: search recursively (but limit depth)
    try:
        for file_path in Path('.').glob('**/*.py'):
            # Skip common non-app directories
            if any(skip in file_path.parts for skip in [
                '__pycache__', 'venv', 'env', '.git', 'node_modules',
                'tests', 'test', 'migrations'
            ]):
                continue

            try:
                with open(file_path, 'r') as f:
                    content = f.read(2048)  # Read first 2KB
                    if ('FastAPI(' in content and
                        'from fastapi import' in content):
                        return str(file_path.relative_to('.'))
            except:
                continue
    except:
        pass

    return None


def detect_test_examples():
    """Auto-detect example test files for LLM pattern learning with folder-aware selection"""
    examples = []

    # Comprehensive exclusion list for build artifacts, caches, dependencies
    exclude_dirs = {
        '.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env', '.env',
        'build', 'dist', 'target', '.next', '.nuxt', 'coverage', '.pytest_cache',
        '.tox', '.cache', '.mypy_cache', '.DS_Store', 'htmlcov', '.coverage',
        'site-packages', 'lib', 'bin', 'scripts', '.vscode', '.idea', '.vs',
        'migrations', 'alembic', 'django_migrations'
    }

    # Also exclude files larger than 500KB (probably not good examples)
    MAX_FILE_SIZE = 500 * 1024  # 500KB

    # Find all test directories and subdirectories
    test_directories = find_test_directories(exclude_dirs)

    # Collect files by directory, taking up to 2 per directory
    collected_files = []

    for dir_path in test_directories:
        dir_files = find_valid_test_files_in_directory(dir_path, MAX_FILE_SIZE)

        # Sort by modification time (recent first), then by size (smaller files first)
        dir_files.sort(key=lambda x: (x.stat().st_mtime, x.stat().st_size), reverse=True)

        # Take up to 2 files from this directory
        collected_files.extend(dir_files[:2])

    # If we still don't have enough files, add more from the main test directories
    if len(collected_files) < 5:
        main_test_dirs = []
        for potential_dir in ["tests", "test", "spec"]:
            test_dir_path = Path(potential_dir)
            if test_dir_path.exists() and test_dir_path.is_dir():
                main_test_dirs.append(test_dir_path)

        for main_dir in main_test_dirs:
            main_files = find_valid_test_files_in_directory(main_dir, MAX_FILE_SIZE)
            # Remove already collected files
            main_files = [f for f in main_files if f not in collected_files]
            main_files.sort(key=lambda x: (x.stat().st_mtime, x.stat().st_size), reverse=True)
            remaining_slots = 5 - len(collected_files)
            collected_files.extend(main_files[:remaining_slots])

    # Convert to examples format
    for test_file in collected_files[:5]:
        try:
            examples.append({
                "name": test_file.name,
                "path": str(test_file.relative_to(Path(".")))
            })
        except Exception:
            continue

    return examples


def find_test_directories(exclude_dirs):
    """Find all test directories and subdirectories"""
    directories = []

    # Check common test directory names
    potential_main_dirs = ["tests", "test", "spec"]

    for main_dir_name in potential_main_dirs:
        main_dir_path = Path(main_dir_name)
        if main_dir_path.exists() and main_dir_path.is_dir():
            # Add main test directory
            directories.append(main_dir_path)

            # Find all subdirectories recursively
            try:
                for sub_dir in main_dir_path.rglob("*"):
                    if sub_dir.is_dir():
                        # Skip excluded directories
                        if any(excluded in sub_dir.parts for excluded in exclude_dirs):
                            continue

                        # Skip if it's not a directory with actual test files
                        if has_test_files(sub_dir):
                            directories.append(sub_dir)
            except Exception:
                continue

    return list(set(directories))


def has_test_files(dir_path):
    """Check if a directory contains test files"""
    if not dir_path.exists() or not dir_path.is_dir():
        return False

    # Check for common test file patterns
    patterns = ["test_*.py", "*_test.py", "*test*.py"]

    for pattern in patterns:
        try:
            if any(dir_path.glob(pattern)):
                return True
        except Exception:
            continue

    return False


def find_valid_test_files_in_directory(dir_path, max_file_size):
    """Find valid test files in a specific directory"""
    if not dir_path.exists() or not dir_path.is_dir():
        return []

    files = []
    patterns = ["test_*.py", "*_test.py", "*test*.py"]

    for pattern in patterns:
        try:
            for test_file in dir_path.glob(pattern):
                if test_file.is_file():
                    # Skip files that are too large
                    try:
                        if test_file.stat().st_size > max_file_size:
                            continue
                    except (OSError, AttributeError):
                        continue

                    # Skip files that aren't valid test files
                    if not _is_valid_test_file(test_file):
                        continue

                    files.append(test_file)
        except Exception:
            continue

    return list(set(files))


def _is_valid_test_file(file_path):
    """Check if a file is a valid test file by examining its content"""
    try:
        # Quick size check first
        if file_path.stat().st_size == 0:
            return False

        # Try to read first few lines
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1024)  # Read first 1KB

        # Check for Python test indicators
        test_indicators = [
            'def test_',      # pytest/unittest test functions
            'class Test',     # Test classes
            'import unittest', # unittest imports
            'import pytest',   # pytest imports
            'from unittest',   # unittest imports
            '@pytest.',       # pytest decorators
            'assert ',        # assertion statements
        ]

        # Must contain at least one test indicator
        if not any(indicator in content for indicator in test_indicators):
            return False

        # Basic Python syntax check - should not have obvious non-Python content
        if content.count('#!/') > 5 or content.count('<?xml') > 0:
            return False

        return True

    except (UnicodeDecodeError, IOError, OSError):
        return False


def generate_auth_examples(framework):
    """Generate framework-specific authentication examples"""
    if framework == "django":
        return '''#     {
    #         "method": "login_required",
    #         "file_location": "django.contrib.auth.decorators",
    #         "auth_type": "session"
    #     },
    #     {
    #         "method": "permission_required",
    #         "file_location": "django.contrib.auth.decorators", 
    #         "auth_type": "session"
    #     }'''
    elif framework == "flask":
        return '''#     {
    #         "method": "login_required",
    #         "file_location": "flask_login",
    #         "auth_type": "session"
    #     },
    #     {
    #         "method": "jwt_required",
    #         "file_location": "flask_jwt_extended",
    #         "auth_type": "jwt"
    #     }'''
    elif framework == "fastapi":
        return '''#     {
    #         "method": "get_current_user",
    #         "file_location": "app/auth.py",
    #         "auth_type": "jwt"
    #     },
    #     {
    #         "method": "get_current_active_user",
    #         "file_location": "app/auth.py",
    #         "auth_type": "jwt"
    #     }'''
    else:
        return '''#     {
    #         "method": "authenticate_user",
    #         "file_location": "app/auth.py", 
    #         "auth_type": "session"
    #     },
    #     {
    #         "method": "require_api_key",
    #         "file_location": "app/middleware.py",
    #         "auth_type": "headers"
    #     }'''


def generate_ml_config(framework):
    """Generate ML/AI specific configuration"""
    if framework in ['tensorflow', 'pytorch', 'scikit-learn', 'transformers', 'ml-project', 'jupyter-ml']:
        return '''# ML/AI Specific Settings
    EXPERIMENT_TRACKING = True  # Track experiments and model versions
    MODEL_VERSIONING = True     # Version control for models
    DATA_VERSIONING = True      # Version control for datasets
    NOTEBOOK_ANALYSIS = True    # Analyze Jupyter notebooks
    MODEL_REGISTRY = None       # Options: mlflow, wandb, neptune, None
    # Model Training Settings
    TRACK_HYPERPARAMETERS = True
    TRACK_METRICS = True
    TRACK_ARTIFACTS = True'''
    else:
        return '''# Standard Project Settings'''


def generate_database_config(db_config):
    """Generate database configuration section"""
    orm = db_config['orm']
    databases = db_config['databases']
    cache = db_config['cache']
    async_db = db_config['async_db']

    return f'''# Database & ORM Configuration
    ORM = "{orm}"  # Options: {format_options_list(SUPPORTED_ORMS)}, none | Detected: {orm}
    DATABASES = {databases}  # Options: {format_options_list(SUPPORTED_DATABASES)} | Detected: {', '.join(databases) if databases else 'none'}
    CACHE_SYSTEMS = {cache}  # Options: {format_options_list(SUPPORTED_CACHE_SYSTEMS)} | Detected: {', '.join(cache) if cache else 'none'}
    ASYNC_DATABASE_SUPPORT = {async_db}'''


def generate_email_config(email_config):
    """Generate email configuration section"""
    email_libs = email_config
    primary_email = email_libs[0] if email_libs else "none"

    return f'''# Email Configuration
    EMAIL_BACKEND = "{primary_email}"  # Options: {format_options_list(SUPPORTED_EMAIL_BACKENDS)}, none | Detected: {primary_email}
    EMAIL_PROVIDERS = {email_libs}  # All detected email libraries'''


def generate_job_config(job_config):
    """Generate background jobs configuration section"""
    job_systems = job_config
    primary_job = job_systems[0] if job_systems else "none"

    return f'''# Background Jobs Configuration
    JOB_QUEUE = "{primary_job}"  # Options: {format_options_list(SUPPORTED_JOB_SYSTEMS)}, none | Detected: {primary_job}
    JOB_SYSTEMS = {job_systems}  # All detected job systems'''
