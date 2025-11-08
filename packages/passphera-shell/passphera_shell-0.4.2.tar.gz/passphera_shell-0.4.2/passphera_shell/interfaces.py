from abc import ABC, abstractmethod

from passphera_shell.entities import Generator, Password


class GeneratorRepository(ABC):
    @abstractmethod
    def save(self, generator: Generator) -> None:
        pass

    @abstractmethod
    def get(self) -> Generator:
        pass

    @abstractmethod
    def update(self, generator: Generator) -> None:
        pass


class VaultRepository(ABC):
    @abstractmethod
    def save(self, password: Password) -> None:
        pass

    @abstractmethod
    def get(self, context: str) -> Password:
        pass

    @abstractmethod
    def update(self, password: Password) -> None:
        pass

    @abstractmethod
    def delete(self, password: Password) -> None:
        pass

    @abstractmethod
    def list(self) -> list[Password]:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass


class CryptoService(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> tuple[str, bytes]:
        """Encrypt plaintext and return (ciphertext, salt)."""
        pass

    @abstractmethod
    def decrypt(self, ciphertext: str, salt: bytes) -> str:
        """Decrypt ciphertext using salt and return plaintext."""
        pass
