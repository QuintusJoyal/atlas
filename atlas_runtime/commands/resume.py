import click
from atlas_runtime import checkpoint


@click.command()
@click.argument("checkpoint_id")
def resume(checkpoint_id):
    """Resume from checkpoint."""
    cp = checkpoint.Checkpoint()
    try:
        data = cp.load(checkpoint_id)
        click.echo(f"Resuming from {checkpoint_id}")
        click.echo(f"Level: {data.get('level')}")
        click.echo(f"Run: {data.get('runId')}")
        click.echo(f"Phase: {data.get('phase')}")
    except Exception as e:
        raise click.ClickException(str(e))
