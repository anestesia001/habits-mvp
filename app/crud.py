from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Habit, HabitEntry
from app.schemas import HabitCreate, HabitEntryCreate, HabitUpdate


def create_habit(db: Session, data: HabitCreate) -> Habit:
    habit = Habit(**data.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def list_habits(db: Session) -> list[Habit]:
    return list(db.scalars(select(Habit).order_by(Habit.id)).all())


def get_habit(db: Session, habit_id: int) -> Habit | None:
    return db.get(Habit, habit_id)


def update_habit(db: Session, habit: Habit, data: HabitUpdate) -> Habit:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)
    return habit


def delete_habit(db: Session, habit: Habit) -> None:
    db.delete(habit)
    db.commit()


def upsert_entry(
    db: Session,
    habit: Habit,
    data: HabitEntryCreate,
) -> HabitEntry:
    entry = db.scalar(
        select(HabitEntry).where(
            HabitEntry.habit_id == habit.id,
            HabitEntry.entry_date == data.entry_date,
        )
    )

    if entry is None:
        entry = HabitEntry(
            habit_id=habit.id,
            entry_date=data.entry_date,
            completed=data.completed,
            note=data.note,
        )
        db.add(entry)
    else:
        entry.completed = data.completed
        entry.note = data.note

    db.commit()
    db.refresh(entry)
    return entry


def list_entries(
    db: Session,
    habit_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[HabitEntry]:
    query = select(HabitEntry).where(HabitEntry.habit_id == habit_id)

    if date_from:
        query = query.where(HabitEntry.entry_date >= date_from)

    if date_to:
        query = query.where(HabitEntry.entry_date <= date_to)

    return list(
        db.scalars(query.order_by(HabitEntry.entry_date.desc())).all()
    )