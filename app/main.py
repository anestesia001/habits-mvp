from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, reports
from app.database import Base, engine, get_db
from app.models import Habit, HabitEntry
from app.s3 import upload_report
from app.schemas import (
    HabitCreate,
    HabitEntryCreate,
    HabitEntryOut,
    HabitOut,
    HabitUpdate,
    S3UploadResult,
)

app = FastAPI(
    title="Habit Tracker API",
    description="Простой API для учёта привычек и выгрузки CSV-отчётов в AWS S3.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/habits", response_model=HabitOut, status_code=201)
def create_habit(
    data: HabitCreate,
    db: Session = Depends(get_db),
) -> Habit:
    return crud.create_habit(db, data)


@app.get("/habits", response_model=list[HabitOut])
def get_habits(db: Session = Depends(get_db)) -> list[Habit]:
    return crud.list_habits(db)


@app.get("/habits/{habit_id}", response_model=HabitOut)
def get_habit(habit_id: int, db: Session = Depends(get_db)) -> Habit:
    habit = crud.get_habit(db, habit_id)

    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit


@app.patch("/habits/{habit_id}", response_model=HabitOut)
def update_habit(
    habit_id: int,
    data: HabitUpdate,
    db: Session = Depends(get_db),
) -> Habit:
    habit = crud.get_habit(db, habit_id)

    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return crud.update_habit(db, habit, data)


@app.delete("/habits/{habit_id}", status_code=204)
def delete_habit(habit_id: int, db: Session = Depends(get_db)) -> None:
    habit = crud.get_habit(db, habit_id)

    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    crud.delete_habit(db, habit)


@app.post(
    "/habits/{habit_id}/entries",
    response_model=HabitEntryOut,
    status_code=201,
)
def create_or_update_entry(
    habit_id: int,
    data: HabitEntryCreate,
    db: Session = Depends(get_db),
) -> HabitEntry:
    habit = crud.get_habit(db, habit_id)

    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return crud.upsert_entry(db, habit, data)


@app.get("/habits/{habit_id}/entries", response_model=list[HabitEntryOut])
def get_entries(
    habit_id: int,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[HabitEntry]:
    habit = crud.get_habit(db, habit_id)

    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return crud.list_entries(db, habit_id, date_from, date_to)


@app.post("/reports/export", response_model=S3UploadResult)
def export_report(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> S3UploadResult:
    report_path: Path = reports.build_csv_report(db, date_from, date_to)

    timestamp = date.today().isoformat()
    object_key = (
        f"{reports.__name__}/{timestamp}-habits-report.csv"
        if False
        else f"habit-reports/{timestamp}-habits-report.csv"
    )

    try:
        location = upload_report(report_path, object_key)
    finally:
        report_path.unlink(missing_ok=True)

    return S3UploadResult(
        bucket="configured-in-settings",
        key=object_key,
        location=location,
    )