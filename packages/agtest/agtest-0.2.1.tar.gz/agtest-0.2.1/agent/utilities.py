import re
import logging
import ast
import os
from enum import Enum
from . import config

def detect_file_type(filepath: str) -> str:
    """
    Detects whether the given file belongs to a controller or service.
    Returns 'controller', 'service', or 'unknown'.
    """
    filepath_lower = filepath.lower()
    filepath_lower = filepath_lower.replace("\\", "/")

    if "/controller" in filepath_lower or "/controllers" in filepath_lower:
        return "controller"
    elif "/service" in filepath_lower or "/services" in filepath_lower:
        return "service"
    else:
        return "unknown"    

def get_prefix_for_controller(controller_name: str, api_content: str) -> str | None:
    """
    Extracts the router prefix for the given controller name from the api.py content.
    """
    pattern = (
        rf"include_router\s*\(\s*{controller_name}\.router\s*,\s*prefix\s*=\s*['\"]([^'\"]+)['\"]"
    )

    match = re.search(pattern, api_content)
    if match:
        return match.group(1) 
    return None

def detect_controller_prefix(filepath: str,api_path:str) -> str | None:
    """
    Detects the route prefix for a given controller by inspecting api.py.
    Returns the prefix  if found, otherwise None.
    """
    controller_name = os.path.basename(filepath).replace(".py", "")
    
    with open(api_path, "r") as f:
        api_content = f.read()

    prefix = get_prefix_for_controller(controller_name, api_content)
    if not prefix:
        logging.warning(f"No prefix found for '{controller_name}' in api.py")

    return prefix

def extract_schemas_and_modules(file_content: str) -> tuple[list[str], list[str]]:
    """
    Extracts:
      1. Schema/model class names imported in the file.
      2. Their full module paths (supports nested imports).
    """
    pattern = ( r"from\s+([\w\.]*\b(?:schema|schemas|model|models)\b[\w\.]*)\s+"
                r"import\s*\(?([^)]+?)\)?(?=\n|$)")
    matches = re.findall(pattern, file_content, re.DOTALL)

    schema_names, module_paths = [], []

    for module_path, imported_part in matches:
        module_paths.append(module_path.strip())
        imports_clean = re.sub(r"\\\n|\n", " ", imported_part.strip())

        for name in re.split(r"[, \s]+", imports_clean):
            if name and re.match(r"^[A-Z][A-Za-z0-9_]*$", name):
                schema_names.append(name)

    return sorted(set(schema_names)), sorted(set(module_paths))

def extract_schema_metadata_from_ast(schema_name: str, module_paths: list[str], workdir: str):
    """
    Locate and parse a schema class from its module path without importing.
    Flow:
    - Loop through module paths.
    - Convert module to file path.
    - Parse file AST.
    - Walk AST and find class by name.
    - Collect schema type, fields, and validators.
    - Return structured metadata if found else None.
    """
    for module_path in module_paths:
        file_path = find_schema_file(module_path, workdir)
        if not file_path:
            continue

        tree = parse_ast_file(file_path)
        if not tree:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == schema_name:
                return {
                    "schema_name": schema_name,
                    "module_path": module_path,
                    "schema_type": get_schema_type(node),
                    "fields": extract_fields(node),
                    "validators": extract_validators(node),
                }

    return None

def find_schema_file(module_path: str, workdir: str) -> str | None:
    """
    Resolve module path → file path.
    - Convert dotted module path to file system path.
    - Append .py extension.
    - Check if file exists inside the working directory.
    - Return file path if found, else None.
    """
    rel = module_path.replace(".", os.sep) + ".py"
    abs_path = os.path.join(workdir, rel)
    return abs_path if os.path.exists(abs_path) else None

