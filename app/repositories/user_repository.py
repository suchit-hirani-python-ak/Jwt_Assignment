from app.db.session import AsyncSession
from app.models.user import User
from sqlalchemy import select
class UserRepository:
    def __init__(self, db:AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User:
        return await self.db.get(User,user_id)
    
    async def list_all(self) -> list[User]:
        query = select(User)
        result =await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self,obj:User) -> User:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
        