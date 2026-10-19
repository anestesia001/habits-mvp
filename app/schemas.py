from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    target_per_week: int = Field(default=7, ge=1, le=7)


class HabitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    target_per_week: int | None = Field(default=None, ge=1, le=7)


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    target_per_week: int
    created_at: datetime


class HabitEntryCreate(BaseModel):
    entry_date: date
    completed: bool = True
    note: str | None = None


class HabitEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    entry_date: date
    completed: bool
    note: str | None
    created_at: datetime


class S3UploadResult(BaseModel):
    bucket: str
    key: str
    location: str