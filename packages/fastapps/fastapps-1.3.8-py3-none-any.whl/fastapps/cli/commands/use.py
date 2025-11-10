"""Use command - Add integrations to FastApps projects."""

from pathlib import Path

from rich.console import Console

console = Console()


METORIAL_TEMPLATE = '''import os
from metorial import Metorial
from openai import AsyncOpenAI


async def call_metorial(
    message: str,
    deployment_id: str = None,
    model: str = "gpt-4o",
    max_steps: int = 25
):
    metorial_api_key = os.getenv('METORIAL_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    deployment_id = deployment_id or os.getenv('METORIAL_DEPLOYMENT_ID')

    if not all([metorial_api_key, openai_api_key, deployment_id]):
        raise ValueError("Missing environment variables: METORIAL_API_KEY, OPENAI_API_KEY, METORIAL_DEPLOYMENT_ID")

    metorial = Metorial(api_key=metorial_api_key)
    openai = AsyncOpenAI(api_key=openai_api_key)

    response = await metorial.run(
        message=message,
        server_deployments=[deployment_id],
        client=openai,
        model=model,
        max_steps=max_steps
    )

    return response.text
'''


def use_metorial():
    """Add Metorial MCP integration to the project."""

    # Check if we're in a FastApps project
    if not Path("server").exists():
        console.print("[red]Error: Not in a FastApps project directory.[/red]")
        console.print("[yellow]Please run this command from your project root.[/yellow]")
        console.print("\n[cyan]If you haven't initialized a project yet:[/cyan]")
        console.print("  fastapps init myproject")
        return False

    # Create api directory if it doesn't exist
    api_dir = Path("server/api")
    api_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py in api directory
    init_file = api_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")

    # Create metorial_mcp.py file
    metorial_file = api_dir / "metorial_mcp.py"

    if metorial_file.exists():
        console.print(f"[yellow]Warning: {metorial_file} already exists.[/yellow]")
        console.print("[yellow]Skipping file creation.[/yellow]")
    else:
        metorial_file.write_text(METORIAL_TEMPLATE)
        console.print(f"\n[green]✓ Created: {metorial_file}[/green]")

    # Check requirements.txt and suggest adding dependencies
    req_file = Path("requirements.txt")
    if req_file.exists():
        requirements = req_file.read_text()
        needs_metorial = "metorial" not in requirements
        needs_openai = "openai" not in requirements

        if needs_metorial or needs_openai:
            console.print("\n[yellow]⚠ Missing dependencies in requirements.txt:[/yellow]")
            if needs_metorial:
                console.print("  - metorial")
            if needs_openai:
                console.print("  - openai")

            console.print("\n[cyan]Add these dependencies:[/cyan]")
            console.print("  echo 'metorial' >> requirements.txt")
            console.print("  echo 'openai' >> requirements.txt")
            console.print("  pip install -r requirements.txt")
            console.print("  # Or: uv pip install -r requirements.txt")

    # Display setup instructions
    console.print("\n[bold green]✓ Metorial MCP integration added![/bold green]")
    console.print("\n[cyan]Setup Instructions:[/cyan]")
    console.print("\n[yellow]1. Install dependencies:[/yellow]")
    console.print("   pip install metorial openai")
    console.print("   # Or: uv pip install metorial openai")

    console.print("\n[yellow]2. Set environment variables:[/yellow]")
    console.print("   export METORIAL_API_KEY='your_metorial_api_key'")
    console.print("   export OPENAI_API_KEY='your_openai_api_key'")
    console.print("   export METORIAL_DEPLOYMENT_ID='your_deployment_id'")

    console.print("\n[yellow]3. Usage in your code:[/yellow]")
    console.print("   from server.api.metorial_mcp import call_metorial")
    console.print("")
    console.print("   result = await call_metorial('Search for AI news')")
    console.print("   print(result)")

    console.print("\n[dim]Documentation: https://metorial.ai/docs[/dim]")
    console.print()

    return True


def use_integration(integration_name: str):
    """
    Add an integration to the FastApps project.

    Args:
        integration_name: Name of the integration (e.g., 'metorial')
    """

    if integration_name == "metorial":
        return use_metorial()
    else:
        console.print(f"[red]Error: Unknown integration '{integration_name}'[/red]")
        console.print("\n[cyan]Available integrations:[/cyan]")
        console.print("  - metorial    Add Metorial MCP integration")
        console.print("\n[dim]More integrations coming soon![/dim]")
        return False

