from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from .db import Base

Base = declarative_base()

class Api(Base):
    __tablename__ = 'apis'
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True)
    method = Column(String)
    response_json = Column(Text)
    status_code = Column(Integer, default=200)
    enabled = Column(Boolean, default=True)
    quota = Column(Integer, default=0)
    quota_period = Column(String, default='hour')
    delay_ms = Column(Integer, default=0)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)

class ApiLog(Base):
    __tablename__ = 'api_logs'
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer)
    timestamp = Column(DateTime)
    status_code = Column(Integer)
    ip = Column(String)
    latency_ms = Column(Integer)

class MetadidomiCloudDatabaseData(Base):
    __tablename__ = 'metadidomi_cloud_database_data'
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Text)

class CloudDatabaseRule(Base):
    __tablename__ = 'cloud_database_rules'
    id = Column(Integer, primary_key=True, index=True)
    collection = Column(String, index=True)
    create = Column(String, default="Utilisateur connecté")
    read = Column(String, default="Utilisateur connecté")
    write = Column(String, default="Utilisateur connecté")
    delete = Column(String, default="Utilisateur connecté")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    created = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    uid = Column(String, unique=True, nullable=True)
    disabled = Column(Boolean, default=False)
