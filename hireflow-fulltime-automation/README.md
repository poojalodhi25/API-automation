# HireFlow Full-Time Automation

Web system for USA Full-Time / W2 / Direct Hire recruitment outreach.

This is **not** a LinkedIn scraper. HireFlow finds opportunities through public job APIs and sends email from Gmail.

## Modules

- Full-Time W2 & Direct Hire Recruiter Search
- USA Recruiter & Opportunity Filtering
- AI Resume Alignment
- Full-Time Job Requirement Matching
- Recruiter Outreach Preparation
- Gmail Automated Outreach
- Personalized Recruiter Communication
- Reply Detection
- Interested Recruiter Identification
- Follow-Up Opportunity Tracking
- Duplicate Email Prevention
- Outreach Analytics & Reporting

## Technology stack

- Python 3.10+
- FastAPI
- MySQL + SQLAlchemy
- HTML, CSS, JavaScript, Bootstrap
- requests / httpx
- python-dotenv
- Pydantic
- Gemini API
- Gmail API

## Run from VS Code (Windows)

1. Open this folder in VS Code / Cursor.
2. Double-click `start.bat` **or** open Terminal and run:

```powershell
cd C:\Users\MY\OneDrive\Desktop\Full-tim\hireflow-fulltime-automation
.\.venv\Scripts\python.exe run.py
```

If `.venv` is missing:

```powershell
uv venv --python 3.12 .venv
uv pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python.exe run.py
```

Do **not** click Run on a random file. Use `run.py` with the interpreter:

`C:\Users\MY\OneDrive\Desktop\Full-tim\hireflow-fulltime-automation\.venv\Scripts\python.exe`

## MySQL

```sql
CREATE DATABASE hireflow_fulltime CHARACTER SET utf8mb4;
```

Put your password in `.env` as `MYSQL_PASSWORD=...`. Tables are created when the app starts.

Job search still works if MySQL is off. Saving candidates / recruiters / emails needs MySQL.

## Test URLs

- Homepage: http://127.0.0.1:8000/
- Health: http://127.0.0.1:8000/api/health
- Job search API: POST http://127.0.0.1:8000/api/jobs/search

## Demo for internship video

1. Open http://127.0.0.1:8000/ and show the dashboard.
2. Search a role on `/search` (Arbeitnow works without a key).
3. Add your own email as a recruiter on `/recruiters`.
4. Add a candidate on `/candidates`.
5. Connect Gmail on `/settings`.
6. Send outreach on `/outreach`.
7. Open Gmail Sent and take screenshots.

## Screen recording on Windows

Press **Win + Alt + R** after the site is open in the browser. Video is saved under `Videos\Captures`.
