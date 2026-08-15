# TaskFlow API

A task management API built with FastAPI and SQLAlchemy.

## Features
- CRUD operations for Projects and Tasks
- Project statistics endpoint (pending/in_progress/completed counts)
- CORS-enabled for frontend integration

## Running locally
1. Create a virtual environment and install dependencies from `requirements.txt`
2. Run `uvicorn main:app --reload`
3. Visit `http://127.0.0.1:8000/docs` for interactive API docs