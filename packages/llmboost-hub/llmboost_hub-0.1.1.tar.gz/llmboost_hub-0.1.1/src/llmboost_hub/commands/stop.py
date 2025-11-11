import click
import subprocess

from llmboost_hub.utils.container_utils import (
    container_name_for_model,
    is_container_running,
)
from llmboost_hub.commands.completions import complete_model_names


def do_stop(model: str, container: str | None, verbose: bool = False) -> dict:
    """
    Stop the model's container.

    Args:
        model: Model identifier (used when container is not directly provided).
        container: Optional explicit container name to stop.
        verbose: If True, echo the docker command.

    Returns:
        Dict: {returncode: int, container_name: str, error: str|None}
    """
    cname = container or container_name_for_model(model)

    # Fast-fail if target container is not running
    if not is_container_running(cname):
        return {
            "returncode": 1,
            "container_name": cname,
            "error": f"Container '{cname}' is not running.",
        }
    cmd = ["docker", "stop", cname]
    if verbose:
        click.echo("[run] " + " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        return {"returncode": 0, "container_name": cname, "error": None}
    except subprocess.CalledProcessError as e:
        return {
            "returncode": e.returncode,
            "container_name": cname,
            "error": f"Docker stop failed (exit {e.returncode})",
        }


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("model", required=True, shell_complete=complete_model_names)
@click.option(
    "-c", "--container", "container", type=str, help="Container name to stop (overrides model)."
)
@click.pass_context
def stop(ctx: click.Context, model, container):
    """
    Stops a running container for a given model (or explicit name).
    """
    verbose = ctx.obj.get("VERBOSE", False)
    res = do_stop(model, container, verbose=verbose)
    if res["returncode"] != 0:
        raise click.ClickException(res["error"] or "Stop failed")
