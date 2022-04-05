from typing import Any
import requests
import json


def get_hosts_from_api(endpoint: str) -> Any:
    """gets host details from api

    Args:
        endpoint (str): endpoint of api

    Returns:
        dict: hosts from api
    """
    try:
        response = requests.get(endpoint)

    except requests.exceptions.Timeout as e:
        print("timeout error: ", e)
        return False

    except requests.exceptions.TooManyRedirects as e:
        print("too many redirects: ", e)
        return False

    except requests.exceptions.RequestException as e:
        print("catastrophic error: ", e)
        return False

    return json.loads(response.text)
