from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class HSEProgram(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    program_type: str = Field(default="hse_plan", index=True)  # NEW: Categorize programs
    planned_date: datetime
    actual_date: Optional[datetime] = None
    status: str = Field(default="pending")
    wpts_number: Optional[str] = None
    evidence_link: Optional[str] = None
    pic_name: Optional[str] = None  # NEW: Person In Charge
    manager_email: str = Field(default="ade.basirwfrd@gmail.com")
    created_at: datetime = Field(default_factory=datetime.utcnow)  # NEW: Timestamp


# Program type options (matching legacy schedule types)
PROGRAM_TYPES = {
    "hse_plan": {"label": "📋 HSE Plan", "color": "#e67e22"},
    "hse_committee": {"label": "🏢 HSE Committee", "color": "#9b59b6"},
    "spr": {"label": "📊 SPR Meeting", "color": "#1abc9c"},
    "hazid_hazop": {"label": "⚠️ HAZID/HAZOP", "color": "#e74c3c"},
    "safety_training": {"label": "🎓 Safety Training", "color": "#3498db"},
    "inspection": {"label": "🔍 Inspection", "color": "#27ae60"},
}
