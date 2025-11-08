from dataclasses import dataclass, field
from datetime import datetime, timezone

from passphera_core.entities import Generator as GeneratorEntity
from passphera_core.utilities import default_properties


@dataclass
class Generator(GeneratorEntity):
    def to_dict(self) -> dict:
        """Convert the Generator entity to a dictionary."""
        return {
            "shift": self.shift,
            "multiplier": self.multiplier,
            "key": self.key,
            "algorithm": self.algorithm,
            "prefix": self.prefix,
            "postfix": self.postfix,
            "character_replacements": self.characters_replacements,
        }

    def from_dict(self, data: dict) -> None:
        """Convert a dictionary to a Generator entity."""
        for key, value in data.items():
            if key in default_properties or key == "characters_replacements":
                setattr(self, key, value)


@dataclass
class Password:
    context: str = field(default_factory=str)
    text: str = field(default_factory=str)
    password: str = field(default_factory=str)
    salt: bytes = field(default_factory=lambda: bytes)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Convert the Password entity to a dictionary."""
        return {
            "context": self.context,
            "text": self.text,
            "password": self.password,
            "salt": self.salt,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def from_dict(self, data: dict) -> None:
        """Convert a dictionary to a Password entity."""
        for key, value in data.items():
            if key in ["context", "text", "password", "salt", "created_at", "updated_at"]:
                setattr(self, key, value)
