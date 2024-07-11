from abc import ABC, abstractmethod
from typing import TypeVar, Union

T = TypeVar("T")


class DatabaseInterface(ABC):

    @abstractmethod
    async def add_entity(self, entity: T) -> T:
        pass

    @abstractmethod
    async def add_entities(self, entities: list[T]) -> list:
        pass

    @abstractmethod
    async def get_entity(self, id: str) -> T:
        pass

    @abstractmethod
    async def get_entities_by_key(self, key: str, id: str) -> Union[bool, T]:
        pass

    @abstractmethod
    async def update_entity(self, id: str, data: dict) -> Union[bool, T]:
        pass

    @abstractmethod
    async def delete_entity(self, id: str) -> bool:
        pass