def parse_ast_file(path: str):
    """
    Parse a Python file into an AST.
    - Open file safely.
    - Parse using ast.parse().
    - Return None if syntax error exists (invalid Python).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return ast.parse(f.read())
    except SyntaxError:
        return None

def get_schema_type(node: ast.ClassDef) -> str:
    """
    Detect schema type based on base classes.
    - Check class base types: BaseModel, SQLAlchemy Base, Enum.
    - Return a label describing the class type.
    """
    bases = [
        b.id if isinstance(b, ast.Name) else getattr(b, "attr", "")
        for b in node.bases
    ]
    if "BaseModel" in bases: 
        return "pydantic_model"
    if any(b in ("Base", "DeclarativeBase") for b in bases):
        return "sqlalchemy_model"
    if "Enum" in bases:
        return "enum"
    return "class"

def extract_fields(node: ast.ClassDef) -> dict:
    """
    Extract field definitions from a class AST.
    Flow:
    - Loop through class body statements.
    - Detect Pydantic style annotated fields (AnnAssign).
    - Detect SQLAlchemy Column() assignments.
    - Collect field name, type, default, required flag, and SQLAlchemy args.
    """
    fields = {}

    for stmt in node.body:

        # Pydantic annotated field: name: type = default
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            field_name = stmt.target.id
            field_type = getattr(stmt.annotation, "id", str(stmt.annotation))
            default = getattr(stmt.value, "value", None) if stmt.value else None
            
            fields[field_name] = {
                "type": field_type,
                "default": default,
                "required": stmt.value is None
            }

        elif isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name):
            field_name = stmt.targets[0].id

            if isinstance(stmt.value, ast.Call) and getattr(stmt.value.func, "id", None) == "Column":
                col_type = None
                if stmt.value.args:
                    arg = stmt.value.args[0]
                    if isinstance(arg, ast.Name):
                        col_type = arg.id
                    elif isinstance(arg, ast.Attribute):
                        col_type = arg.attr

                kwargs = {kw.arg: getattr(kw.value, "value", None) for kw in stmt.value.keywords}

                fields[field_name] = {
                    "type": col_type or "Column",
                    **kwargs
                }

    return fields

def extract_validators(node: ast.ClassDef) -> list[str]:
    """
    Extract Pydantic validator method names.
    Flow:
    - Scan class methods.
    - Detect @validator or @field_validator decorators.
    - Collect function names.
    """
    validators = []

    for stmt in node.body:
        if isinstance(stmt, ast.FunctionDef):
            for deco in stmt.decorator_list:
                if isinstance(deco, ast.Call) and getattr(deco.func, "attr", "") == "field_validator":
                    validators.append(stmt.name)

                if isinstance(deco, ast.Call) and getattr(deco.func, "id", "") == "validator":
                    validators.append(stmt.name)

    return validators

def detect_provider_from_key(api_key: str):
    """
    Detects which AI provider an API key belongs to using known prefixes.
    Returns (provider_name, env_var_name, model_name).
    """
    for provider, (env_name, model, pattern) in config.KEY_PATTERNS.items():
        if api_key.startswith(pattern):
            return provider, env_name, model

    # Default fallback to Gemini
    logging.warning("Could not auto-detect provider from key prefix.")
    return "google", "GOOGLE_API_KEY", "models/gemini-2.5-flash"

def set_provider_in_config(provider: str, env_key: str, model_name: str, api_key: str):
    """
    Updates environment variables and config dynamically based on detected provider.
    """
    os.environ[env_key] = api_key
    setattr(config, env_key, api_key)
    config.MODEL_NAME = model_name
    logging.info(f"Provider set to: {provider.capitalize()} (model: {model_name})")


def prompt_for_api_key():
    """
    Prompts user for an API key and auto-detects provider.
    Returns (provider_name, api_key).
    """
    api_key = input("\nEnter your API key ").strip()
    if not api_key:
        logging.error("API key is required!")
        return None, None

    provider, env_key, model = detect_provider_from_key(api_key)
    set_provider_in_config(provider, env_key, model, api_key)

    return provider, api_key