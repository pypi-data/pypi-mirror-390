from .utilities import  extract_schema_metadata_from_ast, extract_schemas_and_modules
import textwrap
import os
import logging
import google.generativeai as genai
import sys
import requests
from . import config
from openai import OpenAI
def get_model_client():
    """
    Initialize and return an AI model client.
    Supports Google Gemini and OpenAI.
    Exits immediately if no valid API key is found.
    """
    google_key = config.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
    openai_key = config.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    providers = [
        (
            "gemini",
            google_key,
            lambda: (
                genai.configure(api_key=google_key),
                genai.GenerativeModel(os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")),
            )[1],
        ),
        (
            "openai",
            openai_key,
            lambda: OpenAI(api_key=openai_key),
        ),
    ]

    client_tuple = next(((name, init()) for name, key, init in providers if key), None)

    if not client_tuple:
        logging.error("No API key found. Please set GOOGLE_API_KEY or OPENAI_API_KEY.")
        sys.exit(1)

    provider, _ = client_tuple
    MODEL_NAME = (
        os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
        if provider == "gemini"
        else os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )
    return client_tuple

def generate_response(client_tuple, prompt: str) -> str:
    """
    Generate AI response using either Google Gemini or OpenAI.
    Keeps logic clean, minimal, and provider-aware.
    """
    provider, client = client_tuple

    if provider == "gemini":
        response = client.generate_content(prompt)
        return response.text.strip()

    elif provider == "openai":
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            
        )
        return response.choices[0].message.content.strip()

    else:
        raise ValueError(f"Unsupported provider: {provider}")

