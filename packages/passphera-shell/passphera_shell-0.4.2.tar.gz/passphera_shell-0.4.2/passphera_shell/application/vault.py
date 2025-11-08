from passphera_shell.entities import Generator, Password
from passphera_shell.exceptions import DuplicatePasswordException, PasswordNotFoundException
from passphera_shell.interfaces import GeneratorRepository, VaultRepository, CryptoService


class GeneratePasswordUseCase:
    def __init__(
            self,
            vault_repository: VaultRepository,
            generator_repository: GeneratorRepository,
            crypto_service: CryptoService,
    ):
        self.vault_repository = vault_repository
        self.generator_repository: GeneratorRepository = generator_repository
        self.crypto_service: CryptoService = crypto_service

    def __call__(self, context: str, text: str) -> Password:
        try:
            password_entity: Password = self.vault_repository.get(context)
            raise DuplicatePasswordException(password_entity)
        except PasswordNotFoundException:
            password_entity: Password = Password(context=context)
            generator_entity: Generator = self.generator_repository.get()
            password = generator_entity.generate_password(text)
            crypted_password, salt = self.crypto_service.encrypt(password)
            password_entity.password = crypted_password
            password_entity.salt = salt
            self.vault_repository.save(password_entity)
            return password_entity


class GetPasswordUseCase:
    def __init__(self, vault_repository: VaultRepository, crypto_service: CryptoService):
        self.vault_repository: VaultRepository = vault_repository
        self.crypto_service: CryptoService = crypto_service

    def __call__(self, context: str) -> Password:
        try:
            password_entity: Password = self.vault_repository.get(context)
            password_entity.password = self.crypto_service.decrypt(password_entity.password, password_entity.salt)
            return password_entity
        except PasswordNotFoundException:
            raise PasswordNotFoundException()


class UpdatePasswordUseCase:
    def __init__(
            self,
            vault_repository: VaultRepository,
            generator_repository: GeneratorRepository,
            crypto_service: CryptoService,
    ):
        self.vault_repository: VaultRepository = vault_repository
        self.generator_repository: GeneratorRepository = generator_repository
        self.crypto_service: CryptoService = crypto_service

    def __call__(self, context: str, text: str) -> Password:
        try:
            password_entity: Password = self.vault_repository.get(context)
            generator_entity: Generator = self.generator_repository.get()
            password = generator_entity.generate_password(text)
            crypted_password, salt = self.crypto_service.encrypt(password)
            password_entity.password = crypted_password
            password_entity.salt = salt
            self.vault_repository.update(password_entity)
            return password_entity
        except PasswordNotFoundException:
            raise PasswordNotFoundException()


class DeletePasswordUseCase:
    def __init__(self, vault_repository: VaultRepository):
        self.vault_repository: VaultRepository = vault_repository

    def __call__(self, context: str) -> Password:
        try:
            password_entity: Password = self.vault_repository.get(context)
            self.vault_repository.delete(password_entity)
            return password_entity
        except PasswordNotFoundException:
            raise PasswordNotFoundException()


class ListPasswordsUseCase:
    def __init__(self, vault_repository: VaultRepository):
        self.vault_repository: VaultRepository = vault_repository

    def __call__(self) -> list[Password]:
        return self.vault_repository.list()


class FlushPasswordsUseCase:
    def __init__(self, vault_repository: VaultRepository):
        self.vault_repository: VaultRepository = vault_repository

    def __call__(self) -> None:
        self.vault_repository.flush()
