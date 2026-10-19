import csv
import tempfile
from datetime import date
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Habit, HabitEntry


def build_csv_report(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Path:
    query = (
        select(Habit, HabitEntry)
        .join(HabitEntry, HabitEntry.habit_id == Habit.id)
        .order_by(Habit.id, HabitEntry.entry_date)
    )

    if date_from:
        query = query.where(HabitEntry.entry_date >= date_from)

    if date_to:
        query = query.where(HabitEntry.entry_date <= date_to)

    rows = db.execute(query).all()

    tmp_file = tempfile.NamedTemporaryFile(
        mode="w",
        newline="",
        suffix=".csv",
        delete=False,
        encoding="utf-8",
    )

    with tmp_file:
        writer = csv.writer(tmp_file)
        writer.writerow(
            [
                "habit_id",
                "habit_name",
                "target_per_week",
                "entry_date",
                "completed",
                "note",
            ]
        )

        for habit, entry in rows:
            writer.writerow(
                [
                    habit.id,
                    habit.name,
                    habit.target_per_week,
                    entry.entry_date.isoformat(),
                    entry.completed,
                    entry.note or "",
                ]
            )

    return Path(tmp_file.name)