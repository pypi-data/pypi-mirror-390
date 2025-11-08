from dash import html
import dash_daq as daq
from bfabric_web_apps.utils.config import settings

def expired(base_url=None):
    """
    Returns an error message for expired sessions with a login link.

    Args:
        base_url (str, optional): The B-Fabric instance base URL.
                                  Defaults to VALIDATION_INSTANCE_URL if not provided.

    Returns:
        list: Dash HTML components for the expired session message.
    """
    url = base_url or settings.VALIDATION_INSTANCE_URL
    return [
        html.P("Your session has expired. Please log into bfabric to continue:"),
        html.A('Login to Bfabric', href=url)
    ]

def no_entity(base_url=None):
    """
    Returns an error message when entity data cannot be fetched.

    Args:
        base_url (str, optional): The B-Fabric instance base URL.
                                  Defaults to VALIDATION_INSTANCE_URL if not provided.

    Returns:
        list: Dash HTML components for the no entity error message.
    """
    url = base_url or settings.VALIDATION_INSTANCE_URL
    return [
        html.P("There was an error fetching the data for your entity. Please try accessing the applicaiton again from bfabric:"),
        html.A('Login to Bfabric', href=url)
    ]

def no_auth(base_url=None):
    """
    Returns an error message for unauthenticated users with a login link.

    Args:
        base_url (str, optional): The B-Fabric instance base URL.
                                  Defaults to VALIDATION_INSTANCE_URL if not provided.

    Returns:
        list: Dash HTML components for the no auth message.
    """
    url = base_url or settings.VALIDATION_INSTANCE_URL
    return [
        html.P("You are not currently logged into an active session. Please log into bfabric to continue:"),
        html.A('Login to Bfabric', href=url)
    ]

dev = [html.P("This page is under development. Please check back later."),html.Br(),html.A("email the developer for more details",href=f"mailto:{settings.DEVELOPER_EMAIL_ADDRESS}")]

auth = [html.Div(id="auth-div")]

charge_switch = [
    daq.BooleanSwitch(id='charge_run', on=True, label="Charge project for run"),
    html.Br()
]
