import botocore


def get_ssm_parameter(
    client: botocore.client, parameter_name: str, decryption: bool = True
) -> str:
    """
    Function to grab parameters from SSM

    note: withdecryption = false will make pg user not work bc its a securestring.
        ignored for String and StringList parameter types

    Args:
        parameter_name (string) - name of the parameter you want

        decryption (Boolean) - Parameter if decryption is needed to access the parameter (default True)

    Returns:
        parameter_value (string)
    """
    try:
        resp = client.get_parameter(Name=parameter_name, WithDecryption=decryption)
        return resp["Parameter"]["Value"]
    except BaseException as e:
        raise e(f"Couldn't grab parameter {parameter_name}, {e}")
