from datetime import datetime

from database import Base
from sqlalchemy import Column, DateTime, Integer, String


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)
    preco = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)