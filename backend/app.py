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


def generate_reminder_email_html(days_remaining: int, program_name: str, source: str, plan_date: str, month: str, pic_name: str) -> str:
    """Generate modern HTML email template for reminders."""
    urgency_color = "#dc3545" if days_remaining <= 7 else "#ffc107"
    urgency_text = "⚠️ URGENT" if days_remaining <= 7 else "🔔 Reminder"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <div style="background: linear-gradient(135deg, #e50914, #b20710); padding: 30px; text-align: center;">
      <h1 style="color: white; margin: 0; font-size: 24px;">🔔 HSE Program Reminder</h1>
      <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">Automated Notification</p>
    </div>
    <div style="padding: 30px;">
      <div style="background: {urgency_color}22; border-left: 4px solid {urgency_color}; padding: 15px; margin: 0 0 20px 0; border-radius: 4px;">
        <strong style="color: {urgency_color};">{urgency_text}: {days_remaining} Days Remaining</strong>
        <p style="margin: 8px 0 0 0; color: #666;">The following HSE program requires your attention.</p>
      </div>
      <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <p style="margin: 8px 0;"><span style="font-weight: 600; color: #666; display: inline-block; width: 100px;">Program:</span> <span style="color: #333; font-weight: 600;">{program_name}</span></p>
        <p style="margin: 8px 0;"><span style="font-weight: 600; color: #666; display: inline-block; width: 100px;">Source:</span> <span style="color: #333;">{source}</span></p>
        <p style="margin: 8px 0;"><span style="font-weight: 600; color: #666; display: inline-block; width: 100px;">Plan Date:</span> <span style="color: #e50914; font-weight: 600;">{plan_date}</span></p>
        <p style="margin: 8px 0;"><span style="font-weight: 600; color: #666; display: inline-block; width: 100px;">Month:</span> <span style="color: #333;">{month.upper()}</span></p>
        <p style="margin: 8px 0;"><span style="font-weight: 600; color: #666; display: inline-block; width: 100px;">PIC:</span> <span style="color: #333;">{pic_name}</span></p>
      </div>
      <p style="color: #555; line-height: 1.6;">Please ensure all preparations are on track for this program. If you have any questions or need to reschedule, please contact your HSE coordinator.</p>
      <div style="text-align: center; margin-top: 30px;">
        <a href="#" style="display: inline-block; background: linear-gradient(135deg, #e50914, #b20710); color: white; padding: 12px 30px; border-radius: 6px; text-decoration: none; font-weight: 600;">View in HSE System</a>
      </div>
    </div>
    <div style="background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #eee;">
      <p style="margin: 0;">HSE Management System | Automated Reminder</p>
      <p style="margin: 8px 0 0 0; color: #999;">This is an automated message. Please do not reply directly.</p>
    </div>
  </div>
