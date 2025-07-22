from sqlalchemy import Column, Text, Integer
from src.database.engine import Base
from src.database.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    email = Column(Text, unique=True, index=True, nullable=False)
    cognito_sub = Column(Text, unique=True, index=True, nullable=False)
    password = Column(Text, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
