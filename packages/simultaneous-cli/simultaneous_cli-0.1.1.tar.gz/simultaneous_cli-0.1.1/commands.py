"""CLI commands for orgs, projects, agents, marketplace, and deployment."""

import json
import uuid
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from cli.auth import get_current_token
from cli.api_client import APIClient, APIError

console = Console()

# Organization commands
org_app = typer.Typer(name="orgs", help="Organization management commands")


@org_app.command("create")
def create_org(name: str = typer.Argument(..., help="Organization name")) -> None:
    """Create a new organization."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            console.print(f"[yellow]Creating organization: {name}[/yellow]")
            org = api.create_org(name)
            console.print("[green]✓ Organization created successfully![/green]")
            console.print(f"[dim]ID: {org.get('id', 'N/A')}[/dim]")
            console.print(f"[dim]Name: {org.get('name', 'N/A')}[/dim]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@org_app.command("list")
def list_orgs() -> None:
    """List all organizations."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            orgs = api.list_orgs()
            
            if not orgs:
                console.print("[yellow]No organizations found[/yellow]")
                return
            
            table = Table(title="Organizations")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Created", style="dim")
            
            for org in orgs:
                table.add_row(
                    str(org.get("id", "N/A")),
                    org.get("name", "N/A"),
                    org.get("created_at", "N/A"),
                )
            
            console.print(table)
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


# Project commands
project_app = typer.Typer(name="projects", help="Project management commands")


