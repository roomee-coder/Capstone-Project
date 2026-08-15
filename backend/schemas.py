from pydantic import BaseModel, Field, validator
from typing import Optional


# ---------- Task Schemas ----------

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    priority: str = Field(default="medium")
    due_date: Optional[str] = None
    status: Optional[str] = "pending"

    @validator("title")
    def title_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip()

    @validator("priority")
    def priority_must_be_valid(cls, v):
        allowed = {"low", "medium", "high"}
        if v not in allowed:
            raise ValueError(f"Priority must be one of {allowed}")
        return v


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None

    @validator("title")
    def title_not_blank(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip() if v else v


class TaskOut(TaskBase):
    id: int
    project_id: int

    class Config:
        orm_mode = True


# ---------- Project Schemas ----------

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1)


class ProjectCreate(ProjectBase):
    owner_id: int


class ProjectOut(ProjectBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# ---------- User Schemas ----------

class UserBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# ---------- Stats Schema ----------

class ProjectStats(BaseModel):
    project_id: int
    total_tasks: int
    pending: int
    in_progress: int
    completed: int