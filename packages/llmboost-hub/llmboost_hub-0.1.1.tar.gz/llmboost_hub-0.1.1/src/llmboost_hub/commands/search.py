import click
import re
import requests
from typing import List, Dict
from llmboost_hub.commands.login import do_login
from llmboost_hub.utils.config import config
from llmboost_hub.utils import gpu_info
import tabulate
import pandas as pd
from llmboost_hub.utils.lookup_cache import load_lookup_df


def _fetch_json(endpoint: str, params: Dict[str, str], verbose: bool = False) -> List[Dict]:
    """
    Fetch a JSON payload from an endpoint with query params.

    Args:
        endpoint: URL to query.
        params: Mapping of query string params.
        verbose: If True, echo the URL and params.

    Returns:
        A list of JSON objects.

    Raises:
        ClickException: On non-200 responses or invalid/malformed bodies.
    """
    # Future support: keep unused for now
    if verbose:
        click.echo(f"Downloading JSON from {endpoint} with params {params}")
    resp = requests.get(endpoint, params=params, timeout=10)
    if resp.status_code != 200:
        raise click.ClickException(f"Lookup failed ({resp.status_code}): {resp.text}")
    try:
        data = resp.json()
    except ValueError:
        raise click.ClickException("Lookup returned invalid JSON")
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    if not isinstance(data, list):
        raise click.ClickException("Unexpected lookup response format")
    return data


def _fetch_from_remote(endpoint: str, query: str, verbose: bool = False) -> pd.DataFrame:
    """
    Fetch lookup CSV (with cache and fallback) and normalize columns.

    Args:
        endpoint: CSV endpoint.
        query: Filter string passed to the loader (used by cache layer).
        verbose: If True, echo loader activity.

    Returns:
        DataFrame with columns: model, gpu, docker_image (sorted by model,gpu).

    Raises:
        ClickException: When required columns are missing from the CSV.
    """
    df = load_lookup_df(endpoint, query, verbose=verbose)

    # Normalize column names
    df.columns = [str(c).strip().lower() for c in df.columns]
    required_cols = {"model", "gpu", "docker_image"}
    if not required_cols.issubset(set(df.columns)):
        missing = required_cols - set(df.columns)
        raise click.ClickException(
            f"Lookup CSV missing required columns: {', '.join(sorted(missing))}"
        )

    # sort by model,gpu
    df = df.sort_values(by=["model", "gpu"]).reset_index(drop=True)
    df.index += 1  # user-friendly display index

    return df[["model", "gpu", "docker_image"]]


def do_search(
    query: str = r".*",
    verbose: bool = False,
    local_only: bool = False,
    skip_cache_update: bool = False,
    names_only: bool = False,
) -> pd.DataFrame:
    """
    Search remote/locally-cached lookup and filter by query and local GPU families.

    Behavior:
        - local_only=True: skip license check and network; load only from local cache file.
        - otherwise: attempt login/validation and fetch with cache fallback.
        - Perform case-insensitive LIKE on 'model'.
        - Filter rows to those matching detected GPU families.

    Args:
        query: Regex pattern to filter 'model' column (case-insensitive).
        verbose: If True, echo key steps.
        local_only: Skip license check and remote fetch; read from local cache only.
        skip_cache_update: Reserved for future use (cache policy is handled in loader).
        names_only: If True, return only the 'model' column.

    Returns:
        DataFrame with columns: model, gpu, docker_image (possibly empty).
    """
    if not local_only:
        # Best-effort: try to ensure license; even on failure, loader may still use cache
        do_login(license_file=None, verbose=verbose)
    lookup_df = load_lookup_df(
        config.LBH_LOOKUP_URL,
        query,
        verbose=verbose,
        local_only=local_only,
        skip_cache_update=skip_cache_update,
    )

    # Filter by query (case-insensitive LIKE on 'model' field)
    filtered_df = lookup_df[
        lookup_df["model"].astype(str).str.contains(pat=query, regex=True, flags=re.IGNORECASE)
    ].reset_index(drop=True)
    filtered_df.index += 1  # user-friendly display index

    # GPU family filter
    available_gpus = gpu_info.get_gpus()
    local_families = {gpu_info.gpu_name2family(g) for g in available_gpus if g}
    filtered_df = (
        filtered_df.assign(_gpu_family=filtered_df["gpu"].apply(gpu_info.gpu_name2family))
        .loc[lambda df: df["_gpu_family"].isin(local_families)]
        .drop(columns=["_gpu_family"])
    ).reset_index(drop=True)
    filtered_df.index += 1  # user-friendly display index

    # Short-circuit: names only
    if names_only:
        return filtered_df[["model"]]

    return filtered_df


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("query", type=str, required=True)
@click.option(
    "--local-only",
    is_flag=True,
    help="Use only the local lookup cache (skip online fetch and license validation).",
)
@click.option(
    "--skip-cache-update",
    is_flag=True,
    help="Fetch, but skip updating local cache. (not applicable with --local-only).",
)
@click.option(
    "--names-only",
    is_flag=True,
    help="Return model names only.",
)
@click.pass_context
def search(ctx: click.Context, query, local_only, skip_cache_update, names_only):
    """
    Search for models in the LLMBoost registry.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    results_df = do_search(
        query,
        verbose=verbose,
        local_only=local_only,
        skip_cache_update=skip_cache_update,
        names_only=names_only,
    )

    click.echo(f"Found {len(results_df)} relevant images")
    if results_df.empty:
        return

    # Present results via tabulate
    click.echo(
        tabulate.tabulate(
            results_df.values.tolist(),
            headers=list(results_df.columns),
            showindex=list(results_df.index),
            tablefmt="psql",
        )
    )
    return results_df
