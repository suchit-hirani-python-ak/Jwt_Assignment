from sqlalchemy import select,update, delete
from app.models.task import Task
from app.db.session import AsyncSession
from app.schemas.task import TaskRequest

class TaskRepository:
    def __init__(self,db: AsyncSession) -> None:
        self.db = db
        
    async def create_task(self,task:TaskRequest, email: str) -> Task:
        task_data = task.model_dump()
        task_data["email"] = email
        new_task = Task(**task_data)
        self.db.add(new_task)
        await self.db.flush()
        await self.db.refresh(new_task)
        return new_task
    
    async def get_by_id(self,id: int, email: str):
        query = select(Task).where(Task.id == id, Task.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()
        
    async def get_all(self, email: str, role: str):
        query = select(Task)
        
        # If not admin, restrict by email
        if role != "admin":
            query = query.where(Task.email == email)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    

    async def update_task_detail(self, id: int, email: str, task: TaskRequest):
        task_data = task.model_dump(exclude_unset=True)
        query = (
            update(Task)
            .where(Task.id == id, Task.email == email)
            .values(**task_data)
            .returning(Task)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_task(self,id:int, email: str):
        query = delete(Task).where(Task.id == id, Task.email == email).returning(Task.id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()