def build_prompt(filepath: str, file_type: str, file_content: str, prefix: str = "") -> str:
    """
    Builds a clean, context-aware prompt for the AI to generate pytest test cases.
    """

    base_guidelines = textwrap.dedent("""
        Guidelines:
        - Write tests using pytest (not unittest).
        - Follow FastAPI testing best practices.
        - Assume conftest.py handles DB setup, TestClient, and authentication fixtures.
        - Do not redefine or recreate DB connections or clients.
        - Always mock DB calls using MagicMock 
        - Add clear, meaningful test names and assert messages.
        - If the function uses a Pydantic schema (request or response), 
          generate payloads that respect the schema’s validation fields.
        - Always include one edge or negative test per function.
        - Mock network calls and DB sessions using unittest.mock or MagicMock.
        - Follow the naming convention: test_<function_name>_<scenario>.
        Assertion Rules:
            - For HTTP responses, use `assert response.status_code == expected_status`
            where `expected_status` is inferred logically (e.g., 200 for success, 404 for not found).
            - Do **not hardcode** literals like `200`, `"success"`, or `"error"`.
            - Instead, refer to constants (e.g., `HTTP_200_OK`, `STATUS_SUCCESS`) defined in the source code.
            - If constants are unavailable, write flexible assertions like:
            `assert response.status_code in (200, 201)`
            - For JSON responses, verify **keys and structure**, not exact string matches:
            `assert "message" in response.json()`
            `assert isinstance(response.json().get("data"), dict)`
            - Before asserting `.assert_called_once()` or `.assert_called_with()`,
            ensure the mocked method path matches exactly what’s imported in the controller.
            - If the service method isn’t called, confirm the payload is schema-valid first.
            - Try to give assertion where needed as so many AssertionError not comes use the defined statement only to check assertion or make custom one so the response get matches.
        Import & Patching Rules
            - When mocking or importing classes, always use their full module path 
            as defined in the import statements within the provided file.
            - Avoid using shortened or assumed paths such as only `controllers` or `services`.
            - Derive the correct path directly from the file’s actual import structure.
            - Ensure that all patch and import statements match the complete module hierarchy
            so that they work correctly across projects with different base package names.
            - Use AsyncMock **only** if the original function is defined with `async def`.
                For normal (synchronous) functions, continue using MagicMock.
                Never wrap a sync method with AsyncMock, as it causes `TypeError: object AsyncMock can't be used in 'await' expression`.

            - If multiple tasks are spawned using asyncio.gather or TaskGroup, 
            ensure each mocked service call is an async-compatible coroutine and does not raise unhandled exceptions.
            Always wrap them inside try/except or mock them to return valid responses.
            - Always patch using the full, absolute module import path that appears inside the controller file.

            - If multiple tasks are spawned using asyncio.gather or TaskGroup, 
            ensure each mocked service call is an async-compatible coroutine.
            - Always patch using the full, absolute module import path that appears inside the controller file.
            - Do not patch via local aliases, test-level imports, or relative imports.
            - Before asserting call counts, ensure that the mocked method is attached to the same class
            and module path that the controller uses at runtime. 
        -Do not use model_dump() use dict() in place where needed as my code is pydantic 1 compatible.  
        -Handle CustomException as it has status,message and details so make test case accordingly         
        -Just include call as needed donot call things twice or thrice as it give assertion error.      
        -Do not use mocker while making test cases use unittest.mock or MagicMock only.                                
    """)

    controller_instructions = textwrap.dedent(f"""
        COMPULSORY RULES FOR CONTROLLER TEST GENERATION 
        For controllers:
        - You MUST always include fixtures for:
            • A mocked database session (MagicMock(spec=Session)).
            • A FastAPI TestClient configured with:
                - Middleware injecting request.state.user_name, request.state.user_role, and request.state.org_client.
                - A registered CustomException handler that returns JSON with 'message' and 'details'.
                - The target router included with the correct prefix (“{prefix}”).
                - A dependency override for get_db that returns the mock DB session.
                - Cleanup of app.dependency_overrides after yield.
        - These fixtures are **mandatory** and must be defined in every controller test file.
        - Make post request correctly with json payload as it is not getting covered so make it correctly.
        - All tests must send HTTP requests through the actual FastAPI endpoints using this TestClient.
        - Always use 'http://' URLs, not 'https://'.
        - Each test must validate both:
            • The response status_code (using logical or constant-based assertions).
            • The JSON response structure (keys like "message", "data", "details").
        - Never recreate or redefine the real database — assume conftest.py provides global configuration.
        - Do NOT create tests for CustomException itself or for global error handlers.
        - Each route function must have:
            • One success case.
            • One edge or negative case.
        - Always recreate the mock DB session for each test because the system follows a 
        "session-per-request" pattern.
        - Middleware injection, CustomException handler, and dependency overrides are COMPULSORY 
        in every controller test file — omitting them makes the test INVALID.

        EXCEPTIONGROUP / TASKGROUP ERROR PREVENTION RULES
        - Always define the FastAPI app and dependency overrides **inside** the test_client fixture.
        - Ensure `app.dependency_overrides[get_db] = override_get_db` is set **before** creating the TestClient.
        - Never import or reuse the global FastAPI `app` from the project — always build a local app per test.
        - Do NOT use `@pytest.mark.asyncio` unless the controller route itself is `async`.
        - Always use `TestClient(app)` (sync client), not `AsyncClient`.
        - Ensure the mock_db_session fixture yields a fresh `MagicMock(spec=Session)` for each test.
        - Always `yield client` instead of `return client` in the fixture so that overrides remain active 
        during the request lifecycle.
        - Always clear overrides with `app.dependency_overrides.clear()` after yield.
        - These rules prevent `exceptiongroup.ExceptionGroup` or 
        `CustomException(status_code=500, message='Internal Server Error')` 
        caused by real DB connections being triggered in background TaskGroups.
    """)

    service_instructions = textwrap.dedent("""
        For services:
        - Create a MagicMock-based request fixture that includes all typical request.state attributes (user_name, user_id, email, role).
        - Use mock values where necessary to simulate realistic request context and validate service logic.
        - Always mock the SQLAlchemy session using MagicMock(spec=Session) to replicate full ORM behavior.
        - Ensure the mock session supports all common methods used in services: query, filter, filter_by, join, outerjoin, offset, limit, order_by, all, first, add, delete, commit, rollback, and refresh.
        - Each mocked method should return the same session instance to allow method chaining (e.g., session.query.return_value = session).
        - Set default return values like session.all.return_value = [] and session.first.return_value = None to prevent AttributeError in chained queries.
        - Validate both return values and method call counts (e.g., commit or rollback should be asserted explicitly).
        - Ensure all tests remain isolated and do not depend on a running API or database connection.
        - Include test cases for all logical branches, exception paths, and edge cases to achieve complete line coverage.
        - Write test cases for custom exceptions raised within service methods, ensuring they are handled and asserted properly.
        - Never instantiate ORM models in tests (avoids `_sa_instance_state` error).
    """)

    detected_schemas, possible_modules = extract_schemas_and_modules(file_content)
    schema_metadata_blocks = []

    if detected_schemas:
        for schema_name in detected_schemas:
            metadata = extract_schema_metadata_from_ast(schema_name, possible_modules, workdir=".")
            if not metadata:
                logging.info(f"Schema metadata not found for {schema_name}")
                continue

            block = f"Schema Metadata for {schema_name}:\n{metadata}"
            schema_metadata_blocks.append(block)

        if schema_metadata_blocks:
            schema_hint = textwrap.dedent(f"""
                The following are structured schema definitions extracted from the project.
                Use them to generate VALID JSON payloads that comply with each schema’s
                required fields, types, and validators.

                {os.linesep.join(schema_metadata_blocks)}

                Rules for Payloads:
                - Include all required fields.
                - Respect type constraints and defaults.
                - For optional fields, include realistic defaults or None.
                - Follow any validation logic listed in validators.
                - Keep the payload concise and realistic.
                - Strict Rule: Do NOT rename or modify any schema field names.
            """)
        else:
            schema_hint = "Schemas detected but no metadata could be extracted."

    else:
        schema_hint = "No explicit schemas detected — infer payloads logically from function parameters."

    if file_type.lower() in ("controller", "controllers"):
        fixture_instructions = controller_instructions
    elif file_type.lower() in ("service", "services"):
        fixture_instructions = service_instructions
    else:
        fixture_instructions = "Unknown file type — write logical pytest tests accordingly."

    prompt = textwrap.dedent(f"""
        You are an expert Python developer specialized in writing pytest test cases for FastAPI projects.

        Task:
        Generate complete pytest-based unit tests for the following FastAPI {file_type} file.

        File path: {filepath}
        {base_guidelines}
        {fixture_instructions}
        {schema_hint}
        File content:
        ```
        {file_content}
        ```
    """)

    return prompt.strip()

def run_agent(filepath: str, file_type: str,prefix: str,output_dir:str): 
    """Run AI agent to generate pytest test cases.""" 
    with open(filepath, "r") as f: 
        file_content = f.read() 

    prompt = build_prompt(filepath, file_type, file_content,prefix) 
    client = get_model_client() 
    generated_code = generate_response(client, prompt) 
    output_path = os.path.join(output_dir, f"test_{os.path.basename(filepath)}")
    with open(output_path, "w") as f:
        f.write(generated_code)
    logging.info(f"Test file generated at: {output_path}")

    