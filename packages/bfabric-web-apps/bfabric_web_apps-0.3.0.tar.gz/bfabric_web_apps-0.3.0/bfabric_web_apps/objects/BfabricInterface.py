from bfabric import Bfabric
from bfabric.rest.token_data import TokenData
import json
import datetime
from bfabric_web_apps.utils.get_logger import get_logger
import os
import bfabric_web_apps

from bfabric_web_apps.utils.config import settings
from bfabric_web_apps.utils.url_utils import normalize_url

class BfabricInterface( Bfabric ):
    _instance = None  # Singleton instance
    _wrapper = None   # Shared wrapper instance
    _token_data = None  # Store TokenData for later use
    """
    A class to interface with the Bfabric API, providing methods to validate tokens,
    retrieve data, and send bug reports.
    """

    def __init__(self):
        """
        Initializes an instance of BfabricInterface.
        """
        pass

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists (Singleton Pattern)."""
        if cls._instance is None:
            cls._instance = super(BfabricInterface, cls).__new__(cls)
        return cls._instance

    def _tokendata_to_legacy_dict(self, token_data: TokenData) -> dict:
        """
        Convert new TokenData Pydantic model to legacy token_data dict format.
        Provides backward compatibility for existing code.

        Args:
            token_data: TokenData from connect_webapp()

        Returns:
            dict: Legacy format token_data
        """
        return {
            'jobId': token_data.job_id,
            'user_data': token_data.user,
            'userWsPassword': token_data.user_ws_password.get_secret_value(),
            'environment': token_data.environment,
            'entityClass_data': token_data.entity_class,
            'entity_id_data': token_data.entity_id,
            'application_data': str(token_data.application_id),
            'token_expires': token_data.token_expires.strftime("%Y-%m-%d %H:%M:%S"),
            'webbase_data': token_data.caller,  # Use caller from token (already validated)
            'application_params_data': {},  # Legacy field, unused
        }

    def _initialize_wrapper(self, wrapper: Bfabric, token_data: TokenData):
        """Internal method to initialize the Bfabric wrapper after token validation."""
        if not wrapper or not token_data:
            raise ValueError("Both wrapper and token_data are required to initialize.")

        # Store the wrapper and token data
        if self._wrapper is None:
            self._wrapper = wrapper
            self._token_data = token_data


    def get_wrapper(self):
        """Return the existing wrapper or raise an error if not initialized."""
        if self._wrapper is None:
            raise RuntimeError("Bfabric wrapper is not initialized. Token validation must run first.")
        return self._wrapper
    

    def token_to_data(self, token):
        """
        Validates the given token and retrieves its associated data using connect_webapp.

        Args:
            token (str): The token to validate.

        Returns:
            str: A JSON string containing token data if valid.
            str: "EXPIRED" if the token is expired.
            None: If the token is invalid or validation fails.
        """

        if not token:
            return None

        try:
            # Use the new connect_webapp method with configurable validation URL
            wrapper, token_data = Bfabric.connect_webapp(
                token=token,
                validation_instance_url=settings.VALIDATION_INSTANCE_URL
            )

            # Validate that the token's instance is in the supported whitelist
            # Normalize URLs for comparison (removes trailing slashes)
            normalized_caller = normalize_url(token_data.caller)
            normalized_whitelist = [normalize_url(url) for url in settings.SUPPORTED_BFABRIC_INSTANCES]

            if normalized_caller not in normalized_whitelist:
                raise ValueError(
                    f"B-Fabric instance '{token_data.caller}' is not in the list of supported instances. "
                    f"Supported instances: {settings.SUPPORTED_BFABRIC_INSTANCES}"
                )

            # Check if token is expired (7 days grace period)
            current_time = datetime.datetime.now(tz=token_data.token_expires.tzinfo)
            if current_time > token_data.token_expires + datetime.timedelta(days=7):
                return "EXPIRED"

            # Initialize the wrapper and store token data
            self._initialize_wrapper(wrapper, token_data)

            # Convert TokenData to legacy dict format for backward compatibility
            token_data_dict = self._tokendata_to_legacy_dict(token_data)

            # Log the token validation process
            L = get_logger(token_data_dict)
            L.log_operation(
                operation="Authentication Process",
                message=f"Token validated successfully. User {token_data_dict.get('user_data')} authenticated.",
                params=None,
                flush_logs=True
            )

            return json.dumps(token_data_dict)

        except Exception as e:
            # Token validation failed
            print(f"Token validation failed: {e}")
            return None
        



    def entity_data(self, token_data: dict) -> str: 
        """
        Retrieves entity data associated with the provided token.

        Args:
            token_data (dict): The token data.

        Returns:
            str: A JSON string containing entity data.
            {}: If the retrieval fails or token_data is invalid.
        """

        entity_class_map = {
            "Run": "run",
            "Sample": "sample",
            "Project": "container",
            "Order": "container",
            "Container": "container",
            "Plate": "plate",
            "Workunit": "workunit",
            "Resource": "resource",
            "Dataset": "dataset"
        }

        if not token_data:
            return json.dumps({})
        
        wrapper = self.get_wrapper()
        entity_class = token_data.get('entityClass_data', None)
        endpoint = entity_class_map.get(entity_class, None)
        entity_id = token_data.get('entity_id_data', None)
        jobId = token_data.get('jobId', None)
        username = token_data.get("user_data", "None")
        environment = token_data.get("environment", "None")

        if wrapper and entity_class and endpoint and entity_id and jobId:
            L = get_logger(token_data)
            
            # Log the read operation directly using Logger L
            entity_data_dict = L.logthis(
                api_call=wrapper.read,
                endpoint=endpoint,
                obj={"id": entity_id},
                max_results=None,
                params=None,
                flush_logs=False
            )[0]

            
            if entity_data_dict:
                json_data = json.dumps({
                    "name": entity_data_dict.get("name", ""),
                    "createdby": entity_data_dict.get("createdby"),
                    "created": entity_data_dict.get("created"),
                    "modified": entity_data_dict.get("modified"),
                    "full_api_response": entity_data_dict,
                })
                return json_data
            else:
                L.log_operation(
                    operation="entity_data",
                    message="Entity data retrieval failed or returned None.",
                    params=None,
                    flush_logs=True
                )
                print("entity_data_dict is empty or None")
                return json.dumps({})
            
        else:
            print("Invalid input or entity information")
            return json.dumps({})
        

    def app_data(self, token_data: dict) -> str:
        """
        Retrieves application data (App Name and Description) associated with the provided token.

        Args:
            token_data (dict): The token data.

        Returns:
            str: A JSON string containing application data.
            {}: If retrieval fails or token_data is invalid.
        """

        if not token_data:
            return json.dumps({})  # Return empty JSON if no token data

        # Extract App ID from token
        app_data_raw = token_data.get("application_data", None)
        
        try:
            app_id = int(app_data_raw)
        except:
            print("Invalid application_data format in token_data")
            return json.dumps({})  # Return empty JSON if app_id is invalid

        # Define API endpoint
        endpoint = "application"
        
        # Initialize Logger
        L = get_logger(token_data)
        
        # Get API wrapper
        wrapper = self.get_wrapper()
        if not wrapper:
            print("Failed to get Bfabric API wrapper")
            return json.dumps({})

        # Make API Call
        app_data_dict = L.logthis(
            api_call=wrapper.read,
            endpoint=endpoint,
            obj={"id": app_id},  # Query using the App ID
            max_results=None,
            params=None,
            flush_logs=False
        )

        # If API call fails, return empty JSON
        if not app_data_dict or len(app_data_dict) == 0:
            L.log_operation(
                operation="app_data",
                message=f"Failed to retrieve application data for App ID {app_id}",
                params=None,
                flush_logs=True
            )
            return json.dumps({})

        # Extract App ID, Name, and Description
        app_info = app_data_dict[0]  # First (and only) result

        json_data = json.dumps({
            "id": app_info.get("id", "Unknown"),
            "name": app_info.get("name", "Unknown"),
            "description": app_info.get("description", "No description available")
        })

        return json_data
     
    
    def send_bug_report(self, token_data = None, entity_data = None, description = None):
        """
        Sends a bug report via email.

        Args:
            token_data (dict): Token data to include in the report.
            entity_data (dict): Entity data to include in the report.
            description (str): A description of the bug.

        Returns:
            bool: True if the report is sent successfully, False otherwise.
        """

        mail_string = f"""
        BUG REPORT FROM QC-UPLOADER
            \n\n
            token_data: {token_data} \n\n 
            entity_data: {entity_data} \n\n
            description: {description} \n\n
            sent_at: {datetime.datetime.now()} \n\n
        """

        mail = f"""
            echo "{mail_string}" | mail -s "Bug Report" {bfabric_web_apps.BUG_REPORT_EMAIL_ADDRESS}
        """

        print("MAIL STRING:")
        print(mail_string)

        print("MAIL:")
        print(mail)

        os.system(mail)

        return True
    

    
# Create a globally accessible instance
bfabric_interface = BfabricInterface()


