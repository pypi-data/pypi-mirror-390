"""Functions for working with tags"""

import requests

from oocli import config


def create(name: str, run_sha: str, *, project: str):
    """Create or update a tag"""
    response = requests.put(
        f"{config.settings().apiurl}/tags/{project}/{name}",
        headers={"X-API-Key": config.settings().token},
        params={"sha": run_sha},
    )
    if response.status_code == 422:
        raise RuntimeError(response.text)
    response.raise_for_status()


def read_all(project: str):
    """Retreive all tags in the project"""
    response = requests.get(
        f"{config.settings().apiurl}/tags/{project}",
        headers={"X-API-Key": config.settings().token},
    )
    response.raise_for_status()
    return response.json()