@project_app.command("create")
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    slug: str = typer.Option(None, "--slug", "-s", help="Project slug (auto-generated if not provided)"),
) -> None:
    """Create a new project."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            console.print(f"[yellow]Creating project: {name}[/yellow]")
            project = api.create_project(name, slug)
            console.print("[green]✓ Project created successfully![/green]")
            console.print(f"[dim]ID: {project.get('id', 'N/A')}[/dim]")
            console.print(f"[dim]Name: {project.get('name', 'N/A')}[/dim]")
            console.print(f"[dim]Slug: {project.get('slug', 'N/A')}[/dim]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@project_app.command("list")
def list_projects(
    archived: bool = typer.Option(False, "--archived", help="Include archived projects"),
) -> None:
    """List all projects."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            projects = api.list_projects(archived=archived)
            
            if not projects:
                console.print("[yellow]No projects found[/yellow]")
                return
            
            table = Table(title="Projects")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Slug", style="dim")
            table.add_column("Archived", style="yellow")
            table.add_column("Created", style="dim")
            
            for project in projects:
                table.add_row(
                    str(project.get("id", "N/A")),
                    project.get("name", "N/A"),
                    project.get("slug", "N/A"),
                    "Yes" if project.get("archived", False) else "No",
                    project.get("created_at", "N/A"),
                )
            
            console.print(table)
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@project_app.command("get")
def get_project(project_id: str = typer.Argument(..., help="Project ID")) -> None:
    """Get a project by ID."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            project = api.get_project(project_id)
            console.print(f"[bold]Project:[/bold] {project.get('name', 'N/A')}")
            console.print(f"  ID: [dim]{project.get('id', 'N/A')}[/dim]")
            console.print(f"  Slug: [dim]{project.get('slug', 'N/A')}[/dim]")
            console.print(f"  Archived: [dim]{'Yes' if project.get('archived', False) else 'No'}[/dim]")
            console.print(f"  Created: [dim]{project.get('created_at', 'N/A')}[/dim]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@project_app.command("delete")
def delete_project(project_id: str = typer.Argument(..., help="Project ID")) -> None:
    """Delete a project."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            console.print(f"[yellow]Deleting project: {project_id}[/yellow]")
            api.delete_project(project_id)
            console.print("[green]✓ Project deleted successfully![/green]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


# Agent commands
agent_app = typer.Typer(name="agents", help="Agent management commands")


@agent_app.command("create")
def create_agent(
    project_id: str = typer.Option(None, "--project-id", help="Project ID (optional, will prompt if not provided)"),
    name: str = typer.Option(None, "--name", "-n", help="Agent name"),
    script: str = typer.Option(None, "--script", "-s", help="Agent script"),
    script_file: Path = typer.Option(None, "--script-file", "-f", help="Path to agent script file"),
    provider_project_id: str = typer.Option(None, "--provider-project-id", help="Browserbase project ID (optional, defaults to API secret)"),
    description: str = typer.Option(None, "--description", "-d", help="Agent description"),
    env_vars: str = typer.Option(None, "--env-vars", "-e", help="Environment variables as JSON"),
    context_id: str = typer.Option(None, "--context-id", "-c", help="Context ID"),
    extension_id: str = typer.Option(None, "--extension-id", "-x", help="Extension ID"),
    region: str = typer.Option(None, "--region", "-r", help="Region"),
    timeout_sec: int = typer.Option(None, "--timeout-sec", "-t", help="Timeout in seconds"),
) -> None:
    """Create a new agent interactively."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            # Interactive project selection if not provided
            if not project_id:
                console.print("[yellow]Loading projects...[/yellow]")
                try:
                    projects = api.list_projects()
                    if not projects:
                        console.print("[red]✗ No projects found. Create a project first with 'sim projects create'[/red]")
                        raise typer.Exit(1)
                    
                    # Display projects in a table
                    table = Table(title="Select a Project")
                    table.add_column("Index", style="cyan", width=8)
                    table.add_column("Name", style="magenta")
                    table.add_column("ID", style="dim")
                    table.add_column("Slug", style="dim")
                    
                    for idx, project in enumerate(projects, 1):
                        table.add_row(
                            str(idx),
                            project.get("name", "N/A"),
                            str(project.get("id", "N/A")),
                            project.get("slug", "N/A"),
                        )
                    
                    console.print(table)
                    console.print()
                    
                    # Get user selection
                    while True:
                        choice = Prompt.ask(
                            f"Select project (1-{len(projects)})",
                            default="1",
                        )
                        try:
                            idx = int(choice) - 1
                            if 0 <= idx < len(projects):
                                project_id = str(projects[idx]["id"])
                                console.print(f"[green]✓ Selected: {projects[idx].get('name', 'N/A')}[/green]")
                                break
                            else:
                                console.print(f"[red]✗ Invalid selection. Please choose 1-{len(projects)}[/red]")
                        except ValueError:
                            console.print("[red]✗ Please enter a number[/red]")
                            
                except APIError as e:
                    console.print(f"[red]✗ Failed to load projects: {e.message}[/red]")
                    raise typer.Exit(1)
                except Exception as e:
                    console.print(f"[red]✗ Error loading projects: {str(e)}[/red]")
                    raise typer.Exit(1)
            
            # Interactive name prompt if not provided
            if not name:
                name = Prompt.ask("Agent name")
            
            # Interactive script file selection if not provided
            if not script_file and not script:
                script_file_path = Prompt.ask("Path to agent script file", default="main.py")
                script_file = Path(script_file_path)
            
            # Read script from file if provided
            if script_file:
                if not script_file.exists():
                    console.print(f"[red]✗ Script file not found: {script_file}[/red]")
                    raise typer.Exit(1)
                script = script_file.read_text()
            elif not script:
                console.print("[red]✗ Either --script or --script-file must be provided[/red]")
                raise typer.Exit(1)
            
            # Provider project ID is optional - API will use default from secrets if not provided
            # Parse env vars
            env_vars_dict = None
            if env_vars:
                try:
                    env_vars_dict = json.loads(env_vars)
                except json.JSONDecodeError:
                    console.print("[red]✗ Invalid JSON in env-vars[/red]")
                    raise typer.Exit(1)
            
            console.print(f"[yellow]Creating agent: {name}[/yellow]")
            agent = api.create_agent(
                project_id=project_id,
                name=name,
                script=script,
                provider_project_id=provider_project_id,
                description=description,
                env_vars=env_vars_dict,
                context_id=context_id,
                extension_id=extension_id,
                region=region,
                timeout_sec=timeout_sec,
            )
            console.print("[green]✓ Agent created successfully![/green]")
            console.print(f"[dim]ID: {agent.get('id', 'N/A')}[/dim]")
            console.print(f"[dim]Name: {agent.get('name', 'N/A')}[/dim]")
            
            # Save to sim.yaml
            try:
                from cli.agent_spec import AgentSpec, RuntimeSpec, EntrypointSpec
                
                # Determine entrypoint from script_file or default
                if script_file:
                    entrypoint_cmd = ["python", str(script_file.name)]
                    agent_dir = script_file.parent
                else:
                    entrypoint_cmd = ["python", "main.py"]
                    agent_dir = Path(".")
                
                # Create AgentSpec
                spec = AgentSpec(
                    name=agent["name"],
                    version="1.0.0",
                    description=agent.get("description", ""),
                    runtime=RuntimeSpec(
                        type="browser",
                        provider="browserbase",
                        region=agent.get("region", "auto"),
                    ),
                    entrypoint=EntrypointSpec(
                        command=entrypoint_cmd,
                    ),
                    timeouts={"execution": agent.get("timeoutSec", 600)},
                    secrets=list(env_vars_dict.keys()) if env_vars_dict else [],
                )
                
                # Prepare metadata for API tracking
                metadata = {
                    "agent_id": str(agent["id"]),
                    "project_id": project_id,
                    "provider_project_id": agent.get("providerProjectId"),
                    "context_id": agent.get("contextId"),
                    "extension_id": agent.get("extensionId"),
                    "region": agent.get("region"),
                    "timeout_sec": agent.get("timeoutSec"),
                    "env_vars": agent.get("envVars", {}),
                }
                
                # Save to sim.yaml
                sim_yaml_path = agent_dir / "sim.yaml"
                spec.to_file(sim_yaml_path, metadata=metadata)
                console.print(f"[green]✓ Saved agent config to: {sim_yaml_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not save sim.yaml: {str(e)}[/yellow]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@agent_app.command("list")
def list_agents(
    project_id: str = typer.Argument(..., help="Project ID"),
    active_only: bool = typer.Option(False, "--active-only", help="Show only active agents"),
) -> None:
    """List agents for a project."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            agents = api.list_agents(project_id, active_only=active_only)
            
            if not agents:
                console.print("[yellow]No agents found[/yellow]")
                return
            
            table = Table(title=f"Agents (Project: {project_id})")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="dim")
            table.add_column("Active", style="yellow")
            table.add_column("Created", style="dim")
            
            for agent in agents:
                table.add_row(
                    str(agent.get("id", "N/A")),
                    agent.get("name", "N/A"),
                    agent.get("description", "N/A") or "",
                    "Yes" if agent.get("active", False) else "No",
                    agent.get("createdAt", "N/A"),
                )
            
            console.print(table)
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@agent_app.command("get")
def get_agent(
    project_id: str = typer.Argument(..., help="Project ID"),
    agent_id: str = typer.Argument(..., help="Agent ID"),
) -> None:
    """Get an agent by ID."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            agent = api.get_agent(project_id, agent_id)
            console.print(f"[bold]Agent:[/bold] {agent.get('name', 'N/A')}")
            console.print(f"  ID: [dim]{agent.get('id', 'N/A')}[/dim]")
            console.print(f"  Description: [dim]{agent.get('description', 'N/A') or 'None'}[/dim]")
            console.print(f"  Active: [dim]{'Yes' if agent.get('active', False) else 'No'}[/dim]")
            console.print(f"  Provider Project ID: [dim]{agent.get('providerProjectId', 'N/A')}[/dim]")
            console.print(f"  Created: [dim]{agent.get('createdAt', 'N/A')}[/dim]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@agent_app.command("delete")
def delete_agent(
    project_id: str = typer.Argument(..., help="Project ID"),
    agent_id: str = typer.Argument(..., help="Agent ID"),
) -> None:
    """Delete an agent."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)


