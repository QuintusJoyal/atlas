import click
from atlas_runtime import orchestrator


@click.command()
@click.argument("workflow")
@click.option("--variant", type=click.Choice(["small", "full"]), default="full")
def run(workflow, variant):
    """Run a workflow."""
    orch = orchestrator.Orchestrator()
    try:
        fm = orch.load_workflow(workflow, variant)
        click.echo(f"Running {workflow} (variant: {variant})")
        click.echo(f"Description: {fm.get('description', 'N/A')}")
    except Exception as e:
        raise click.ClickException(str(e))
