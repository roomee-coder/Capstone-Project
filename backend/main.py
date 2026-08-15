import time
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from algorithms import insertion_sort, binary_search, linear_search
from quick_add import parse_task_description
import models
import schemas
from database import engine, get_db

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")

# ---------- Logging setup ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskflow")

# ---------- Middleware: request logging ----------
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time_ms = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} - {process_time_ms:.2f}ms")
    return response

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "null",  # allows file:// origin during local testing
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ==================== USERS ====================

@app.post("/users", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=422, detail="Email already registered")
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# ==================== PROJECTS ====================

@app.post("/projects", response_model=schemas.ProjectOut, status_code=201)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    owner = db.query(models.User).filter(models.User.id == project.owner_id).first()
    if not owner:
        raise HTTPException(status_code=422, detail="Owner (user) does not exist")
    db_project = models.Project(name=project.name, owner_id=project.owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@app.get("/projects", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()


@app.get("/projects/{project_id}/stats", response_model=schemas.ProjectStats)
def get_project_stats(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    counts = (
        db.query(models.Task.status, func.count(models.Task.id))
        .filter(models.Task.project_id == project_id)
        .group_by(models.Task.status)
        .all()
    )

    status_counts = {status: count for status, count in counts}
    total = sum(status_counts.values())

    return schemas.ProjectStats(
        project_id=project_id,
        total_tasks=total,
        pending=status_counts.get("pending", 0),
        in_progress=status_counts.get("in_progress", 0),
        completed=status_counts.get("completed", 0),
    )


# ==================== TASKS ====================

@app.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=422, detail="Project does not exist")

    db_task = models.Task(
        title=task.title,
        priority=task.priority,
        due_date=task.due_date,
        status=task.status or "pending",
        project_id=task.project_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task




@app.post("/tasks/quick-add", status_code=201)
def quick_add_task(payload: dict, db: Session = Depends(get_db)):
    description = payload.get("description")
    project_id = payload.get("project_id")

    if not description or not isinstance(description, str) or not description.strip():
        raise HTTPException(status_code=422, detail="description is required and must be a non-empty string")

    if project_id is None or not isinstance(project_id, int):
        raise HTTPException(status_code=422, detail="project_id is required and must be an integer")

    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=422, detail="project_id does not reference an existing project")

    parsed = parse_task_description(description)

    new_task = models.Task(
        title=parsed["title"],
        priority=parsed["priority"],
        due_date=parsed["due_date_hint"],
        status="pending",
        project_id=project_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# ==================== SORT & SEARCH (Section 2) ====================

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


@app.get("/tasks", response_model=None)
def list_tasks(sort: str = None, db: Session = Depends(get_db)):
    all_tasks = db.query(models.Task).all()

    if sort is None:
        return all_tasks

    task_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "due_date": t.due_date,
            "status": t.status,
            "project_id": t.project_id,
        }
        for t in all_tasks
    ]

    if sort == "priority":
        for task in task_dicts:
            task["_rank"] = PRIORITY_RANK.get(task["priority"], 0)
        insertion_sort(task_dicts, "_rank")
        for task in task_dicts:
            del task["_rank"]
    elif sort == "due_date":
        insertion_sort(task_dicts, "due_date")
    else:
        raise HTTPException(status_code=422, detail="sort must be 'priority' or 'due_date'")

    return task_dicts

@app.get("/tasks/search")
def search_tasks(title: str, algo: str = "binary", db: Session = Depends(get_db)):
    all_tasks = db.query(models.Task).all()
    index = [{"id": t.id, "title": t.title} for t in all_tasks]

    if algo == "binary":
        insertion_sort(index, "title")
        found_index = binary_search(index, title, "title")
    elif algo == "linear":
        found_index = linear_search(index, title, "title")
    else:
        raise HTTPException(status_code=422, detail="algo must be 'binary' or 'linear'")

    if found_index == -1:
        raise HTTPException(status_code=404, detail="No task found with that exact title")

    matched_id = index[found_index]["id"]
    task = db.query(models.Task).filter(models.Task.id == matched_id).first()
    return task

@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=200)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}



# ==================== ROOT ====================

@app.get("/")
def root():
    return {"message": "TaskFlow API is running"}