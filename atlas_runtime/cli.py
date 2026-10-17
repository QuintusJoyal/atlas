import click
from atlas_runtime.commands import run, resume, status, checkpoint_fork

@click.group()
@click.version_option(version="0.1.0", package_name="atlas-runtime")
def cli():
    """Atlas Orchestration Runtime"""
    pass

cli.add_command(run.run)
cli.add_command(resume.resume)
cli.add_command(status.status)
cli.add_command(checkpoint_fork.checkpoint_fork)

if __name__ == "__main__":
    cli()