</body>
</html>
"""


def send_email(to_email: str, subject: str, html_body: str):
    """Send email using Resend API."""
    if not to_email or not to_email.strip():
        print(f"[EMAIL SKIPPED] No email address provided for: {subject}")
        return False
        
    if not RESEND_API_KEY:
        print(f"[EMAIL SKIPPED] No API key. Would send to {to_email}: {subject}")
        return False

    try:
        params = {
            "from": "HSE System <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        resend.Emails.send(params)
        print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")
        return False


def check_otp_matrix_reminders():
    """Check OTP and Matrix data for upcoming plan_dates and send reminders."""
    today = date.today()
    two_weeks = today + timedelta(days=14)
    one_week = today + timedelta(days=7)
    
    two_weeks_str = two_weeks.strftime("%Y-%m-%d")
    one_week_str = one_week.strftime("%Y-%m-%d")
    
    data_dir = Path(__file__).parent / "data"
    reminders_sent = 0
    
    # Define all data sources to check
    otp_files = [
        ("OTP Indonesia (Narogong)", "otp_indonesia_narogong.json"),
        ("OTP Indonesia (Duri)", "otp_indonesia_duri.json"),
        ("OTP Indonesia (Balikpapan)", "otp_indonesia_balikpapan.json"),
        ("OTP Asia", "otp_asia_data.json"),
    ]
    
    matrix_categories = ["audit", "training", "drill", "meeting"]
    matrix_files = []
    for cat in matrix_categories:
        for base in ["narogong", "duri", "balikpapan"]:
            matrix_files.append((f"Matrix {cat.title()} ({base.title()})", f"matrix_{cat}_indonesia_{base}.json"))
    
    all_files = otp_files + matrix_files
    
    for source_name, filename in all_files:
        file_path = data_dir / filename
        if not file_path.exists():
            continue
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            for prog in data.get("programs", []):
                program_name = prog.get("name", "Unknown Program")
                
                for month_key, month_data in prog.get("months", {}).items():
                    plan_date = month_data.get("plan_date", "")
                    if not plan_date:
                        continue
                    
                    pic_email = month_data.get("pic_email", "")
                    pic_manager_email = month_data.get("pic_manager_email", "")
                    pic_name = month_data.get("pic_name", "N/A")
                    
                    # Check if plan_date matches 2 weeks or 1 week from now
                    days_remaining = None
                    if plan_date == two_weeks_str:
                        days_remaining = 14
                    elif plan_date == one_week_str:
                        days_remaining = 7
                    
                    if days_remaining:
                        subject = f"{'⚠️ URGENT: ' if days_remaining == 7 else ''}HSE Reminder: {program_name} - {days_remaining} days remaining"
                        html_body = generate_reminder_email_html(
                            days_remaining=days_remaining,
                            program_name=program_name,
                            source=source_name,
                            plan_date=plan_date,
                            month=month_key,
                            pic_name=pic_name
                        )
                        
                        # Send to PIC
                        if pic_email:
                            if send_email(pic_email, subject, html_body):
                                reminders_sent += 1
                        
                        # Send to PIC Manager
                        if pic_manager_email and pic_manager_email != pic_email:
                            if send_email(pic_manager_email, f"[Manager Copy] {subject}", html_body):
                                reminders_sent += 1
                                
        except Exception as e:
            print(f"[REMINDER ERROR] Failed to process {filename}: {e}")
    
    print(f"[REMINDER CHECK] Completed. Sent {reminders_sent} reminder emails.")
    return reminders_sent


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
    scheduler.add_job(
        check_otp_matrix_reminders,
        'cron',
        hour=8,
        minute=5,
        id='daily_otp_matrix_reminder_check'
    )
    scheduler.start()
    print("[STARTUP] Scheduler started - daily checks at 08:00 (HSE Programs) and 08:05 (OTP/Matrix)")

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


@app.post("/test-reminders")
def test_reminders():
    """Manually trigger the OTP/Matrix reminder check for testing."""
    reminders_sent = check_otp_matrix_reminders()
    return {
        "status": "completed",
        "reminders_sent": reminders_sent,
        "message": f"Checked all OTP and Matrix data. Sent {reminders_sent} reminder emails."
    }


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


# ===== CALENDAR EVENTS API =====
@app.get("/calendar-events")
def get_calendar_events():
    """Get all calendar events from OTP and Matrix screens for calendar display."""
    events = []
    
    # Load OTP Indonesia - all bases
    for base in ["narogong", "duri", "balikpapan"]:
        otp_data = load_otp_data(base)
        for prog in otp_data.get("programs", []):
            for month_key, month_data in prog.get("months", {}).items():
                plan_date = month_data.get("plan_date", "")
                impl_date = month_data.get("impl_date", "")
                if plan_date or impl_date:
                    events.append({
                        "id": prog.get("id"),
                        "source": "otp",
                        "region": "indonesia",
                        "base": base,
                        "category": None,
                        "program_name": prog.get("name", "Unknown"),
                        "month": month_key,
                        "plan_date": plan_date,
                        "impl_date": impl_date,
                        "pic_name": month_data.get("pic_name", ""),
                        "plan_type": prog.get("plan_type", "")
                    })
    
    # Load OTP Asia
    otp_asia_path = Path(__file__).parent / "data" / "otp_asia_data.json"
    if otp_asia_path.exists():
        with open(otp_asia_path, 'r') as f:
            otp_asia_data = json.load(f)
            for prog in otp_asia_data.get("programs", []):
                for month_key, month_data in prog.get("months", {}).items():
                    plan_date = month_data.get("plan_date", "")
                    impl_date = month_data.get("impl_date", "")
                    if plan_date or impl_date:
                        events.append({
                            "id": prog.get("id"),
                            "source": "otp",
                            "region": "asia",
                            "base": None,
                            "category": None,
                            "program_name": prog.get("name", "Unknown"),
                            "month": month_key,
                            "plan_date": plan_date,
                            "impl_date": impl_date,
                            "pic_name": month_data.get("pic_name", ""),
                            "plan_type": prog.get("plan_type", "")
                        })
    
    # Load Matrix - all categories, Indonesia all bases
    for category in ["audit", "training", "drill", "meeting"]:
        for base in ["narogong", "duri", "balikpapan"]:
            matrix_data = load_matrix_data(category, "indonesia", base)
            for prog in matrix_data.get("programs", []):
                for month_key, month_data in prog.get("months", {}).items():
                    plan_date = month_data.get("plan_date", "")
                    impl_date = month_data.get("impl_date", "")
                    if plan_date or impl_date:
                        events.append({
                            "id": prog.get("id"),
                            "source": "matrix",
                            "region": "indonesia",
                            "base": base,
                            "category": category,
                            "program_name": prog.get("name", "Unknown"),
                            "month": month_key,
                            "plan_date": plan_date,
                            "impl_date": impl_date,
                            "pic_name": month_data.get("pic_name", ""),
                            "plan_type": prog.get("plan_type", "")
                        })
    
    return {"events": events}


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

def get_otp_file_path(base: str = None):
    """Get the file path for OTP data based on base."""
    if base and base != "all":
        return Path(__file__).parent / "data" / f"otp_indonesia_{base}.json"
    return OTP_DATA_FILE

def load_otp_data(base: str = None):
    """Load OTP data from JSON file. If base is 'all', merge data from all bases."""
    if base == "all":
        # Aggregate data from all 3 bases - MERGE month data
        programs_by_id = {}
        for b in ["narogong", "duri", "balikpapan"]:
            file_path = get_otp_file_path(b)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    for prog in data.get("programs", []):
                        prog_id = prog.get("id")
                        if prog_id not in programs_by_id:
                            # First time seeing this program, add it with a copy
                            programs_by_id[prog_id] = {
                                "id": prog_id,
                                "name": prog.get("name", ""),
                                "plan_type": prog.get("plan_type", ""),
                                "due_date": prog.get("due_date"),
                                "months": dict(prog.get("months", {})),
                                "progress": prog.get("progress", 0)
                            }
                        else:
                            # Merge month data - use data from this base if it has values
                            existing = programs_by_id[prog_id]
                            for month_key, month_data in prog.get("months", {}).items():
                                if month_key not in existing["months"]:
                                    existing["months"][month_key] = month_data
                                else:
                                    # Merge: prefer non-empty values from this base
                                    existing_month = existing["months"][month_key]
                                    for field in ["plan", "actual", "wpts_id", "plan_date", "impl_date", "pic_name", "pic_manager", "pic_email", "pic_manager_email"]:
                                        if month_data.get(field) and not existing_month.get(field):
                                            existing_month[field] = month_data[field]
        return {"year": 2026, "programs": list(programs_by_id.values())}
    
    file_path = get_otp_file_path(base)
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return {"year": 2026, "programs": []}

def save_otp_data(data, base: str = None):
    """Save OTP data to JSON file."""
    file_path = get_otp_file_path(base)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
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
def get_otp_data(base: str = None):
    """Get all OTP data. Pass base=narogong|duri|balikpapan|all for specific base data."""
    data = load_otp_data(base)
    # Calculate progress for each program
    for prog in data.get("programs", []):
        prog["progress"] = calculate_progress(prog)
    return data


@app.get("/otp/{program_id}")
def get_otp_program(program_id: int, base: str = None):
    """Get a specific OTP program by ID."""
    data = load_otp_data(base)
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            prog["progress"] = calculate_progress(prog)
            return prog
    raise HTTPException(status_code=404, detail="OTP program not found")


class OTPMonthUpdate(BaseModel):
    plan: Optional[int] = None
    actual: Optional[int] = None
    wpts_id: Optional[str] = None
    plan_date: Optional[str] = None
    impl_date: Optional[str] = None
    pic_name: Optional[str] = None
    pic_manager: Optional[str] = None
    pic_email: Optional[str] = None
    pic_manager_email: Optional[str] = None


@app.put("/otp/{program_id}/month/{month}")
def update_otp_month(program_id: int, month: str, update: OTPMonthUpdate, base: str = None):
    """Update Plan/Actual values for a specific month of an OTP program."""
    valid_months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    if month.lower() not in valid_months:
        raise HTTPException(status_code=400, detail=f"Invalid month. Must be one of: {valid_months}")
    
    def update_program_month(prog, month_key, upd):
        """Helper to update a program's month data."""
        if "months" not in prog:
            prog["months"] = {}
        if month_key not in prog["months"]:
            prog["months"][month_key] = {"plan": 0, "actual": 0}
        
        if upd.plan is not None:
            prog["months"][month_key]["plan"] = upd.plan
        if upd.actual is not None:
            prog["months"][month_key]["actual"] = upd.actual
        if upd.wpts_id is not None:
            prog["months"][month_key]["wpts_id"] = upd.wpts_id
        if upd.plan_date is not None:
            prog["months"][month_key]["plan_date"] = upd.plan_date
        if upd.impl_date is not None:
            prog["months"][month_key]["impl_date"] = upd.impl_date
        if upd.pic_name is not None:
            prog["months"][month_key]["pic_name"] = upd.pic_name
        if upd.pic_manager is not None:
            prog["months"][month_key]["pic_manager"] = upd.pic_manager
        if upd.pic_email is not None:
            prog["months"][month_key]["pic_email"] = upd.pic_email
        if upd.pic_manager_email is not None:
            prog["months"][month_key]["pic_manager_email"] = upd.pic_manager_email
        prog["progress"] = calculate_progress(prog)
    
    # If base is 'all', update ALL 3 bases
    if base == "all":
        bases_to_update = ["narogong", "duri", "balikpapan"]
        updated_prog = None
        for b in bases_to_update:
            data = load_otp_data(b)
            for prog in data.get("programs", []):
                if prog.get("id") == program_id:
                    update_program_month(prog, month.lower(), update)
                    updated_prog = prog
                    break
            save_otp_data(data, b)
        if updated_prog:
            return {"message": f"OTP program {program_id} month {month} updated in all bases", "program": updated_prog}
        raise HTTPException(status_code=404, detail="OTP program not found")
    
    # Update single base
    data = load_otp_data(base)
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            update_program_month(prog, month.lower(), update)
            save_otp_data(data, base)
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


