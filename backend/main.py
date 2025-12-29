import os
from datetime import datetime, timedelta, date
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
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
    title="HSE Management System API",
    description="API for managing HSE Programs with automated reminders",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "HSE Management System", "version": "2.0.0"}


@app.get("/program-types")
def get_program_types():
    """Get available program types."""
    return PROGRAM_TYPES


@app.get("/statistics")
def get_statistics(session: Session = Depends(get_session)):
    """Get dashboard statistics (matching legacy CSMS dashboard)."""
    # Total counts
    total_programs = session.exec(select(func.count(HSEProgram.id))).one()
    completed = session.exec(
        select(func.count(HSEProgram.id)).where(HSEProgram.status == "Closed")
    ).one()
    pending = session.exec(
        select(func.count(HSEProgram.id)).where(HSEProgram.status != "Closed")
    ).one()
    
    # This month
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
    
    # Upcoming (next 30 days)
    upcoming = session.exec(
        select(func.count(HSEProgram.id)).where(
            HSEProgram.planned_date >= datetime.now(),
            HSEProgram.planned_date <= datetime.now() + timedelta(days=30),
            HSEProgram.status != "Closed"
        )
    ).one()
    
    # Programs by type
    by_type = {}
    for ptype in PROGRAM_TYPES.keys():
        count = session.exec(
            select(func.count(HSEProgram.id)).where(HSEProgram.program_type == ptype)
        ).one()
        by_type[ptype] = count
    
    # Completion rate
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
    """Update an existing HSE program status (legacy endpoint)."""
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

    # Update only provided fields
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


@app.post("/test-reminder")
def test_reminder():
    """Manually trigger reminder check (for testing)."""
    check_and_send_reminders()
    return {"message": "Reminder check executed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
