"""Functions for working with projects"""

import requests

from oocli import config


def read_all():
    """Retreive all projects"""
    response = requests.get(
        f"{config.settings().apiurl}/projects",
        headers={"X-API-Key": config.settings().token},
    )
    response.raise_for_status()
    return response.json()