# ===== OTP ASIA DATA PERSISTENCE =====
OTP_ASIA_DATA_FILE = Path(__file__).parent / "data" / "otp_asia_data.json"

def load_otp_asia_data():
    """Load OTP ASIA data from JSON file."""
    if OTP_ASIA_DATA_FILE.exists():
        with open(OTP_ASIA_DATA_FILE, 'r') as f:
            return json.load(f)
    return {"year": 2026, "programs": []}

def save_otp_asia_data(data):
    """Save OTP ASIA data to JSON file."""
    OTP_ASIA_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OTP_ASIA_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_progress_asia(program):
    """Calculate progress percentage for an OTP ASIA program."""
    total_plan = 0
    total_actual = 0
    for month_data in program.get("months", {}).values():
        total_plan += month_data.get("plan", 0)
        total_actual += month_data.get("actual", 0)
    if total_plan == 0:
        return 100 if total_actual >= 0 else 0
    return min(100, round((total_actual / total_plan) * 100))


@app.get("/otp-asia")
def get_otp_asia_data():
    """Get all OTP ASIA data."""
    data = load_otp_asia_data()
    for prog in data.get("programs", []):
        prog["progress"] = calculate_progress_asia(prog)
    return data


@app.get("/otp-asia/{program_id}")
def get_otp_asia_program(program_id: int):
    """Get a specific OTP ASIA program by ID."""
    data = load_otp_asia_data()
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            prog["progress"] = calculate_progress_asia(prog)
            return prog
    raise HTTPException(status_code=404, detail="OTP ASIA program not found")


