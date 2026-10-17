import click
from atlas_runtime import checkpoint


@click.command()
def status():
    """Show status."""
    cp = checkpoint.Checkpoint()
    checkpoints = cp.list()
    if not checkpoints:
        click.echo("No checkpoints found")
        return
    click.echo(f"Found {len(checkpoints)} checkpoints:")
    for c in checkpoints[:5]:
        click.echo(f"  {c['checkpointId']} (level={c.get('level')}, phase={c.get('phase')})")
