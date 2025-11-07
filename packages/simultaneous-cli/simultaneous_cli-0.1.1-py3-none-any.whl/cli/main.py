"""CLI entry point for Simultaneous."""

import json

import typer
from rich.console import Console

from cli.auth import auth_app, get_current_token
from cli.api_client import APIClient, APIError
from cli.commands import (
    org_app,
    project_app,
    agent_app,
    marketplace_app,
    deploy_app,
)

app = typer.Typer(
    name="sim",
    help="Simultaneous CLI - Run agents across multiple providers",
    add_completion=False,
)
console = Console()

# Add subcommands
app.add_typer(auth_app)
app.add_typer(org_app)
app.add_typer(project_app)
app.add_typer(agent_app)
app.add_typer(marketplace_app)
app.add_typer(deploy_app)


@app.command()
def run(
    agent_name: str = typer.Argument(..., help="Name of the agent to run"),
    project_id: str = typer.Option(None, "--project-id", "-p", help="Project ID"),
    agent_id: str = typer.Option(None, "--agent-id", "-a", help="Agent ID"),
    params: str = typer.Option(None, "--params", "-d", help="JSON parameters for the agent"),
    parallel: int = typer.Option(1, "--parallel", "-n", help="Number of parallel shards"),
) -> None:
    """Run an agent."""
    if not get_current_token():
        console.print("[red]✗ Not authenticated. Use 'sim auth signin' to sign in.[/red]")
        raise typer.Exit(1)
    
    try:
        with APIClient() as api:
            # If agent_id not provided, try to find agent by name
            if not agent_id and agent_name:
                if not project_id:
                    console.print("[red]✗ Project ID required when agent ID not provided[/red]")
                    raise typer.Exit(1)
                
                # List agents and find by name
                agents = api.list_agents(project_id)
                matching = [a for a in agents if a.get("name") == agent_name]
                if not matching:
                    console.print(f"[red]✗ Agent '{agent_name}' not found in project[/red]")
                    raise typer.Exit(1)
                agent_id = str(matching[0]["id"])
            
            if not agent_id or not project_id:
                console.print("[red]✗ Both project_id and agent_id are required[/red]")
                raise typer.Exit(1)
            
            # Parse params
            params_dict = {}
            if params:
                try:
                    params_dict = json.loads(params)
                except json.JSONDecodeError:
                    console.print("[red]✗ Invalid JSON in params[/red]")
                    raise typer.Exit(1)
            
            console.print(f"[green]Running agent: {agent_name or agent_id}[/green]")
            result = api.run_agent(project_id, agent_id, params_dict)
            
            console.print("[green]✓ Agent started successfully![/green]")
            console.print(f"[dim]Run ID: {result.get('run_id', 'N/A')}[/dim]")
            
    except APIError as e:
        console.print(f"[red]✗ API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def runs(
    command: str = typer.Argument(..., help="Command: list, get, cancel"),
    run_id: str = typer.Argument(None, help="Run ID (for get/cancel)"),
) -> None:
    """Manage runs."""
    if command == "list":
        console.print("[green]Listing runs...[/green]")
        # TODO: Implement run listing
    elif command == "get" and run_id:
        console.print(f"[green]Getting run: {run_id}[/green]")
        # TODO: Implement run retrieval
    elif command == "cancel" and run_id:
        console.print(f"[green]Cancelling run: {run_id}[/green]")
        # TODO: Implement run cancellation
    else:
        console.print("[red]Invalid command or missing run_id[/red]")
        raise typer.Exit(1)


@app.command()
def logs(
    command: str = typer.Argument(..., help="Command: stream, get"),
    run_id: str = typer.Argument(..., help="Run ID"),
) -> None:
    """Manage logs."""
    if command == "stream":
        console.print(f"[green]Streaming logs for run: {run_id}[/green]")
        # TODO: Implement log streaming
    elif command == "get":
        console.print(f"[green]Getting logs for run: {run_id}[/green]")
        # TODO: Implement log retrieval
    else:
        console.print("[red]Invalid command. Use 'stream' or 'get'[/red]")
        raise typer.Exit(1)


@app.command()
def workflow(
    command: str = typer.Argument(..., help="Command: create, run, list"),
    name: str = typer.Argument(None, help="Workflow name"),
) -> None:
    """Manage workflows."""
    if command == "create" and name:
        console.print(f"[green]Creating workflow: {name}[/green]")
        # TODO: Implement workflow creation
    elif command == "run" and name:
        console.print(f"[green]Running workflow: {name}[/green]")
        # TODO: Implement workflow execution
    elif command == "list":
        console.print("[green]Listing workflows...[/green]")
        # TODO: Implement workflow listing
    else:
        console.print("[red]Invalid command or missing name[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

