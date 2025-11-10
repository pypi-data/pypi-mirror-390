"""
Run command for Laddr CLI.

Manages Docker environment and job execution.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time
from typing import Any

import click

from ..utils import (
        ProjectNotFoundError,
        check_docker,
        check_docker_compose,
        compose_up,
        console,
        print_header,
        print_info,
        print_panel,
        print_success,
        validate_project_directory,
        wait_for_service,
)


@click.group()
@click.pass_context
def run(ctx: click.Context):
        """Run environments, agents, or pipelines.

        Usage:
            laddr run dev [--build] [--no-detach]
            laddr run agent <agent_name> [--inputs '{...}']
            laddr run pipeline <file.yml>
        """


@run.command("dev")
@click.option("--build", is_flag=True, help="Force rebuild images")
@click.option("--detach", "-d", is_flag=True, help="Run in detached mode (background)")
def run_dev(build: bool, detach: bool):
    """Run the Laddr development environment.
    
    Starts all infrastructure services and agent workers:
    - PostgreSQL (internal observability database)
    - Redis (message bus)
    - API server
    - Agent workers
    - Dashboard
    
    By default, shows live logs (like docker compose up).
    Use --detach/-d to run in background.
    
    Examples:
        laddr run dev              # Show logs
        laddr run dev --build      # Rebuild and show logs
        laddr run dev --detach     # Run in background
    """
    # Ensure we're in a project
    if not validate_project_directory(Path.cwd()):
        raise ProjectNotFoundError()

    # Check Docker availability
    check_docker()
    check_docker_compose()

    print_header("Starting Laddr Development Environment (This may take a few minutes)")

    # Build command for docker compose up
    cmd = ["docker", "compose", "up"]
    if build:
        cmd.append("--build")
    
    # In detached mode, start services in background first
    if detach:
        cmd.append("-d")
    
    # Start services and show logs
    try:
        if not detach:
            # Non-detached mode: stream logs live (Ctrl+C to stop)
            print_info("Starting services and streaming logs (Ctrl+C to stop)...")
            subprocess.run(cmd, check=False)
        else:
            # Detached mode: start in background, then show all logs
            print_info("Starting services in detached mode...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                print_info(f"Error starting services: {result.stderr}")
                raise click.ClickException("Failed to start services")
            
            # Wait a moment for services to initialize
            print_info("Waiting for services to initialize...")
            time.sleep(3)
            
            # Show all logs from all services
            print_info("Showing service logs...\n")
            subprocess.run(["docker", "compose", "logs"], check=False)
            
            # Wait for critical services to be ready
            print_info("\nWaiting for services to be ready...")
            critical_services = ["postgres", "redis", "api"]
            for service in critical_services:
                wait_for_service(service, timeout=30)
            
            print_success("\nLaddr is running!")
            _print_service_info()
            _print_management_commands()
    
    except KeyboardInterrupt:
        if not detach:
            print_info("\nStopping services...")
            subprocess.run(["docker", "compose", "down"], check=False)


@run.command("pipeline")
@click.argument("pipeline_file")
def run_pipeline(pipeline_file: str):
    """Run a pipeline defined in a YAML file."""
    # Lazy import to avoid hard deps when not running pipeline
    import yaml  # type: ignore

    if not validate_project_directory(Path.cwd()):
        raise ProjectNotFoundError()

    with open(pipeline_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    stages = data.get("pipeline") or data.get("stages") or data.get("tasks")
    if not isinstance(stages, list):
        raise click.BadParameter("Pipeline YAML must define a list under 'pipeline' or 'stages'")

    # Use Laddr runtime (shared env for all agents)
    import asyncio

    from laddr.core import AgentRunner, LaddrConfig  # type: ignore

    print_header("Running Pipeline")

    results: dict[str, Any] = {}
    runner = AgentRunner(env_config=LaddrConfig())
    for stage in stages:
        agent_name = stage.get("agent")
        # Support both {inputs: {...}} and arbitrary keys; if tasks format, pass remaining keys except 'agent'
        inputs = stage.get("inputs", {k: v for k, v in stage.items() if k != "agent"})
        if not agent_name:
            raise click.BadParameter("Each stage must include 'agent'")
        console.print(f"  [dim]→[/dim] Running stage: [cyan]{agent_name}[/cyan]")
        res = asyncio.run(runner.run(inputs, agent_name=agent_name))
        results[agent_name] = res

    print_success("Pipeline complete")
    console.print("\n[bold cyan]Results[/bold cyan]")
    console.print(json.dumps(results, indent=2, ensure_ascii=False))
    console.print()


@run.command("agent")
@click.argument("agent_name")
@click.option("--inputs", "inputs_json", default="{}", help="JSON dict of inputs for the agent")
def run_agent_cmd(agent_name: str, inputs_json: str):
    """Run a single agent locally using AgentRunner."""
    import asyncio
    import os
    import sys

    # Ensure local project imports work (agents package)
    try:
        cwd = str(Path.cwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
    except Exception:
        pass

    # Favor local-friendly defaults to avoid external deps
    try:
        if not os.environ.get("DATABASE_URL"):
            os.environ["DATABASE_URL"] = "sqlite:///laddr.db"
        if not os.environ.get("QUEUE_BACKEND") and not os.environ.get("REDIS_URL"):
            os.environ["QUEUE_BACKEND"] = "memory"
    except Exception:
        pass

    if not validate_project_directory(Path.cwd()):
        raise ProjectNotFoundError()

    try:
        inputs = json.loads(inputs_json) if inputs_json else {}
    except json.JSONDecodeError:
        raise click.BadParameter("--inputs must be a valid JSON object")

    # Use new runtime
    try:
        from laddr.core import LaddrConfig, run_agent

        print_header(f"Running Agent → {agent_name}")

        # Load environment config
        config = LaddrConfig()

        # Run agent
        result = asyncio.run(run_agent(agent_name, inputs, config))

        # Print result
        print_success(f"Job completed: {result['job_id']}")
        console.print("\n[bold cyan]Result[/bold cyan]")
        console.print(json.dumps(result, indent=2, ensure_ascii=False))
        console.print()

    except Exception as e:
        print_info(f"Error: {e}")
        raise click.ClickException(str(e))


@run.command("replay")
@click.argument("job_id")
@click.option("--reexecute", is_flag=True, help="Re-execute the job instead of returning stored result")
def replay_job(job_id: str, reexecute: bool):
    """Replay a previous job by job ID.
    
    Examples:
        laddr run replay abc123-456-def
        laddr run replay abc123-456-def --reexecute
    """
    if not validate_project_directory(Path.cwd()):
        raise ProjectNotFoundError()

    try:
        from laddr.core import AgentRunner, LaddrConfig

        print_header(f"Replaying Job → {job_id}")

        # Load environment config
        config = LaddrConfig()
        runner = AgentRunner(env_config=config)

        # Replay
        result = runner.replay(job_id, reexecute=reexecute)

        # Print result
        print_success("Job replay complete")
        console.print("\n[bold cyan]Result[/bold cyan]")
        console.print(json.dumps(result, indent=2, ensure_ascii=False))
        console.print()

    except Exception as e:
        print_info(f"Error: {e}")
        raise click.ClickException(str(e))


def _print_service_info() -> None:
    """Print service URLs in minimalistic style."""
    console.print("\n[bold cyan]Services[/bold cyan]")
    console.print("  [dim]Dashboard[/dim]  http://localhost:5173")
    console.print("  [dim]API[/dim]        http://localhost:8000")
    console.print("  [dim]API Docs[/dim]   http://localhost:8000/docs")
    console.print("  [dim]Postgres[/dim]   localhost:5432")
    console.print("  [dim]Redis[/dim]      localhost:6379")


def _print_management_commands() -> None:
    """Print management command help in minimalistic style."""
    console.print("\n[bold cyan]Commands[/bold cyan]")
    console.print("  [cyan]laddr logs <agent>[/cyan]      View agent logs")
    console.print("  [cyan]laddr ps[/cyan]                Show container status")
    console.print("  [cyan]laddr scale <agent> <N>[/cyan] Scale agent workers")
    console.print("  [cyan]laddr stop[/cyan]              Stop all services")
    console.print()


# Alias for backward compatibility
@click.command(name="run-dev", hidden=True)
def run_dev_alias():
    """Alias for 'laddr run dev'."""
    from click import Context

    ctx = Context(run_dev)
    ctx.invoke(run_dev)
