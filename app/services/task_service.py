from app.exception.error import BadRequest, NotFound
from app.repositories.task_repository import TaskRepository, AsyncSession
from app.schemas.task import TaskRequest

class TaskService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = TaskRepository(db)
    
    async def create(self,task:TaskRequest,email: str):
        if not task.name or not task.task_status or not task.description:
            raise BadRequest("string is empty")
        async with self.repo.db.begin():
            return  await self.repo.create_task(task, email)
    
    async def get_task_by_id(self, id: int,email: str):
        task = await self.repo.get_by_id(id,email)
        if not task:
            raise NotFound(f"task id:{id} not found")
        return task
    
    async def get_task_all(self, email: str, role: str):
        return await self.repo.get_all(email,role)
    
    async def update_task(self, id: int, email: str, task: TaskRequest):
        async with self.repo.db.begin():
            updated_task = await self.repo.update_task_detail(id, email, task)
            
            if not updated_task:
                raise NotFound("Task not found or unauthorized")
                
            return updated_task

    async def delete_task_by_id(self, id: int, email: str):
        async with self.repo.db.begin():
            deleted_id = await self.repo.delete_task(id, email)
            
            if deleted_id is None:
                raise NotFound("Task not found or already deleted")
                
            return {"detail": "Task deleted successfully"}
