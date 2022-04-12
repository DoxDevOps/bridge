from fabric import Connection


def get_app_version(user_name: str, ip_address: str, app_dir: str) -> str:
    """gets version of an application running on remote server

    Args:
        user_name (str): remote user name
        ip_address (str): ip address of remote server
        app_dir (str): directory of application

    Returns:
        str: version of application on remote server
    """
    try:
        run_cmd = Connection(
            f"{user_name}@{ip_address}").run(f"cd {app_dir} && git describe", hide=True)

    except Exception as e:
        print(e)
        return "failed_to_get_version"

    return "{0.stdout}".format(run_cmd).strip()


def get_host_os(user_name: str, ip_address: str) -> str:
    """gets version of operating system running on remote server

    Args:
        user_name (str): remote user name
        ip_address (str): ip address of remote server

    Returns:
        str: version of operating system on remote server
    """
    try:
        run_cmd = Connection(
            f"{user_name}@{ip_address}").run("uname -a", hide=True)

    except Exception as e:
        print(e)
        return "failed_to_get_version"

    return "{0.stdout}".format(run_cmd).strip()
