
from typing import Optional

import requests
from libgravatar import Gravatar


def get_gravatar_image(email) -> Optional[str]:
    """Only will return a url if the user exists and is correct on gravatar, otherwise None"""
    g = Gravatar(email)
    profile_url = g.get_profile()
    res = requests.get(profile_url)
    if res.status_code == 200:
        return g.get_image()
    return None