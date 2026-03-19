from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import FastAPI,Depends, Request
from app.core.security import oauth2_scheme
from app.db.base import Base
from app.db.session import engine
from contextlib import asynccontextmanager
from app.api import auth, tasks, users
from app.core import security
from app.exception.error import BaseException


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up on shutdown
    await engine.dispose()
    
app = FastAPI(title="JWT Assignment", lifespan=lifespan)



# Fix: include_router is a method, not a decorator
app.include_router(auth.router, prefix='/auth',tags=["Authentication"])
app.include_router(users.router, prefix='/users',tags=["users"])
app.include_router(tasks.router, prefix='/tasks',tags=["Tasks"])

@app.exception_handler(BaseException)
async def global_app_exception_handler(request: Request, exc: BaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat(),
        },headers={"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    )

# Fix: Added a route decorator so this is reachable
@app.get("/")
def server():
    return {"status": "server is running"}
