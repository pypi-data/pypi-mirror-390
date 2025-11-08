from passphera_core.entities import Generator as GeneratorCoreEntity
from passphera_shell.entities import Generator as GeneratorShellEntity
from passphera_shell.interfaces import GeneratorRepository


class GetGeneratorUseCase:
    def __init__(self, generator_repository: GeneratorRepository):
        self.generator_repository: GeneratorRepository = generator_repository

    def __call__(self) -> GeneratorShellEntity:
        return self.generator_repository.get()


class UpdateGeneratorUseCase:
    def __init__(self, generator_repository: GeneratorRepository):
        self.generator_repository: GeneratorRepository = generator_repository

    def __call__(self, generator: GeneratorShellEntity) -> None:
        self.generator_repository.update(generator)


class GetPropertiesUseCase:
    def __init__(self, generator_repository: GeneratorRepository):
        self.generator_repository: GeneratorRepository = generator_repository

    def __call__(self) -> dict:
        generator_shell_entity = self.generator_repository.get()
        core_entity = GeneratorCoreEntity(**generator_shell_entity.model_dump())
        return core_entity.get_properties()


class SetPropertyUseCase:
    def __init__(self, generator_repository: GeneratorRepository):
        self.generator_repository: GeneratorRepository = generator_repository

    def __call__(self, prop: str, value: str) -> GeneratorShellEntity:
        generator_shell_entity = self.generator_repository.get()
        core_entity = GeneratorCoreEntity(**generator_shell_entity.model_dump())
        core_entity.set_property(prop, value)
        updated_shell_entity = GeneratorShellEntity(**core_entity.__dict__)
        self.generator_repository.update(updated_shell_entity)
        return updated_shell_entity


class ResetPropertyUseCase:
    def __init__(self, generator_repository: GeneratorRepository):
        self.generator_repository: GeneratorRepository = generator_repository

    def __call__(self, prop: str) -> GeneratorShellEntity:
        generator_shell_entity = self.generator_repository.get()
        core_entity = GeneratorCoreEntity(**generator_shell_entity.model_dump())
        core_entity.reset_property(prop)
        updated_shell_entity = GeneratorShellEntity(**core_entity.__dict__)
        self.generator_repository.update(updated_shell_entity)
        return updated_shell_entity


class GetCharacterReplacementUseCase:
    def __init__(self, generator_repository: GeneratorRepository):
        self.generator_repository: GeneratorRepository = generator_repository

    def __call__(self, character: str) -> str:
        generator_shell_entity = self.generator_repository.get()
        core_entity = GeneratorCoreEntity(**generator_shell_entity.model_dump())
        return core_entity.get_character_replacement(character)


class SetCharacterReplacementUseCase:
    def __init__(self, generator_repository: GeneratorRepository):
        self.generator_repository: GeneratorRepository = generator_repository

    def __call__(self, character: str, replacement: str) -> GeneratorShellEntity:
        generator_shell_entity = self.generator_repository.get()
        core_entity = GeneratorCoreEntity(**generator_shell_entity.model_dump())
        core_entity.set_character_replacement(character, replacement)
        updated_shell_entity = GeneratorShellEntity(**core_entity.__dict__)
        self.generator_repository.update(updated_shell_entity)
        return updated_shell_entity


class ResetCharacterReplacementUseCase:
    def __init__(self, generator_repository: GeneratorRepository,):
        self.generator_repository: GeneratorRepository = generator_repository

    def __call__(self, character: str) -> GeneratorShellEntity:
        generator_shell_entity = self.generator_repository.get()
        core_entity = GeneratorCoreEntity(**generator_shell_entity.model_dump())
        core_entity.reset_character_replacement(character)
        updated_shell_entity = GeneratorShellEntity(**core_entity.__dict__)
        self.generator_repository.update(updated_shell_entity)
        return updated_shell_entity