class OTPAsiaMonthUpdate(BaseModel):
    plan: Optional[int] = None
    actual: Optional[int] = None
    wpts_id: Optional[str] = None
    plan_date: Optional[str] = None
    impl_date: Optional[str] = None
    pic_name: Optional[str] = None
    pic_manager: Optional[str] = None
    pic_email: Optional[str] = None
    pic_manager_email: Optional[str] = None


@app.put("/otp-asia/{program_id}/month/{month}")
def update_otp_asia_month(program_id: int, month: str, update: OTPAsiaMonthUpdate):
    """Update Plan/Actual values for a specific month of an OTP ASIA program."""
    valid_months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    if month.lower() not in valid_months:
        raise HTTPException(status_code=400, detail=f"Invalid month. Must be one of: {valid_months}")
    
    data = load_otp_asia_data()
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
            if update.plan_date is not None:
                prog["months"][month.lower()]["plan_date"] = update.plan_date
            if update.impl_date is not None:
                prog["months"][month.lower()]["impl_date"] = update.impl_date
            if update.pic_name is not None:
                prog["months"][month.lower()]["pic_name"] = update.pic_name
            if update.pic_manager is not None:
                prog["months"][month.lower()]["pic_manager"] = update.pic_manager
            if update.pic_email is not None:
                prog["months"][month.lower()]["pic_email"] = update.pic_email
            if update.pic_manager_email is not None:
                prog["months"][month.lower()]["pic_manager_email"] = update.pic_manager_email
            
            prog["progress"] = calculate_progress_asia(prog)
            save_otp_asia_data(data)
            return {"message": f"OTP ASIA program {program_id} month {month} updated", "program": prog}
    
    raise HTTPException(status_code=404, detail="OTP ASIA program not found")


