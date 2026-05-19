from typing import Annotated, Union
from midil.utils.models import SnakeCaseModel
from pydantic import Field


_DEFAULT_EXPIRES_IN_SECONDS = 900


class HMACCursorConfig(SnakeCaseModel):
    algorithm: str = Field(
        "hmac", description="Type discriminator for HMAC cursor config"
    )
    secretKey: str = Field(..., description="Secret key for cursor pagination.")
    expiresInSeconds: int = Field(
        default=_DEFAULT_EXPIRES_IN_SECONDS,
        description="Expiration time for cursor in seconds.",
    )


CursorConfig = Annotated[
    Union[HMACCursorConfig],
    Field(discriminator="algorithm"),
]
