from bfabric import Bfabric, BfabricAuth, BfabricClientConfig
from bfabric.config.config_data import ConfigData
from bfabric_web_apps.utils.config import settings
from bfabric_web_apps.utils.url_utils import normalize_url


def get_power_user_wrapper(token_data):
    """
    Initializes and returns a Bfabric power user instance for the given B-Fabric instance.

    Reads power user credentials from settings based on the base_url from token_data.

    Args:
        token_data (dict): A dictionary containing token information.
            Required key: "webbase_data" - the B-Fabric base URL

    Returns:
        Bfabric: A Bfabric instance initialized with power user credentials
        for the same B-Fabric instance as the token.

    Raises:
        ValueError: If webbase_data is missing or credentials are not configured.
    """
    base_url = token_data.get("webbase_data")

    if not base_url:
        raise ValueError("token_data must contain 'webbase_data' field")

    # Normalize URLs for comparison (removes trailing slashes)
    normalized_base_url = normalize_url(base_url)
    normalized_credentials = {normalize_url(url): creds
                             for url, creds in settings.POWER_USER_CREDENTIALS.items()}

    # Get power user credentials for this instance
    credentials = normalized_credentials.get(normalized_base_url)
    if not credentials:
        raise ValueError(
            f"No power user credentials configured for B-Fabric instance '{base_url}'. "
            f"Please add credentials to POWER_USER_CREDENTIALS in settings."
        )

    auth = BfabricAuth(login=credentials['login'], password=credentials['password'])
    client_config = BfabricClientConfig(base_url=base_url)
    config_data = ConfigData(client=client_config, auth=auth)
    return Bfabric(config_data=config_data)