import os
import logging
from .utilities import detect_file_type, detect_controller_prefix,prompt_for_api_key
from .agent_services import run_agent
from . import config 

logging.basicConfig(level=logging.INFO, format="%(message)s")

def agent_ai():
    """
    CLI tool to generate tests for FastAPI controllers or services.
    - Takes a file path input from the user.
    - Detects whether the file is a controller or service.
    - Extracts router prefix for controllers.
    - Runs the AI test generator (`run_agent`) with correct context.
    """
    provider, api_key = prompt_for_api_key()
    if not provider:
        logging.error("Provider setup failed. Exiting.")
        return

    filepath = input("Enter the file path (controller/service): ").strip()
    filepath = os.path.abspath(filepath)

    if not os.path.exists(filepath):
        logging.error("Error: File not found. Please check the path and try again.")
        return
    
    output_dir = input("Enter output directory : ").strip()
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    file_type = detect_file_type(filepath)
    prefix = ""
    if file_type == "controller":
        api_file = input("Enter router file path (where all routes are there): ").strip()
        api_file = os.path.abspath(api_file)

        if not os.path.exists(api_file):
            logging.warning(f"Router file not found at {api_file}, skipping prefix detection.")
        else:
            prefix = detect_controller_prefix(filepath, api_file)
            logging.info(f" Detected prefix: {prefix}")

    if file_type in ["controller", "service"]:
        logging.info("Running agent...")
        run_agent(filepath, file_type, prefix , output_dir)
        logging.info("Agent finished successfully.")
    else:
        logging.warning("Unknown file type. Please ensure it's in controllers or services.")

if __name__ == "__main__":
    agent_ai()
