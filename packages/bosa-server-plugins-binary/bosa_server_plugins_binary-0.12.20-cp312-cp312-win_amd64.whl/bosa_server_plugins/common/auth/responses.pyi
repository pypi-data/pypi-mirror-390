from bosa_server_plugins.common.auth.custom import CustomAuthenticationScheme as CustomAuthenticationScheme
from bosa_server_plugins.common.auth.oauth2 import OAuth2AuthenticationScheme as OAuth2AuthenticationScheme
from pydantic import BaseModel, Field as Field
from typing import Annotated

class PluginAuthenticationSchemeResponse(BaseModel):
    """Response model for plugin authentication schemes."""
    supported_auth_types: list[Annotated[CustomAuthenticationScheme | OAuth2AuthenticationScheme, None]]