@agent_app.command("deploy")
def agents_deploy(
    project_id: str = typer.Option(None, "--project-id", "-p", help="Project ID (optional if sim.yaml exists)"),
    agent_id: str = typer.Option(None, "--agent-id", "-a", help="Agent ID (optional if sim.yaml exists)"),
    agent_dir: Path = typer.Option(".", "--agent-dir", "-d", help="Path to agent code (contains sim.yaml)"),
    image: str = typer.Option(None, "--image", "-i", help="Target image (e.g. ghcr.io/org/agent:tag)"),
    registry: str = typer.Option("ghcr", "--registry", help="ghcr|ecr|dockerhub"),
    build: bool = typer.Option(False, "--build", help="Build image on API from uploaded directory"),
    push: bool = typer.Option(False, "--push", help="Push image to registry after build (server side)"),
) -> None:
    """Register or build-and-register an agent container image with the API.
    
    Reads sim.yaml from agent_dir to get project_id/agent_id if not provided.
    Auto-generates Dockerfile if it doesn't exist.
    """
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)

    try:
        agent_dir = Path(agent_dir).resolve()
        sim_yaml_path = agent_dir / "sim.yaml"
        
        # Try to load sim.yaml for metadata
        spec = None
        metadata = {}
        if sim_yaml_path.exists():
            try:
                from cli.agent_spec import AgentSpec
                spec = AgentSpec.from_file(sim_yaml_path)
                
                # Load metadata from sim.yaml
                import yaml
                with open(sim_yaml_path, "r") as f:
                    yaml_data = yaml.safe_load(f)
                    metadata = yaml_data.get("metadata", {})
                    
                # Use metadata for IDs if not provided
                if not project_id and metadata.get("project_id"):
                    project_id = metadata["project_id"]
                if not agent_id and metadata.get("agent_id"):
                    agent_id = metadata["agent_id"]
                    
                # Use spec name for image tag if image not provided
                if not image:
                    # Generate image name from agent name
                    agent_name = spec.name.lower().replace(" ", "-").replace("_", "-")
                    # Try to get username from GHCR_USERNAME env or use a default
                    import os
                    ghcr_username = os.getenv("GHCR_USERNAME", "your-username")
                    image = f"ghcr.io/{ghcr_username}/{agent_name}:latest"
                    
                console.print(f"[dim]Loaded config from: {sim_yaml_path}[/dim]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not load sim.yaml: {e}[/yellow]")
        
        if not project_id:
            console.print("[red]✗ Project ID required. Provide --project-id or ensure sim.yaml has metadata.project_id[/red]")
            raise typer.Exit(1)
        if not agent_id:
            console.print("[red]✗ Agent ID required. Provide --agent-id or ensure sim.yaml has metadata.agent_id[/red]")
            raise typer.Exit(1)
        if not image:
            console.print("[red]✗ Image required. Provide --image or ensure sim.yaml is loaded[/red]")
            raise typer.Exit(1)
        
        # Ensure Dockerfile exists (auto-generate if needed)
        dockerfile_path = agent_dir / "Dockerfile"
        if not dockerfile_path.exists():
            try:
                from cli.dockerfile_gen import ensure_dockerfile
                console.print(f"[yellow]Generating Dockerfile for agent...[/yellow]")
                ensure_dockerfile(agent_dir, spec)
                console.print(f"[green]✓ Generated Dockerfile: {dockerfile_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not auto-generate Dockerfile: {e}[/yellow]")
                console.print("[yellow]⚠ You may need to create Dockerfile manually[/yellow]")
        
        with APIClient() as api:
            console.print(f"[yellow]Deploying agent container: {agent_id} → {image}[/yellow]")
            result = api.deploy_agent(
                project_id=project_id,
                agent_id=agent_id,
                container_image=image,
                container_registry=registry,
                build_image=build,
                push_image=push,
                agent_dir_path=agent_dir if build else None,
            )
            console.print("[green]✓ Agent deployment registered![/green]")
            console.print(f"[dim]Image: {result.get('container_image', image)}[/dim]")
            
            # Update sim.yaml with container image if deployed successfully
            if sim_yaml_path.exists() and spec:
                try:
                    import yaml
                    with open(sim_yaml_path, "r") as f:
                        yaml_data = yaml.safe_load(f)
                    if "metadata" not in yaml_data:
                        yaml_data["metadata"] = {}
                    yaml_data["metadata"]["container_image"] = result.get("container_image", image)
                    yaml_data["metadata"]["container_registry"] = registry
                    yaml_data["metadata"]["deployed_at"] = result.get("deployed_at")
                    with open(sim_yaml_path, "w") as f:
                        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
                    console.print(f"[dim]Updated sim.yaml with deployment info[/dim]")
                except Exception as e:
                    console.print(f"[yellow]⚠ Could not update sim.yaml: {e}[/yellow]")
                    
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@agent_app.command("run")
def agents_run(
    project_id: str = typer.Option(None, "--project-id", "-p", help="Project ID (optional if sim.yaml exists)"),
    agent_id: str = typer.Option(None, "--agent-id", "-a", help="Agent ID (optional if sim.yaml exists)"),
    agent_dir: Path = typer.Option(".", "--agent-dir", "-d", help="Path to agent directory (contains sim.yaml)"),
    params: str = typer.Option(None, "--params", "-p", help="JSON parameters for the agent"),
    env_vars: str = typer.Option(None, "--env", help="JSON map of extra env vars"),
    timeout_sec: int = typer.Option(None, "--timeout-sec", help="Timeout seconds"),
) -> None:
    """Run a deployed agent container once via API (Modal under the hood).
    
    Reads sim.yaml from agent_dir to get project_id/agent_id if not provided.
    """
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)

    try:
        agent_dir = Path(agent_dir).resolve()
        sim_yaml_path = agent_dir / "sim.yaml"
        
        # Try to load sim.yaml for metadata
        if sim_yaml_path.exists():
            try:
                import yaml
                with open(sim_yaml_path, "r") as f:
                    yaml_data = yaml.safe_load(f)
                    metadata = yaml_data.get("metadata", {})
                    
                # Use metadata for IDs if not provided
                if not project_id and metadata.get("project_id"):
                    project_id = metadata["project_id"]
                if not agent_id and metadata.get("agent_id"):
                    agent_id = metadata["agent_id"]
                if timeout_sec is None and metadata.get("timeout_sec"):
                    timeout_sec = metadata["timeout_sec"]
                    
                console.print(f"[dim]Loaded config from: {sim_yaml_path}[/dim]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not load sim.yaml: {e}[/yellow]")
        
        if not project_id:
            console.print("[red]✗ Project ID required. Provide --project-id or ensure sim.yaml has metadata.project_id[/red]")
            raise typer.Exit(1)
        if not agent_id:
            console.print("[red]✗ Agent ID required. Provide --agent-id or ensure sim.yaml has metadata.agent_id[/red]")
            raise typer.Exit(1)
        
        params_dict = {}
        env_dict = {}
        if params:
            try:
                params_dict = json.loads(params)
            except json.JSONDecodeError:
                console.print("[red]✗ Invalid JSON in --params[/red]")
                raise typer.Exit(1)
        if env_vars:
            try:
                env_dict = json.loads(env_vars)
            except json.JSONDecodeError:
                console.print("[red]✗ Invalid JSON in --env[/red]")
                raise typer.Exit(1)

        with APIClient() as api:
            console.print(f"[yellow]Running agent container: {agent_id}[/yellow]")
            res = api.run_agent_container(
                project_id=project_id,
                agent_id=agent_id,
                params=params_dict,
                env_vars=env_dict,
                timeout_sec=timeout_sec or 600,
            )
            console.print("[green]✓ Run started![/green]")
            console.print(f"[dim]Run ID: {res.get('run_id', 'N/A')} | Modal: {res.get('modal_run_id', 'N/A')}[/dim]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


# Marketplace commands
marketplace_app = typer.Typer(name="marketplace", help="Marketplace commands")


@marketplace_app.command("publish")
def publish_agent(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    project_id: str = typer.Option(None, "--project-id", "-p", help="Project ID (if not provided, will be inferred)"),
    public: bool = typer.Option(True, "--public/--private", help="Make agent public or private"),
) -> None:
    """Publish an agent to the marketplace."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            console.print(f"[yellow]Publishing agent: {agent_id}[/yellow]")
            # Note: project_id may not be needed if agent_id is globally unique
            result = api.publish_agent(project_id or "", agent_id, public=public)
            console.print("[green]✓ Agent published successfully![/green]")
            console.print(f"[dim]Published: {result.get('published', 'N/A')}[/dim]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@marketplace_app.command("list")
def list_marketplace_agents() -> None:
    """List agents in the marketplace."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            agents = api.list_marketplace_agents()
            
            if not agents:
                console.print("[yellow]No agents found in marketplace[/yellow]")
                return
            
            table = Table(title="Marketplace Agents")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="dim")
            table.add_column("Author", style="yellow")
            
            for agent in agents:
                table.add_row(
                    str(agent.get("id", "N/A")),
                    agent.get("name", "N/A"),
                    agent.get("description", "N/A") or "",
                    agent.get("author", "N/A"),
                )
            
            console.print(table)
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@marketplace_app.command("deploy")
def deploy_from_marketplace(
    agent_id: str = typer.Argument(..., help="Marketplace agent ID"),
    project_id: str = typer.Argument(..., help="Target project ID"),
) -> None:
    """Deploy an agent from the marketplace to a project."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            console.print(f"[yellow]Deploying agent from marketplace: {agent_id}[/yellow]")
            result = api.deploy_from_marketplace(agent_id, project_id)
            console.print("[green]✓ Agent deployed successfully![/green]")
            console.print(f"[dim]Agent ID: {result.get('agent_id', 'N/A')}[/dim]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


# Deploy commands
deploy_app = typer.Typer(name="deploy", help="Deployment commands")


@deploy_app.command("agent")
def deploy_agent_to_cloud(
    project_id: str = typer.Argument(..., help="Project ID"),
    agent_id: str = typer.Argument(..., help="Agent ID"),
) -> None:
    """Deploy an agent to the cloud (Modal).
    
    Note: This is a placeholder for future Modal integration.
    """
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            console.print(f"[yellow]Deploying agent to cloud: {agent_id}[/yellow]")
            console.print("[dim]Note: Modal integration coming soon[/dim]")
            result = api.deploy_agent_to_cloud(project_id, agent_id)
            console.print("[green]✓ Agent deployment initiated![/green]")
            console.print(f"[dim]Deployment ID: {result.get('deployment_id', 'N/A')}[/dim]")
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)