class OTPAsiaProgramCreate(BaseModel):
    name: str
    plan_type: Optional[str] = "Annually"
    due_date: Optional[str] = None


@app.post("/otp-asia")
def create_otp_asia_program(program: OTPAsiaProgramCreate):
    """Create a new OTP ASIA program."""
    data = load_otp_asia_data()
    
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
    save_otp_asia_data(data)
    return {"message": "OTP ASIA program created successfully", "program": new_program}


class OTPAsiaProgramUpdate(BaseModel):
    name: Optional[str] = None
    plan_type: Optional[str] = None
    due_date: Optional[str] = None


@app.put("/otp-asia/{program_id}")
def update_otp_asia_program(program_id: int, update: OTPAsiaProgramUpdate):
    """Update an OTP ASIA program's metadata."""
    data = load_otp_asia_data()
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            if update.name is not None:
                prog["name"] = update.name
            if update.plan_type is not None:
                prog["plan_type"] = update.plan_type
            if update.due_date is not None:
                prog["due_date"] = update.due_date
            
            save_otp_asia_data(data)
            return {"message": f"OTP ASIA program {program_id} updated", "program": prog}
    
    raise HTTPException(status_code=404, detail="OTP ASIA program not found")


@app.delete("/otp-asia/{program_id}")
def delete_otp_asia_program(program_id: int):
    """Delete an OTP ASIA program."""
    data = load_otp_asia_data()
    original_count = len(data.get("programs", []))
    data["programs"] = [p for p in data.get("programs", []) if p.get("id") != program_id]
    
    if len(data["programs"]) == original_count:
        raise HTTPException(status_code=404, detail="OTP ASIA program not found")
    
    save_otp_asia_data(data)
    return {"message": f"OTP ASIA program {program_id} deleted successfully"}


@app.put("/otp-asia/year/{year}")
def update_otp_asia_year(year: int):
    """Update the OTP ASIA year."""
    data = load_otp_asia_data()
    data["year"] = year
    save_otp_asia_data(data)
    return {"message": f"OTP ASIA year updated to {year}"}


# ===== MATRIX API =====
# Matrix categories: audit, training, drill, meeting
# Matrix regions: indonesia, asia

