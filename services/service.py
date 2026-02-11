from typing import Generic, List, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

from core.setup import async_session_factory

M = TypeVar("M", bound=DeclarativeBase)
P = TypeVar("P", bound=BaseModel)


class Service(Generic[M, P]):
    def __init__(
        self,
        model: M,
        model_options: List,
        schema: P,
        schema_base: P,
        schema_update: P,
        rel_schema: P,
    ):
        self.model = model
        self.model_options = model_options
        self.schema = schema
        self.schema_base = schema_base
        self.schema_update = schema_update
        self.rel_schema = rel_schema

    async def create_obj(self, obj_data: BaseModel) -> P:
        async with async_session_factory() as session:
            new_obj = self.model(**obj_data.model_dump())  # type: ignore
            session.add(new_obj)

            await session.commit()
            await session.refresh(new_obj)

            return self.schema.model_validate(new_obj)

    async def get_by_id(self, obj_id: int) -> P:
        async with async_session_factory() as session:
            obj = await session.get(self.model, obj_id, options=self.model_options)  # type: ignore
            if obj is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No {self.model.__name__} with id ({obj_id}) found",
                )
            return self.rel_schema.model_validate(obj)

    async def get_all(self, offset: int, limit: int) -> List[P]:
        async with async_session_factory() as session:
            query = select(self.model).offset(offset).limit(limit)  # type: ignore
            res = await session.scalars(query)
            objs = res.all()
            return [self.schema.model_validate(obj) for obj in objs]

    async def delete_obj_by_id(self, obj_id: int) -> P:
        async with async_session_factory() as session:
            obj = await session.get(self.model, obj_id)  # type: ignore
            if obj is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No {self.model.__name__} with id ({obj_id}) found",
                )
            await session.delete(obj)
            await session.commit()

            return self.schema.model_validate(obj)

    async def change_obj(self, obj_data: P, obj_id: int) -> P:
        async with async_session_factory() as session:
            obj_to_change = await session.get(self.model, obj_id)  # type: ignore
            obj_data_dict = obj_data.model_dump(exclude_unset=True)

            for key, val in obj_data_dict.items():
                setattr(obj_to_change, key, val)

            await session.commit()
            await session.refresh(obj_to_change)

            return self.rel_schema.model_validate(obj_to_change)
