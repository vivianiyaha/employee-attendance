from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///attendance.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    staff_id = Column(String, unique=True)
    name = Column(String)
    department = Column(String)
    shift = Column(String)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    staff_id = Column(String)
    name = Column(String)
    department = Column(String)
    date = Column(String)
    clock_in = Column(DateTime)
    clock_out = Column(DateTime)
    status = Column(String)
    hours_worked = Column(Float)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True)
    staff_id = Column(String)
    name = Column(String)
    leave_type = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    status = Column(String)


Base.metadata.create_all(bind=engine)
