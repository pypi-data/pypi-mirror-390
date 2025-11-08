from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field
from typing import Optional, List, Dict

class Settings(BaseSettings):

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    REDIS_USERNAME: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None

    # Power user credentials per B-Fabric instance (service accounts)
    POWER_USER_CREDENTIALS: Dict[str, Dict[str, str]] = Field(
        default={
            "https://fgcz-bfabric.uzh.ch/bfabric": {
                "login": "gfeeder",
                "password": ""
            },
            "https://fgcz-bfabric-test.uzh.ch/bfabric": {
                "login": "",
                "password": ""
            }
        },
        description="Power user credentials mapped to each B-Fabric instance base URL"
    )

    HOST: str = "127.0.0.1"
    PORT: int = 8050

    DEV: bool = False
    DEBUG: bool = False

    DEVELOPER_EMAIL_ADDRESS: EmailStr = "claudio.cannizzaro@fgcz.uzh.ch"
    BUG_REPORT_EMAIL_ADDRESS: EmailStr = "gwtools@fgcz.system"

    #Run main pipeline config (only FGCZ specific)
    GSTORE_REMOTE_PATH: str = "/path/to/remote/gstore"
    SCRATCH_PATH: str = "/scratch/folder"
    TRX_LOGIN: str = "trxcopy@fgcz-server.uzh.ch" 
    TRX_SSH_KEY: str = "/home/user/.ssh/your_ssh_key"
    URL: str = "https:/fgcz/dummy/url"

    # Which service id to use for the charge 
    SERVICE_ID: int = 0

    # Which dataset template id to use for dataset creation
    DATASET_TEMPLATE_ID: int = 0

    # B-Fabric Configuration
    VALIDATION_INSTANCE_URL: str = "https://fgcz-bfabric-test.uzh.ch/bfabric"

    # Whitelist of supported B-Fabric instances (for security validation)
    SUPPORTED_BFABRIC_INSTANCES: List[str] = Field(
        default=[
            "https://fgcz-bfabric.uzh.ch/bfabric",
            "https://fgcz-bfabric-test.uzh.ch/bfabric"
        ],
        description="List of allowed B-Fabric base URLs. Tokens from other instances will be rejected."
    )

    class Config:

        env_file = ".env"  

        # Disable reading from environment variables
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return file_secret_settings, init_settings 

# Instantiate settings
settings = Settings()

