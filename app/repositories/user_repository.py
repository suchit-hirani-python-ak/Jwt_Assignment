from sqlalchemy import select, update
from app.db.session import AsyncSession
from app.models.user import User
from app.models.token import TokenGeneration
class UserRepository:
    def __init__(self, db:AsyncSession):
        self.db = db

    
    async def list_all(self) -> list[User]:
        query = select(User)
        result =await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, id: int):
        query = select(User).where(User.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit() 
        await self.db.refresh(user) # Pulls the new ID back into the 'user' object
        return user
    
    async def update_token(self, user_id:int,token:str):
        query = update(TokenGeneration).where(TokenGeneration.user_id == user_id, TokenGeneration.is_used == False).values(is_used = True)
        await self.db.execute(query)
        
        new_token_entry = TokenGeneration(
            refresh_token=token,
            user_id=user_id,
            is_used=False
        )
        self.db.add(new_token_entry)
        
        await self.db.commit()
        return new_token_entry