def get_matrix_file_path(category: str, region: str, base: str = None):
    """Get the file path for a specific matrix category, region, and base."""
    if region == "indonesia" and base and base != "all":
        return Path(__file__).parent / "data" / f"matrix_{category}_{region}_{base}.json"
    return Path(__file__).parent / "data" / f"matrix_{category}_{region}.json"

def load_matrix_data(category: str, region: str, base: str = None):
    """Load matrix data for a specific category, region, and base."""
    if region == "indonesia" and base == "all":
        # Aggregate data from all 3 bases - MERGE month data
        programs_by_id = {}
        for b in ["narogong", "duri", "balikpapan"]:
            file_path = get_matrix_file_path(category, region, b)
            if file_path.exists():
                with open(file_path, "r") as f:
                    data = json.load(f)
                    for prog in data.get("programs", []):
                        prog_id = prog.get("id")
                        if prog_id not in programs_by_id:
                            # First time seeing this program, add it with a copy
                            programs_by_id[prog_id] = {
                                "id": prog_id,
                                "name": prog.get("name", ""),
                                "reference": prog.get("reference", ""),
                                "plan_type": prog.get("plan_type", ""),
                                "due_date": prog.get("due_date"),
                                "months": dict(prog.get("months", {})),
                                "progress": prog.get("progress", 0)
                            }
                        else:
                            # Merge month data - use data from this base if it has values
                            existing = programs_by_id[prog_id]
                            for month_key, month_data in prog.get("months", {}).items():
                                if month_key not in existing["months"]:
                                    existing["months"][month_key] = month_data
                                else:
                                    # Merge: prefer non-empty values from this base
                                    existing_month = existing["months"][month_key]
                                    for field in ["plan", "actual", "wpts_id", "plan_date", "impl_date", "pic_name", "pic_manager", "pic_email", "pic_manager_email"]:
                                        if month_data.get(field) and not existing_month.get(field):
                                            existing_month[field] = month_data[field]
        return {"year": 2026, "category": category, "region": region, "programs": list(programs_by_id.values())}
    
    file_path = get_matrix_file_path(category, region, base)
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)
    return {"year": 2026, "category": category, "region": region, "programs": []}

def save_matrix_data(category: str, region: str, data: dict, base: str = None):
    """Save matrix data for a specific category, region, and base."""
    file_path = get_matrix_file_path(category, region, base)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def calculate_matrix_progress(program: dict) -> int:
    """Calculate progress based on plan vs actual."""
    total_plan = 0
    total_actual = 0
    for month_data in program.get("months", {}).values():
        total_plan += month_data.get("plan", 0)
        total_actual += month_data.get("actual", 0)
    if total_plan == 0:
        return 0
    return min(100, int((total_actual / total_plan) * 100))

class MatrixMonthUpdate(BaseModel):
    plan: int
    actual: int
    wpts_id: Optional[str] = ""
    plan_date: Optional[str] = ""
    impl_date: Optional[str] = ""
    pic_name: Optional[str] = ""
    pic_manager: Optional[str] = ""
    pic_email: Optional[str] = ""
    pic_manager_email: Optional[str] = ""

class MatrixProgramCreate(BaseModel):
    name: str
    reference: Optional[str] = ""
    plan_type: Optional[str] = "Monthly"
    due_date: Optional[str] = None

class MatrixProgramUpdate(BaseModel):
    name: Optional[str] = None
    reference: Optional[str] = None
    plan_type: Optional[str] = None
    due_date: Optional[str] = None

