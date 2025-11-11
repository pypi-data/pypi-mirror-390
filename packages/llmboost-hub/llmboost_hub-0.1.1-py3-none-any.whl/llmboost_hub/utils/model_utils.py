import os
from typing import List


def path_has_files(path: str) -> bool:
    """
    Return True if 'path' exists, is a directory, and contains at least one file
    in its subtree (current dir or any nested subdirectory).

    Args:
        path: Absolute or relative directory path.

    Returns:
        True if there is at least one regular file somewhere under 'path'; False otherwise.
    """
    # Fast-fail if not a directory
    if not os.path.isdir(path):
        return False
    # Walk the tree and short-circuit as soon as we see any file
    for _, _, files in os.walk(path):
        if files:
            return True
    return False


def is_model_downloaded(models_root: str, model_id: str) -> bool:
    """
    Check if the models root contains a downloaded model directory for `model_id`.

    Args:
        models_root: Root directory that stores models (e.g., `config.LBH_MODELS`).
        model_id: Model identifier; may include `org/name` or plain name.

    Returns:
        True if `models_root/model_id` exists and contains at least one file; False otherwise.
    """
    return path_has_files(os.path.join(models_root, str(model_id or "")))


def get_model_name_from_model_id(model_id: str) -> str:
    """
    Get name of model from a Hugging Face style model id.
    Applies following transformations:
        - Remove repo/organization prefix (if present; splits on '/')
    Converts any 'org/name' to just 'name'.

    Examples:
        'Org/Model_Name' -> 'Model_name'
        'model.name'     -> 'model.name'

    Args:
        model_id: Model id such as 'org/name' or 'name'.

    Returns:
        Normalized model name.
    """
    parts = str(model_id or "").split("/")
    return parts[-1]  # get last part after '/'


def get_repo_from_model_id(model_id: str) -> str:
    """
    Extract the organization/user (repo owner) from a Hugging Face style model id.

    Examples:
        'org/name' -> 'org'
        'name'     -> ''  (no org present)

    Args:
        model_id: Model id such as 'org/name' or 'name'.

    Returns:
        The repo/organization segment if present; otherwise an empty string.
    """
    parts = str(model_id or "").split("/")
    return parts[-2] if len(parts) >= 2 else ""
