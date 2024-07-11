from typing import Type, Union

from beanie import Document

from database.interfaces.database_interface import DatabaseInterface


class MongoDatabase(DatabaseInterface):
    def __init__(self, collection: Type[Document]):
        self.collection = collection

    async def add_entity(self, entity: Document) -> Document:
        return await entity.create()

    async def add_entities(self, entities: list) -> list:
        return await self.collection.insert_many(entities)

    async def get_entity(self, id: str) -> Document:
        return await self.collection.get(id)

    async def get_all_entities(self) -> Union[bool, Document]:
        return await self.collection.all().to_list()

    async def get_entities_by_key(self, key: str, id: str) -> Union[bool, Document]:
        return await self.collection.find({key: id}).to_list()

    async def update_entity(
        self,
        id: str,
        data: dict,
    ) -> Union[bool, Document]:

        des_body = {k: v for k, v in data.items() if v is not None}
        update_query = {"$set": {field: value for field, value in des_body.items()}}
        entity = await self.collection.get(id)
        if entity:
            await entity.update(update_query)
            return entity
        return False

    async def delete_entity(self, id: str) -> bool:
        entity = await self.get_entity(id)
        if entity:
            await entity.delete()
            return True
        return False
