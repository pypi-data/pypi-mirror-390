from pathlib import Path
from typing import Literal

from pydantic import SecretStr, Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


pixel_env_choices = AliasChoices("PIXEL_ENV", "KEYCLOAK_ENV")
pixel_username_choices = AliasChoices("PIXEL_USERNAME", "KEYCLOAK_USERNAME")
pixel_password_choices = AliasChoices("PIXEL_PASSWORD", "KEYCLOAK_PASSWORD")
pixel_realm_choices = AliasChoices("PIXEL_TENANT", "KEYCLOAK_REALM")

class PixelApiSettings(BaseSettings):
    """
    Settings for the Pixel API client
    """

    @classmethod
    def from_env_file(cls, env_file: Path | str) -> "PixelApiSettings":
        """Instantiate the settings from an environment file.

        Warning:
            Environment variables will always take precedence over the values in the file.
        """
        return cls(_env_file=env_file)  # type: ignore

    model_config = SettingsConfigDict(frozen=True, extra="ignore")  # Makes it hashable



    PIXEL_ENV: Literal["dev", "test", "prod"] = Field(validation_alias=pixel_env_choices, default="prod")

    PIXEL_USERNAME: str = Field(validation_alias=pixel_username_choices)
    """The client secret for the Keycloak server"""

    PIXEL_PASSWORD: SecretStr = Field(validation_alias=pixel_password_choices)
    """The password for the Keycloak"""

    PIXEL_TENANT: str = Field(validation_alias=pixel_realm_choices)
    """The realm for the Keycloak server"""

    PIXEL_SERVER_URL_OVERRIDE: str | None = Field(alias="PIXEL_SERVER_URL", default=None)
    PIXEL_API_URL_OVERRIDE: str | None = Field(alias="PIXEL_API_URL", default=None)
    
    @property
    def PIXEL_CLIENT_ID(self):
        return "frontend"
    
    
    @property
    def PIXEL_REALM(self):
        return self.PIXEL_TENANT.capitalize()
    
    @property
    def PIXEL_API_URL(self): 
        return self.PIXEL_API_URL_OVERRIDE or f"https://{self.PIXEL_ENV}.api.geodatapixel.no/{self.PIXEL_REALM.lower()}"
    
    @property
    def PIXEL_SERVER_URL(self):
        return self.PIXEL_SERVER_URL_OVERRIDE or f"https://{self.PIXEL_ENV}.keycloak.geodatapixel.no"

    PIXEL_CLIENT_NO_VERSION_CHECK: bool = False
    """If True, the client will not check for a newer version of the pixel-client package on startup."""
