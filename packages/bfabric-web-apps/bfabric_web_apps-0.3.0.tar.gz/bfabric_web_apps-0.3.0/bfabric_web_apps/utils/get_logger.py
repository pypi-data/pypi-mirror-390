from bfabric_web_apps.objects.Logger import Logger

def get_logger(token_data):
    """
    Extract logging-related information from token_data and create a Logger instance.

    Args:
        token_data (dict): Token data containing jobId, user_data, and webbase_data

    Returns:
        Logger: Initialized Logger instance
    """
    jobId = token_data.get('jobId', None)
    username = token_data.get("user_data", "None")
    base_url = token_data.get("webbase_data")

    if not base_url:
        raise ValueError("token_data must contain 'webbase_data' field")

    return Logger(
        jobid=jobId,
        username=username,
        base_url=base_url,
    )