"""This module provides a base service for CRUD operations on a model."""
from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
LoadSchemaType = TypeVar("LoadSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseModelService(Generic[ModelType, CreateSchemaType, LoadSchemaType, UpdateSchemaType]):
    """A base class for model services that provides CRUD operations.

    This class is generic and can be used with any model and schema types.
    """
    def __init__(self, model: Type[ModelType], create_schema: Type[CreateSchemaType], load_schema: Type[LoadSchemaType], update_schema: Type[UpdateSchemaType]):
        """Initializes the BaseModelService.

        Args:
            model: The model type.
            create_schema: The create schema type.
            load_schema: The load schema type.
            update_schema: The update schema type.
        """
        self.model = model
        self.create_schema = create_schema
        self.load_schema = load_schema
        self.update_schema = update_schema

    async def load(self, session: AsyncSession, id: int) -> LoadSchemaType | None:
        """Loads a model instance by its ID.

        Args:
            session: The database session.
            id: The ID of the model instance to load.

        Returns:
            The loaded model instance as a load schema, or None if not found.
        """
        result = await session.execute(select(self.model).where(self.model.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return self.load_schema.from_orm(db_obj)
        return None

    async def create(self, session: AsyncSession, obj_in: CreateSchemaType) -> LoadSchemaType:
        """Creates a new model instance.

        Args:
            session: The database session.
            obj_in: The create schema with the data for the new model instance.

        Returns:
            The created model instance as a load schema.

        Raises:
            IntegrityError: If the new model instance violates a database constraint.
        """
        obj = self.model(**obj_in.model_dump())
        session.add(obj)
        try:
            await session.flush()
            await session.commit()
            await session.refresh(obj)
            return self.load_schema.from_orm(obj)
        except IntegrityError as e:
            await session.rollback()
            raise e

    async def update(self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType) -> LoadSchemaType:
        """Updates a model instance.

        Args:
            session: The database session.
            db_obj: The model instance to update.
            obj_in: The update schema with the new data.

        Returns:
            The updated model instance as a load schema.
        """
        result = await session.execute(select(self.model).where(self.model.id == db_obj.id))
        db_obj = result.scalar_one_or_none()

        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return self.load_schema.from_orm(db_obj)

    async def delete(self, session: AsyncSession, db_obj: ModelType) -> None:
        """Deletes a model instance.

        Args:
            session: The database session.
            db_obj: The model instance to delete.
        """
        result = await session.execute(select(self.model).where(self.model.id == db_obj.id))
        db_obj = result.scalar_one_or_none()
        await session.delete(db_obj)
        await session.commit()