import os
import json
from datetime import datetime, timedelta, date
from contextlib import asynccontextmanager
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import Session, SQLModel, select, create_engine, func
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
import resend

from models import HSEProgram, PROGRAM_TYPES

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hse_management.db")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
resend.api_key = RESEND_API_KEY

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Global scheduler reference
scheduler = BackgroundScheduler()


def get_session():
    with Session(engine) as session:
        yield session


# Pydantic models for request bodies
class ProgramUpdate(BaseModel):
    actual_date: datetime
    status: str
    wpts_number: str
    evidence_link: Optional[str] = None


class ProgramCreate(BaseModel):
    title: str
    program_type: Optional[str] = "hse_plan"
    planned_date: datetime
    pic_name: Optional[str] = None
    manager_email: Optional[str] = "ade.basirwfrd@gmail.com"


# Legacy Project Create (for frontend compatibility)
class LegacyProjectCreate(BaseModel):
    name: str
    title: Optional[str] = None
    category: Optional[str] = "other"
    well_name: Optional[str] = None
    kontrak_no: Optional[str] = None
    status: Optional[str] = "Upcoming"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    rig_down: Optional[str] = None
    assigned_to: Optional[str] = None
    pic_email: Optional[str] = None
    pic_manager_email: Optional[str] = None


class ProgramFullUpdate(BaseModel):
    title: Optional[str] = None
    program_type: Optional[str] = None
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    status: Optional[str] = None
    wpts_number: Optional[str] = None
    evidence_link: Optional[str] = None
    pic_name: Optional[str] = None
    manager_email: Optional[str] = None


def check_and_send_reminders():
    """Check for upcoming programs and send reminder emails."""
    with Session(engine) as session:
        today = date.today()

        # Logic 1: 1 Month Warning (exactly 30 days)
        one_month_date = today + timedelta(days=30)
        stmt1 = select(HSEProgram).where(
            HSEProgram.planned_date >= datetime.combine(one_month_date, datetime.min.time()),
            HSEProgram.planned_date < datetime.combine(one_month_date + timedelta(days=1), datetime.min.time())
        )
        programs_1m = session.exec(stmt1).all()

        for prog in programs_1m:
            send_email(
                prog.manager_email,
                f"Upcoming HSE Program: {prog.title} due in 1 Month",
                f"Reminder: The HSE program '{prog.title}' is scheduled for {prog.planned_date.strftime('%Y-%m-%d')}."
            )
            print(f"[REMINDER] Sent 1-month warning for: {prog.title}")

        # Logic 2: 2 Weeks Urgent Warning (exactly 14 days and not completed)
        two_weeks_date = today + timedelta(days=14)
        stmt2 = select(HSEProgram).where(
            HSEProgram.planned_date >= datetime.combine(two_weeks_date, datetime.min.time()),
            HSEProgram.planned_date < datetime.combine(two_weeks_date + timedelta(days=1), datetime.min.time()),
            HSEProgram.status != "Closed"
        )
        programs_2w = session.exec(stmt2).all()

        for prog in programs_2w:
            send_email(
                prog.manager_email,
                f"URGENT: HSE Program {prog.title} due in 2 Weeks!",
                f"URGENT: The HSE program '{prog.title}' is due on {prog.planned_date.strftime('%Y-%m-%d')} and is still pending."
            )
            print(f"[URGENT] Sent 2-week warning for: {prog.title}")


def send_email(to_email: str, subject: str, body: str):
    """Send email using Resend API."""
    if not RESEND_API_KEY:
        print(f"[EMAIL SKIPPED] No API key. Would send to {to_email}: {subject}")
        return

    try:
        params = {
            "from": "HSE System <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": f"<p>{body}</p>",
        }
        resend.Emails.send(params)
        print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    SQLModel.metadata.create_all(engine)
    print("[STARTUP] Database tables created")

    scheduler.add_job(
        check_and_send_reminders,
        'cron',
        hour=8,
        minute=0,
        id='daily_reminder_check'
    )
    scheduler.start()
    print("[STARTUP] Scheduler started - daily check at 08:00")

    yield

    # Shutdown
    scheduler.shutdown()
    print("[SHUTDOWN] Scheduler stopped")


