# bambot/project.py
import os
import pkg_resources
from .utils import generate_app_name, echo_info, echo_success, echo_warning

TEMPLATE_FILES = [
    "agent_template.py", "Dockerfile", "agent_runner.py", "requirements.txt", "server.py"
]

def init_project(container_name=None, agent_type="langchain"):
    """Initialize a new Bam project"""
    if not container_name:
        container_name = generate_app_name()

    project_dir = os.path.join(os.getcwd(), container_name)
    if os.path.exists(project_dir):
        echo_warning(f"Directory '{container_name}' already exists. Skipping project initialization.")
        return

    echo_info(f"Initializing project '{container_name}'...")

    # Create project directory
    os.makedirs(project_dir, exist_ok=True)

    # Copy template files to the project directory
    templates_dir = pkg_resources.resource_filename(__name__, 'templates')
    for filename in TEMPLATE_FILES:
        template_path = os.path.join(templates_dir, filename)
        with open(template_path, "r") as f:
            template = f.read()
        if filename == "agent_runner.py":
            template = template.replace("{{AGENT_TYPE}}", agent_type)
        file_path = os.path.join(project_dir, filename.replace("agent_template.py", f"{agent_type}_agent.py"))
        with open(file_path, "w") as f:
            f.write(template)

    # Create .env file
    env_file_path = os.path.join(project_dir, ".env")
    with open(env_file_path, "w") as f:
        f.write("OPENAI_API_KEY=your_openai_api_key\n")

    echo_success(f"Project '{container_name}' initialized successfully!")