@app.get("/matrix")
def get_matrix_programs(category: str = "audit", region: str = "indonesia", base: str = None):
    """Get all matrix programs for a specific category, region, and base."""
    valid_categories = ["audit", "training", "drill", "meeting"]
    valid_regions = ["indonesia", "asia"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {valid_categories}")
    if region not in valid_regions:
        raise HTTPException(status_code=400, detail=f"Invalid region. Must be one of: {valid_regions}")
    return load_matrix_data(category, region, base)

@app.get("/matrix/{program_id}")
def get_matrix_program(program_id: int, category: str = "audit", region: str = "indonesia", base: str = None):
    """Get a specific matrix program by ID."""
    data = load_matrix_data(category, region, base)
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            return prog
    raise HTTPException(status_code=404, detail="Matrix program not found")

@app.put("/matrix/{program_id}/month/{month}")
def update_matrix_month(program_id: int, month: str, update: MatrixMonthUpdate, category: str = "audit", region: str = "indonesia", base: str = None):
    """Update monthly plan/actual values for a matrix program."""
    valid_months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    if month.lower() not in valid_months:
        raise HTTPException(status_code=400, detail=f"Invalid month. Must be one of: {valid_months}")
    
    month_data = {
        "plan": update.plan,
        "actual": update.actual,
        "wpts_id": update.wpts_id or "",
        "plan_date": update.plan_date or "",
        "impl_date": update.impl_date or "",
        "pic_name": update.pic_name or "",
        "pic_manager": update.pic_manager or "",
        "pic_email": update.pic_email or "",
        "pic_manager_email": update.pic_manager_email or ""
    }
    
    # If base is 'all', update ALL 3 bases
    if base == "all":
        bases_to_update = ["narogong", "duri", "balikpapan"]
        updated_prog = None
        for b in bases_to_update:
            data = load_matrix_data(category, region, b)
            for prog in data.get("programs", []):
                if prog.get("id") == program_id:
                    if "months" not in prog:
                        prog["months"] = {}
                    prog["months"][month.lower()] = month_data
                    prog["progress"] = calculate_matrix_progress(prog)
                    updated_prog = prog
                    break
            save_matrix_data(category, region, data, b)
        if updated_prog:
            return {"message": "Matrix month updated in all bases", "program": updated_prog}
        raise HTTPException(status_code=404, detail="Matrix program not found")
    
    # Update single base
    data = load_matrix_data(category, region, base)
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            if "months" not in prog:
                prog["months"] = {}
            prog["months"][month.lower()] = month_data
            prog["progress"] = calculate_matrix_progress(prog)
            save_matrix_data(category, region, data, base)
            return {"message": "Matrix month updated", "program": prog}
    raise HTTPException(status_code=404, detail="Matrix program not found")

@app.post("/matrix")
def create_matrix_program(program: MatrixProgramCreate, category: str = "audit", region: str = "indonesia"):
    """Create a new matrix program."""
    data = load_matrix_data(category, region)
    new_id = max([p.get("id", 0) for p in data.get("programs", [])] + [0]) + 1
    new_program = {
        "id": new_id,
        "name": program.name,
        "reference": program.reference or "",
        "plan_type": program.plan_type or "Monthly",
        "due_date": program.due_date,
        "months": {m: {"plan": 0, "actual": 0, "wpts_id": ""} for m in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]},
        "progress": 0
    }
    data["programs"].append(new_program)
    save_matrix_data(category, region, data)
    return {"message": "Matrix program created", "program": new_program}

@app.put("/matrix/{program_id}")
def update_matrix_program(program_id: int, update: MatrixProgramUpdate, category: str = "audit", region: str = "indonesia"):
    """Update matrix program metadata."""
    data = load_matrix_data(category, region)
    for prog in data.get("programs", []):
        if prog.get("id") == program_id:
            if update.name is not None:
                prog["name"] = update.name
            if update.reference is not None:
                prog["reference"] = update.reference
            if update.plan_type is not None:
                prog["plan_type"] = update.plan_type
            if update.due_date is not None:
                prog["due_date"] = update.due_date
            save_matrix_data(category, region, data)
            return {"message": "Matrix program updated", "program": prog}
    raise HTTPException(status_code=404, detail="Matrix program not found")

@app.delete("/matrix/{program_id}")
def delete_matrix_program(program_id: int, category: str = "audit", region: str = "indonesia"):
    """Delete a matrix program."""
    data = load_matrix_data(category, region)
    original_count = len(data.get("programs", []))
    data["programs"] = [p for p in data.get("programs", []) if p.get("id") != program_id]
    if len(data["programs"]) == original_count:
        raise HTTPException(status_code=404, detail="Matrix program not found")
    save_matrix_data(category, region, data)
    return {"message": f"Matrix program {program_id} deleted successfully"}


@app.post("/test-reminder")
def test_reminder():
    """Manually trigger reminder check (for testing)."""
    check_and_send_reminders()
    return {"message": "Reminder check executed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

