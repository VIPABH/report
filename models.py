from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///allowed_users.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class AllowedUser(Base):
    __tablename__ = "allowed_users"
    user_id = Column(Integer, primary_key=True)
    added_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)
