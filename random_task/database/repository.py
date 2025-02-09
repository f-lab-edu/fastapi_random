from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from database.orm import User

class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.username == username)
        )

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()
        self.session.refresh(instance=user)
        return user

    def get_all_users(self) -> List[User]:
        return list(self.session.scalars(select(User))) 