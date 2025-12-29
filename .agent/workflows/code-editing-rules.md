---
description: MANDATORY rules - follow these EVERY TIME before any work
---

# CRITICAL RULES - FOLLOW ALWAYS

## RULE 1: NEVER CODE IMMEDIATELY
- When user asks for ANYTHING, create **implementation_plan.md** FIRST
- Do NOT write any code until user says "start coding"
- Wait for explicit approval before touching any file

## RULE 2: NEVER REMOVE FEATURES
- The app is fully functional - DO NOT break it
- NEVER remove, delete, or change existing functionality
- If user asks for "next step", ASK FOR CONFIRMATION first in implementation plan
- Always preserve all existing features

## RULE 3: ONLY ADD NEW FEATURES
- My job is to ADD new features, not remove them
- Only remove/delete/change if user EXPLICITLY tells me to
- When in doubt, ASK first

## RULE 4: MAINTAIN 5 BACKUP COMMITS
- Before ANY edit, create a backup commit
- Keep last 5 commits available for rollback
- If something breaks, can revert to any of the last 5 states

## HUGGINGFACE SPACE
- Main app: https://huggingface.co/spaces/ade-basirwfrd/HSEPlanv.1

## WORKFLOW
1. User asks for something
2. I create implementation_plan.md
3. User reviews and approves
4. User says "start coding"
5. I create backup commit
6. I make changes
7. I test locally
8. User deploys when ready
