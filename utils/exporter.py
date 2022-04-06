import requests


def send_data(endpoint: str, payload: dict, headers: dict) -> bool:
    """sends data to central repo

    Args:
        endpoint (str): central repo endpoint
        payload (dict): remote data
        headers (str): required headers

    Returns:
        bool: True if data is sent to central repo successfully, False otherwise
    """
    try:
        r = requests.post(endpoint, json=payload, headers=headers)

    except Exception as e:
        print("Failed to send data to a central point. The exception details is: ", e)
        return False

    else:

        r.raise_for_status()
        print('Data sent successfully', r.json())
        return True
