import click
from atlas_runtime import checkpoint


@click.command("fork")
@click.argument("checkpoint_id")
@click.option("--level", type=click.Choice(["replay", "branch", "resume"]), default="resume")
def checkpoint_fork(checkpoint_id, level):
    """Fork a checkpoint."""
    cp = checkpoint.Checkpoint()
    try:
        result = cp.fork(checkpoint_id, fork_level=level)
        click.echo(f"Forked {checkpoint_id} as {level}: {result}")
    except Exception as e:
        raise click.ClickException(str(e))