app = FastAPI(
    title="HSE Plan Management System",
    description="API for managing HSE Programs with automated reminders",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def root():
    """Serve the main HTML page."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"status": "healthy", "service": "HSE Plan Management System", "version": "2.0.0"}


@app.get("/program-types")
def get_program_types():
    """Get available program types."""
    return PROGRAM_TYPES


@app.get("/statistics")
def get_statistics(session: Session = Depends(get_session)):
    """Get dashboard statistics."""
    total_programs = session.exec(select(func.count(HSEProgram.id))).one()
    completed = session.exec(
        select(func.count(HSEProgram.id)).where(HSEProgram.status == "Closed")
    ).one()
    pending = session.exec(
        select(func.count(HSEProgram.id)).where(HSEProgram.status != "Closed")
    ).one()
    
    now = datetime.now()
    first_of_month = datetime(now.year, now.month, 1)
    if now.month == 12:
        first_of_next = datetime(now.year + 1, 1, 1)
    else:
        first_of_next = datetime(now.year, now.month + 1, 1)
    
    this_month = session.exec(
        select(func.count(HSEProgram.id)).where(
            HSEProgram.planned_date >= first_of_month,
            HSEProgram.planned_date < first_of_next
        )
    ).one()
    
    upcoming = session.exec(
        select(func.count(HSEProgram.id)).where(
            HSEProgram.planned_date >= datetime.now(),
            HSEProgram.planned_date <= datetime.now() + timedelta(days=30),
            HSEProgram.status != "Closed"
        )
    ).one()
    
    by_type = {}
    for ptype in PROGRAM_TYPES.keys():
        count = session.exec(
            select(func.count(HSEProgram.id)).where(HSEProgram.program_type == ptype)
        ).one()
        by_type[ptype] = count
    
    completion_rate = (completed / total_programs * 100) if total_programs > 0 else 0.0
    
    return {
        "total_programs": total_programs,
        "completed": completed,
        "pending": pending,
        "this_month": this_month,
        "upcoming": upcoming,
        "completion_rate": round(completion_rate, 1),
        "by_type": by_type,
    }


@app.get("/programs", response_model=List[HSEProgram])
def get_programs(
    program_type: Optional[str] = Query(None, description="Filter by program type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    session: Session = Depends(get_session)
):
    """Get all HSE programs with optional filters."""
    query = select(HSEProgram)
    
    if program_type:
        query = query.where(HSEProgram.program_type == program_type)
    if status:
        query = query.where(HSEProgram.status == status)
    
    return session.exec(query.order_by(HSEProgram.planned_date)).all()


# ===== LEGACY API ENDPOINTS (for frontend compatibility) =====

@app.get("/projects")
def get_projects(session: Session = Depends(get_session)):
    """Legacy endpoint: Get all programs as 'projects'."""
    programs = session.exec(select(HSEProgram).order_by(HSEProgram.planned_date)).all()
    # Transform to legacy project format
    return [
        {
            "id": p.id,
            "name": p.title,
            "title": p.title,
            "status": p.status if p.status != "pending" else "Upcoming",
            "start_date": p.planned_date.strftime("%Y-%m-%d") if p.planned_date else None,
            "end_date": p.actual_date.strftime("%Y-%m-%d") if p.actual_date else None,
            "rig_down": p.actual_date.strftime("%Y-%m-%d") if p.actual_date else None,
            "category": p.program_type,
            "well_name": "",
            "kontrak_no": "",
            "assigned_to": p.pic_name or "",
            "pic_email": p.manager_email,
        }
        for p in programs
    ]


@app.post("/projects")
def create_project(project: LegacyProjectCreate, session: Session = Depends(get_session)):
    """Legacy endpoint: Create a new program from frontend 'project' form."""
    # Map legacy project to HSE Program
    planned_date = datetime.now()
    if project.start_date:
        try:
            planned_date = datetime.strptime(project.start_date, "%Y-%m-%d")
        except:
            pass
    
    # Map category to program_type
    category_map = {
        "hse-training": "safety_training",
        "emergency-drill": "hse_plan",
        "observation-card": "inspection",
        "safety-meeting": "hse_committee",
        "inspection": "inspection",
        "other": "hse_plan",
    }
    program_type = category_map.get(project.category, "hse_plan")
    
    # Map status
    status_map = {
        "Upcoming": "pending",
        "InProgress": "pending",
        "Completed": "Closed",
        "OnHold": "pending",
        "Canceled": "Closed",
    }
    status = status_map.get(project.status, "pending")
    
    db_program = HSEProgram(
        title=project.name,
        program_type=program_type,
        planned_date=planned_date,
        status=status,
        pic_name=project.assigned_to,
        manager_email=project.pic_email or "ade.basirwfrd@gmail.com",
        created_at=datetime.utcnow()
    )
    session.add(db_program)
    session.commit()
    session.refresh(db_program)
    
    return {
        "id": db_program.id,
        "name": db_program.title,
        "status": project.status,
        "message": "HSE Program created successfully"
    }


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_session)):
    """Legacy endpoint: Delete a program."""
    program = session.get(HSEProgram, project_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    session.delete(program)
    session.commit()
    return {"message": "Program deleted successfully"}


@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    """Legacy endpoint: Return all tasks."""
    return tasks_storage


# In-memory task storage (simple approach for now)
tasks_storage = []
task_id_counter = 1


class TaskCreate(BaseModel):
    project_id: str
    code: str
    title: str
    implementation_date: Optional[str] = None
    frequency: Optional[str] = "once"
    pic_name: Optional[str] = None
    pic_email: Optional[str] = None
    status: Optional[str] = "Upcoming"


@app.post("/tasks")
def create_task(task: TaskCreate):
    """Create a new task."""
    global task_id_counter
    new_task = {
        "id": str(task_id_counter),
        "project_id": task.project_id,
        "code": task.code,
        "title": task.title,
        "implementation_date": task.implementation_date,
        "frequency": task.frequency,
        "pic_name": task.pic_name,
        "pic_email": task.pic_email,
        "status": task.status,
        "attachments": []
    }
    tasks_storage.append(new_task)
    task_id_counter += 1
    return new_task


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    wpts_id: Optional[str] = None


@app.put("/tasks/{task_id}")
def update_task(task_id: str, task_update: TaskUpdate):
    """Update an existing task."""
    for task in tasks_storage:
        if task["id"] == task_id:
            if task_update.status:
                task["status"] = task_update.status
            if task_update.wpts_id is not None:
                task["wpts_id"] = task_update.wpts_id
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/schedules")
def get_schedules(session: Session = Depends(get_session)):
    """Legacy endpoint: Get programs as schedules."""
    programs = session.exec(select(HSEProgram).order_by(HSEProgram.planned_date)).all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "type": p.program_type,
            "date": p.planned_date.strftime("%Y-%m-%d") if p.planned_date else None,
            "status": p.status,
        }
        for p in programs
    ]


# ===== END LEGACY ENDPOINTS =====


@app.post("/programs", response_model=HSEProgram)
def create_program(program: ProgramCreate, session: Session = Depends(get_session)):
    """Create a new HSE program."""
    db_program = HSEProgram(
        title=program.title,
        program_type=program.program_type,
        planned_date=program.planned_date,
        pic_name=program.pic_name,
        manager_email=program.manager_email,
        created_at=datetime.utcnow()
    )
    session.add(db_program)
    session.commit()
    session.refresh(db_program)
    return db_program


@app.get("/programs/{program_id}", response_model=HSEProgram)
def get_program(program_id: int, session: Session = Depends(get_session)):
    """Get a specific HSE program by ID."""
    program = session.get(HSEProgram, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


@app.post("/update-program/{program_id}", response_model=HSEProgram)
def update_program_status(
    program_id: int,
    update_data: ProgramUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing HSE program status."""
    program = session.get(HSEProgram, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    if not update_data.wpts_number:
        raise HTTPException(status_code=400, detail="WPTS Number is required")

    program.actual_date = update_data.actual_date
    program.status = update_data.status
    program.wpts_number = update_data.wpts_number
    program.evidence_link = update_data.evidence_link

    session.add(program)
    session.commit()
    session.refresh(program)
    return program


@app.put("/programs/{program_id}", response_model=HSEProgram)
def update_program_full(
    program_id: int,
    update_data: ProgramFullUpdate,
    session: Session = Depends(get_session)
):
    """Full update of an HSE program."""
    program = session.get(HSEProgram, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(program, key, value)

    session.add(program)
    session.commit()
    session.refresh(program)
    return program


@app.delete("/programs/{program_id}")
def delete_program(program_id: int, session: Session = Depends(get_session)):
    """Delete an HSE program."""
    program = session.get(HSEProgram, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    session.delete(program)
    session.commit()
    return {"message": "Program deleted successfully"}




# ===== KPI DATA PERSISTENCE =====
KPI_DATA_FILE = Path(__file__).parent / "data" / "kpi_data.json"

def load_kpi_data():
    """Load KPI data from JSON file."""
    if KPI_DATA_FILE.exists():
        with open(KPI_DATA_FILE, 'r') as f:
            return json.load(f)
    return {"man_hours": {}, "kpi": {}}

def save_kpi_data(data):
    """Save KPI data to JSON file."""
    KPI_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(KPI_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@app.get("/kpi")
def get_kpi_data():
    """Get all KPI data."""
    return load_kpi_data()


class KPIYearUpdate(BaseModel):
    man_hours: Optional[float] = None
    fatality_target: Optional[float] = None
    fatality_result: Optional[float] = None
    trir_target: Optional[float] = None
    trir_result: Optional[float] = None
    pvir_target: Optional[float] = None
    pvir_result: Optional[float] = None
    environment_target: Optional[float] = None
    environment_result: Optional[float] = None
    fire_target: Optional[float] = None
    fire_result: Optional[float] = None
    firstaid_target: Optional[float] = None
    firstaid_result: Optional[float] = None
    occupational_target: Optional[float] = None
    occupational_result: Optional[float] = None


@app.put("/kpi/{year}")
def update_kpi_year(year: str, update: KPIYearUpdate):
    """Update KPI data for a specific year."""
    data = load_kpi_data()
    
    if year not in data["kpi"]:
        data["kpi"][year] = {}
    if year not in data["man_hours"]:
        data["man_hours"][year] = 0
    
    if update.man_hours is not None:
        data["man_hours"][year] = update.man_hours
    
    metrics = ["fatality", "trir", "pvir", "environment", "fire", "firstaid", "occupational"]
    for metric in metrics:
        if metric not in data["kpi"][year]:
            data["kpi"][year][metric] = {"target": 0, "result": 0}
        
        target_attr = f"{metric}_target"
        result_attr = f"{metric}_result"
        
        if getattr(update, target_attr, None) is not None:
            data["kpi"][year][metric]["target"] = getattr(update, target_attr)
        if getattr(update, result_attr, None) is not None:
            data["kpi"][year][metric]["result"] = getattr(update, result_attr)
    
    save_kpi_data(data)
    return {"message": f"KPI data for {year} updated successfully", "data": data}



# ===== LL INDICATOR DATA PERSISTENCE =====
LL_DATA_FILE = Path(__file__).parent / "data" / "ll_indicator.json"

def load_ll_data():
    """Load LL Indicator data from JSON file."""
    if LL_DATA_FILE.exists():
        with open(LL_DATA_FILE, 'r') as f:
            return json.load(f)
    return {"year": 2025, "lagging": [], "leading": []}

def save_ll_data(data):
    """Save LL Indicator data to JSON file."""
    LL_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LL_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@app.get("/ll-indicator")
def get_ll_indicator():
    """Get all LL Indicator data."""
    return load_ll_data()


class LLIndicatorUpdate(BaseModel):
    indicator_type: str  # "lagging" or "leading"
    indicator_id: int
    target: Optional[str] = None
    actual: Optional[str] = None


@app.put("/ll-indicator")
def update_ll_indicator(update: LLIndicatorUpdate):
    """Update a specific LL indicator."""
    data = load_ll_data()
    
    indicators = data.get(update.indicator_type, [])
    for ind in indicators:
        if ind.get("id") == update.indicator_id:
            if update.target is not None:
                ind["target"] = update.target
            if update.actual is not None:
                ind["actual"] = update.actual
            break
    
    save_ll_data(data)
    return {"message": f"LL Indicator updated successfully", "data": data}


@app.put("/ll-indicator/year")
def update_ll_year(year: int):
    """Update the LL Indicator year."""
    data = load_ll_data()
    data["year"] = year
    save_ll_data(data)


# ===== OTP DATA PERSISTENCE =====
OTP_DATA_FILE = Path(__file__).parent / "data" / "otp_data.json"

def load_otp_data():
    """Load OTP data from JSON file."""
    if OTP_DATA_FILE.exists():
        with open(OTP_DATA_FILE, 'r') as f:
            return json.load(f)
    return {"year": 2026, "programs": []}

def save_otp_data(data):
    """Save OTP data to JSON file."""
    OTP_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OTP_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_progress(program):
    """Calculate progress percentage for an OTP program."""
    total_plan = 0
    total_actual = 0
    for month_data in program.get("months", {}).values():
        total_plan += month_data.get("plan", 0)
        total_actual += month_data.get("actual", 0)
    if total_plan == 0:
        return 100 if total_actual >= 0 else 0
    return min(100, round((total_actual / total_plan) * 100))


@app.get("/otp")
def get_otp_data():
    """Get all OTP data."""
    data = load_otp_data()
    # Calculate progress for each program
    for prog in data.get("programs", []):
        prog["progress"] = calculate_progress(prog)
    return data


@app.get("/otp/{program_id}")
def get_otp_program(program_id: int):
    """Get a specific OTP program by ID."""
    data = load_otp_data()
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            prog["progress"] = calculate_progress(prog)
            return prog
    raise HTTPException(status_code=404, detail="OTP program not found")


class OTPMonthUpdate(BaseModel):
    plan: Optional[int] = None
    actual: Optional[int] = None
    wpts_id: Optional[str] = None


@app.put("/otp/{program_id}/month/{month}")
def update_otp_month(program_id: int, month: str, update: OTPMonthUpdate):
    """Update Plan/Actual values for a specific month of an OTP program."""
    valid_months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    if month.lower() not in valid_months:
        raise HTTPException(status_code=400, detail=f"Invalid month. Must be one of: {valid_months}")
    
    data = load_otp_data()
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            if "months" not in prog:
                prog["months"] = {}
            if month.lower() not in prog["months"]:
                prog["months"][month.lower()] = {"plan": 0, "actual": 0}
            
            if update.plan is not None:
                prog["months"][month.lower()]["plan"] = update.plan
            if update.actual is not None:
                prog["months"][month.lower()]["actual"] = update.actual
            if update.wpts_id is not None:
                prog["months"][month.lower()]["wpts_id"] = update.wpts_id
            
            prog["progress"] = calculate_progress(prog)
            save_otp_data(data)
            return {"message": f"OTP program {program_id} month {month} updated", "program": prog}
    
    raise HTTPException(status_code=404, detail="OTP program not found")


class OTPProgramCreate(BaseModel):
    name: str
    plan_type: Optional[str] = "Annually"
    due_date: Optional[str] = None


@app.post("/otp")
def create_otp_program(program: OTPProgramCreate):
    """Create a new OTP program."""
    data = load_otp_data()
    
    # Generate new ID
    max_id = max([p.get("id", 0) for p in data.get("programs", [])], default=0)
    new_id = max_id + 1
    
    new_program = {
        "id": new_id,
        "name": program.name,
        "plan_type": program.plan_type,
        "due_date": program.due_date,
        "months": {
            "jan": {"plan": 0, "actual": 0},
            "feb": {"plan": 0, "actual": 0},
            "mar": {"plan": 0, "actual": 0},
            "apr": {"plan": 0, "actual": 0},
            "may": {"plan": 0, "actual": 0},
            "jun": {"plan": 0, "actual": 0},
            "jul": {"plan": 0, "actual": 0},
            "aug": {"plan": 0, "actual": 0},
            "sep": {"plan": 0, "actual": 0},
            "oct": {"plan": 0, "actual": 0},
            "nov": {"plan": 0, "actual": 0},
            "dec": {"plan": 0, "actual": 0}
        },
        "progress": 0
    }
    
    data["programs"].append(new_program)
    save_otp_data(data)
    return {"message": "OTP program created successfully", "program": new_program}


class OTPProgramUpdate(BaseModel):
    name: Optional[str] = None
    plan_type: Optional[str] = None
    due_date: Optional[str] = None


@app.put("/otp/{program_id}")
def update_otp_program(program_id: int, update: OTPProgramUpdate):
    """Update an OTP program's metadata."""
    data = load_otp_data()
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            if update.name is not None:
                prog["name"] = update.name
            if update.plan_type is not None:
                prog["plan_type"] = update.plan_type
            if update.due_date is not None:
                prog["due_date"] = update.due_date
            
            save_otp_data(data)
            return {"message": f"OTP program {program_id} updated", "program": prog}
    
    raise HTTPException(status_code=404, detail="OTP program not found")


@app.delete("/otp/{program_id}")
def delete_otp_program(program_id: int):
    """Delete an OTP program."""
    data = load_otp_data()
    original_count = len(data.get("programs", []))
    data["programs"] = [p for p in data.get("programs", []) if p.get("id") != program_id]
    
    if len(data["programs"]) == original_count:
        raise HTTPException(status_code=404, detail="OTP program not found")
    
    save_otp_data(data)
    return {"message": f"OTP program {program_id} deleted successfully"}


@app.put("/otp/year/{year}")
def update_otp_year(year: int):
    """Update the OTP year."""
    data = load_otp_data()
    data["year"] = year
    save_otp_data(data)
    return {"message": f"OTP year updated to {year}"}


@app.post("/test-reminder")
def test_reminder():
    """Manually trigger reminder check (for testing)."""
    check_and_send_reminders()
    return {"message": "Reminder check executed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

