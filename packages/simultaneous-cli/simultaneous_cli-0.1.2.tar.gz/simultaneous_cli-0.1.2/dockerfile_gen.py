"""Dockerfile generation utilities."""

import json
from pathlib import Path
from typing import Optional

from cli.agent_spec import AgentSpec


def generate_dockerfile(agent_dir: Path, spec: Optional[AgentSpec] = None) -> str:
    """Generate a Dockerfile for an agent based on sim.yaml or auto-detection.
    
    Args:
        agent_dir: Directory containing agent code
        spec: Optional AgentSpec (if None, will try to load from sim.yaml)
        
    Returns:
        Dockerfile content as string
    """
    agent_dir = Path(agent_dir)
    
    # Try to load spec if not provided
    if spec is None:
        spec_path = agent_dir / "sim.yaml"
        if spec_path.exists():
            spec = AgentSpec.from_file(spec_path)
    
    # Detect language and entrypoint
    requirements_txt = agent_dir / "requirements.txt"
    package_json = agent_dir / "package.json"
    main_py = agent_dir / "main.py"
    main_js = agent_dir / "index.js"
    
    # Determine base image and setup
    if package_json.exists():
        # Node.js agent
        base_image = "node:20-slim"
        install_cmd = "RUN npm install"
        entrypoint_cmd = spec.entrypoint.command if spec else ["node", "index.js"]
    elif requirements_txt.exists() or main_py.exists():
        # Python agent
        base_image = "python:3.11-slim"
        install_cmd = ""
        if requirements_txt.exists():
            install_cmd = "COPY requirements.txt .\n    RUN pip install --no-cache-dir -r requirements.txt"
        entrypoint_cmd = spec.entrypoint.command if spec else ["python", "main.py"]
    else:
        # Default to Python
        base_image = "python:3.11-slim"
        install_cmd = ""
        entrypoint_cmd = spec.entrypoint.command if spec else ["python", "-m", "main"]
    
    # Get entrypoint command from spec or default
    if spec and spec.entrypoint:
        cmd_parts = spec.entrypoint.command + spec.entrypoint.args
    else:
        cmd_parts = entrypoint_cmd
    
    # Build Dockerfile
    dockerfile_lines = [
        f"FROM {base_image}",
        "",
        "WORKDIR /app",
        "",
    ]
    
    # Add install commands
    if install_cmd:
        if "\n" in install_cmd:
            # Multi-line install command
            for line in install_cmd.split("\n"):
                dockerfile_lines.append(line)
        else:
            dockerfile_lines.append(install_cmd)
        dockerfile_lines.append("")
    
    # Copy agent code
    dockerfile_lines.append("# Copy agent code")
    dockerfile_lines.append("COPY . .")
    dockerfile_lines.append("")
    
    # Set environment variables
    dockerfile_lines.append("# Environment variables")
    dockerfile_lines.append("ENV PYTHONUNBUFFERED=1")
    if spec and spec.secrets:
        dockerfile_lines.append(f"# Note: Secrets required: {', '.join(spec.secrets)}")
    dockerfile_lines.append("")
    
    # Set entrypoint - use exec form for CMD: CMD ["python", "main.py"]
    cmd_json = json.dumps(cmd_parts)
    dockerfile_lines.append("# Run agent")
    dockerfile_lines.append(f"CMD {cmd_json}")
    
    return "\n".join(dockerfile_lines)


def ensure_dockerfile(agent_dir: Path, spec: Optional[AgentSpec] = None) -> Path:
    """Ensure a Dockerfile exists in agent_dir, generating one if needed.
    
    Args:
        agent_dir: Directory containing agent code
        spec: Optional AgentSpec
        
    Returns:
        Path to Dockerfile (existing or newly created)
    """
    agent_dir = Path(agent_dir)
    dockerfile_path = agent_dir / "Dockerfile"
    
    if not dockerfile_path.exists():
        # Generate Dockerfile
        dockerfile_content = generate_dockerfile(agent_dir, spec)
        dockerfile_path.write_text(dockerfile_content, encoding='utf-8')
    
    return dockerfile_path

