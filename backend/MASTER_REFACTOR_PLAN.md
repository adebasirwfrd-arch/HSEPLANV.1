Markdown

**ROLE:** Senior Full Stack Architect & Refactoring Specialist.

**MISSION:**
Execute a complete "Renovation" of the legacy HSE Management System.
Refactor the monolithic source code into a "Smart Monolith" architecture (Modular Development -> Single File Deployment).

**CONTEXT:**
- **Legacy Source:** `/Users/izzadev/.gemini/antigravity/scratch/hse-management-system/index.html` (READ THIS FILE FIRST).
- **Target Directory:** `/Users/izzadev/.gemini/antigravity/scratch/hse-plan v.2` (CREATE THIS).

**CORE STRATEGY (THE NEW WORKFLOW):**
1.  **EXTRACT:** Pull only active logic (Dashboard, Calendar/OTP, KPI, Incidents) into `src/` files. Discard Login/Profile/Settings code.
2.  **MODERNIZE:** Replace old navigation with a **Side Drawer (Hamburger Menu)**.
3.  **AUTOMATE:** Create a `build.py` script. The workflow is: Edit `src/` -> Run `build.py` -> Output `index.html`.
4.  **DOCUMENT:** Create `AI_RULES.md` so future AI sessions understand this architecture.

---

### PHASE 1: BACKEND SETUP (Hugging Face Ready)
Create in root `hse-plan v.2/`:

1.  **`Dockerfile`**:
    ```dockerfile
    FROM python:3.9-slim
    WORKDIR /app
    COPY . /app
    RUN pip install --no-cache-dir fastapi uvicorn
    RUN useradd -m -u 1000 user
    USER user
    ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
    ```
2.  **`main.py`**:
    ```python
    from fastapi import FastAPI
    from fastapi.responses import FileResponse
    app = FastAPI()
    @app.get("/")
    async def read_root(): return FileResponse('index.html')
    ```

---

### PHASE 2: SOURCE EXTRACTION (The `src/` Folder)
Create `src/` folder inside target. Extract content from Legacy Source as follows:

**1. `src/style.css`**
- Extract ALL CSS used by Dashboard, Calendar, KPI, and Forms.
- **ADD DRAWER CSS:**
  ```css
  .drawer { position: fixed; top: 0; left: -260px; height: 100%; width: 260px; background: #1e293b; transition: 0.3s; z-index: 1000; padding-top: 60px; }
  .drawer.open { left: 0; }
  .drawer a { display: block; padding: 15px 20px; color: #cbd5e1; text-decoration: none; border-bottom: 1px solid #334155; }
  .drawer a:hover { background: #0f172a; color: white; }
  .hamburger { position: fixed; top: 15px; left: 15px; font-size: 24px; cursor: pointer; z-index: 1100; color: #333; }
  .view-section { display: none; padding: 60px 20px; } /* Hide views by default */
2. src/script.js

Extract ALL Data Arrays (programs, kpiData) and Render Functions (renderCalendar, renderChart, submitIncident).

ADD NAV LOGIC:

JavaScript

function toggleDrawer() { document.querySelector('.drawer').classList.toggle('open'); }
function switchView(viewId) {
    document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
    document.getElementById(viewId + '-view').style.display = 'block';
    toggleDrawer(); // Close drawer
}
document.addEventListener('DOMContentLoaded', () => {
    switchView('dashboard'); // Default
    // Add safety checks before rendering
    if(typeof renderDashboard === 'function') renderDashboard();
    if(typeof renderCalendar === 'function') renderCalendar();
});
3. src/layout.html (The Shell)

Create HTML skeleton.

Body must contain:

<div class="hamburger" onclick="toggleDrawer()">☰</div>

<div class="drawer">...links calling switchView('dashboard'), switchView('calendar')...</div>

Placeholders for injection: , , , , , .

4. src/views/ (Fragments)

src/views/dashboard.html: Inner HTML of legacy #dashboard-view.

src/views/calendar.html: Inner HTML of legacy #calendar-view.

src/views/kpi.html: Inner HTML of legacy #kpi-view.

src/views/incidents.html: Inner HTML of legacy #incidents-view.

PHASE 3: THE BUILDER (Workflow Automation)
Create build.py in root:

Python

import os
def read(path):
    try: return open(path, 'r', encoding='utf-8').read()
    except: return f""

def build():
    print("🚧 Building...")
    layout = read('src/layout.html')
    # Inject CSS & JS
    layout = layout.replace('', f"<style>{read('src/style.css')}</style>")
    layout = layout.replace('', f"<script>{read('src/script.js')}</script>")
    
    # Inject Views wrapped in IDs
    layout = layout.replace('', f'<div id="dashboard-view" class="view-section">{read("src/views/dashboard.html")}</div>')
    layout = layout.replace('', f'<div id="calendar-view" class="view-section">{read("src/views/calendar.html")}</div>')
    layout = layout.replace('', f'<div id="kpi-view" class="view-section">{read("src/views/kpi.html")}</div>')
    layout = layout.replace('', f'<div id="incidents-view" class="view-section">{read("src/views/incidents.html")}</div>')

    with open('index.html', 'w', encoding='utf-8') as f: f.write(layout)
    print("✅ Build Done: index.html created.")

if __name__ == "__main__": build()
PHASE 4: DOCUMENTATION (AI RULES)
Create AI_RULES.md in root. This defines the development rules:

Markdown

# 🤖 AI RULES - HSE PLAN V.2
1. **NEVER EDIT `index.html`**. It is a build artifact (output).
2. **ALWAYS EDIT `src/`**. Change views, styles, or logic there.
3. **ALWAYS RUN `python build.py`** after making changes to regenerate the app.
4. **FILE MAP:**
   - Styles: `src/style.css`
   - Logic: `src/script.js`
   - UI: `src/views/*.html`
EXECUTION ORDER
Read the Legacy Source File to understand the content.

Create the directory structure hse-plan v.2 and all files listed in Phases 1, 2, 3, and 4.

Run python build.py to generate the first V.2 index.html.