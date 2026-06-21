from typing import Generic, Type, TypeVar, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    Abstract Base Repository implementing generic Async CRUD operations.
    Follows Data Access Object (DAO) pattern to encapsulate database interactions.
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Retrieves a database record by its Primary Key.
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Retrieves multiple records with offset pagination.
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, db_obj: ModelType) -> ModelType:
        """
        Saves a new object instance in the current transaction.
        Performs a flush to populate auto-generated IDs without committing.
        """
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: Any) -> ModelType:
        """
        Updates an existing database record dynamically from a dictionary or schema.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Handles Pydantic models (v2 model_dump)
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in.__dict__
            
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def delete(self, db: AsyncSession, *, db_obj: ModelType) -> ModelType:
        """
        Deletes a record from the database.
        """
        await db.delete(db_obj)
        await db.flush()
        return db_obj
