from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskResponse, TaskRequest, TaskByIdResponse, TaskUpdateStatus
from app.schemas.token import TokenResponse
from app.services.task_service import TaskService, AsyncSession
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from typing import Annotated
from fastapi import Body

router = APIRouter()

@router.post("", response_model=TaskResponse)
async def create_task(
    payload: TaskRequest, 
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: TokenResponse = Depends(get_current_user) # Injected from Header
):
    # Pass the ID extracted from the SECURE token payload
    # Assuming 'sub' holds your user_id string/int
    return await TaskService(db).create(payload, current_user.sub)

@router.get("",response_model=list[TaskResponse])
async def all_task(db:Annotated[AsyncSession, Depends(get_db)],current_user: TokenResponse=Depends(get_current_user)):
    return await TaskService(db).get_task_all(current_user.sub,current_user.role)

@router.get("/{id}",response_model=TaskByIdResponse)
async def task_by_id(id: int, db:Annotated[AsyncSession, Depends(get_db)],current_user: TokenResponse=Depends(get_current_user)):
    return await TaskService(db).get_task_by_id(id, current_user.sub)



@router.put("/{id}", response_model=TaskUpdateStatus)
async def status_update(
    id: int, 
    task: TaskRequest,  # Move this up! (No default value)
    db: Annotated[AsyncSession, Depends(get_db)], # Has default value
    current_user: TokenResponse = Depends(get_current_user) # Has default value
):
    return await TaskService(db).update_task(id, current_user.sub, task)

@router.delete("/{id}")
async def delete(id: int,
                 # Move this up! (No default value)
    db: Annotated[AsyncSession, Depends(get_db)], # Has default value
    current_user: TokenResponse = Depends(get_current_user) # Has default value
):
    return await TaskService(db).delete_task_by_id(id,current_user.sub)

