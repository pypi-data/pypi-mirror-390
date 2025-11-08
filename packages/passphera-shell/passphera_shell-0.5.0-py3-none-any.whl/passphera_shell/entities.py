from datetime import datetime, timezone

from pydantic import BaseModel, Field

from passphera_core.utilities import default_properties


class Generator(BaseModel):
    """
    A Pydantic model representing the configuration for the password generator.
    This model is used for serialization and validation at the application boundaries.
    """
    shift: int = Field(default=default_properties["shift"])
    multiplier: int = Field(default=default_properties["multiplier"])
    key: str = Field(default=default_properties["key"])
    algorithm: str = Field(default=default_properties["algorithm"])
    prefix: str = Field(default=default_properties["prefix"])
    postfix: str = Field(default=default_properties["postfix"])
    characters_replacements: dict[str, str] = Field(default_factory=dict)


class Password(BaseModel):
    """
    A Pydantic model representing a password entry in the vault.
    """
    context: str = Field(default="")
    password: str = Field(default="")
    salt: bytes = Field(default=b"")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
