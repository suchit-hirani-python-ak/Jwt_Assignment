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
    """
    Create a new task for the authenticated user.

    Args:
        payload (TaskRequest): Task details provided by the user.
        db (AsyncSession): Database session dependency.
        current_user (TokenResponse): Authenticated user extracted from JWT.

    Returns:
        TaskResponse: Created task details.
    """
    return await TaskService(db).create(payload, current_user.sub)

@router.get("",response_model=list[TaskResponse])
async def all_task(db:Annotated[AsyncSession, Depends(get_db)],current_user: TokenResponse=Depends(get_current_user)):
    """
    Create a new task for the authenticated user.

    Args:
        payload (TaskRequest): Task details provided by the user.
        db (AsyncSession): Database session dependency.
        current_user (TokenResponse): Authenticated user extracted from JWT.

    Returns:
        TaskResponse: Created task details.
    """
    return await TaskService(db).get_task_all(current_user.sub,current_user.role)

@router.get("/{id}",response_model=TaskByIdResponse)
async def task_by_id(id: int, db:Annotated[AsyncSession, Depends(get_db)],
    current_user: TokenResponse=Depends(get_current_user)):
    """
    Retrieve a specific task by ID.

    Args:
        id (int): Task ID.
        db (AsyncSession): Database session.
        current_user (TokenResponse): Authenticated user.

    Returns:
        TaskByIdResponse: Task details.
    """
    return await TaskService(db).get_task_by_id(id, current_user.sub)



@router.put("/{id}", response_model=TaskUpdateStatus)
async def status_update(
    id: int, 
    task: TaskRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenResponse, Depends(get_current_user)]
):
    """update an existing task

    Args:
        id (int): Retrive Task Id
        task (TaskRequest): _description_
        db (Annotated[AsyncSession, Depends): _description_

    Returns:
        TaskUpdateStatus: Update task
    """
    return await TaskService(db).update_task(id, current_user.sub, task)

@router.delete("/{id}")
async def delete(id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenResponse, Depends(get_current_user)]
):
    """
    Delete a task by ID.

    Args:
        id (int): Task ID.
        db (AsyncSession): Database session.
        current_user (TokenResponse): Authenticated user.

    Returns:
        dict: Confirmation of deletion.
    """
    return await TaskService(db).delete_task_by_id(id,current_user.sub)

