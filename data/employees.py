"""Employee data + user-database seeding.

The original module generated a single fake employee on every run. We extend
it to:
  - generate richer per-employee profiles (designation, manager, projects,
    leave balance, office, permissions, role) used by the chat system prompt;
  - seed an initial user database (`data/users.json`) with bcrypt-hashed
    passwords for the demo accounts the login page advertises.

Idempotent: if `data/users.json` already exists, seeding is skipped.
"""
import random
from datetime import datetime, timedelta
from faker import Faker

from auth.models import EmployeeProfile, Role
from auth.security import hash_password
from config.settings import get_settings
from utils.file_utils import read_json, write_json

fake = Faker()

# ----- domain vocab ---------------------------------------------------------

POSITIONS = [
    "Research Scientist",
    "Senior Software Engineer",
    "Operations Manager",
    "HR Specialist",
    "Security Officer",
    "Biochemist",
    "Data Engineer",
    "Product Manager",
]

DEPARTMENTS = ["R&D", "IT", "Operations", "HR", "Security", "Finance"]

SKILLS_POOL = [
    "Python",
    "Project Management",
    "Data Analysis",
    "Genetic Research",
    "Cybersecurity",
    "Machine Learning",
    "Leadership",
    "Database Management",
    "Public Speaking",
    "Bioengineering",
    "Cloud Architecture",
    "Viral Pathogen Studies",
]

LOCATIONS = [
    "Raccoon City HQ",
    "Umbrella Europe — Paris",
    "Umbrella Asia — Tokyo",
    "Umbrella North America — New York",
    "Umbrella South America — São Paulo",
]

PROJECT_POOL = [
    "Project W-Tyrant",
    "G-Virus R&D",
    "T-Veronica Continuation",
    "U.M.F. Autopsy Review",
    "Hive Network Hardening",
    "Arklay Lab Renovation",
    "Quantum Bio-Computing Initiative",
    "AI Threat Modeling",
    "Satellite Comms Uplink",
    "Pharmaceutical Logistics Overhaul",
]

# ----- demo seed accounts ---------------------------------------------------

DEMO_SEED = [
    {
        "email": "admin@umbrella.corp",
        "full_name": "Alex Wesker",
        "designation": "Chief Operations Officer",
        "department": "Operations",
        "role": Role.ADMIN,
        "manager_name": "Ozwell E. Spencer",
        "projects": ["HIVE Control Expansion", "Executive AI Platform"],
        "office_location": "Raccoon City HQ — Executive Wing",
        "leave_balance": 22,
    },
    {
        "email": "hr@umbrella.corp",
        "full_name": "Lisa Trevor",
        "designation": "Senior HR Specialist",
        "department": "HR",
        "role": Role.HR,
        "manager_name": "Alex Wesker",
        "projects": ["Talent Retention Initiative", "Employee Wellness Program"],
        "office_location": "Raccoon City HQ — HR Wing",
        "leave_balance": 14,
    },
    {
        "email": "manager@umbrella.corp",
        "full_name": "William Birkin",
        "designation": "Head of R&D",
        "department": "R&D",
        "role": Role.MANAGER,
        "manager_name": "Alex Wesker",
        "projects": ["G-Virus R&D", "Project W-Tyrant"],
        "office_location": "Raccoon City HQ — Lab 4",
        "leave_balance": 9,
    },
    {
        "email": "employee@umbrella.corp",
        "full_name": "Jill Valentine",
        "designation": "Security Operations Specialist",
        "department": "Security",
        "role": Role.EMPLOYEE,
        "manager_name": "William Birkin",
        "projects": ["Arklay Mountains Surveillance", "Hive Network Hardening"],
        "office_location": "Raccoon City HQ — Security Ops",
        "leave_balance": 18,
    },
    {
        "email": "demo@umbrella.corp",
        "full_name": "Ada Wong",
        "designation": "Field Intelligence Analyst",
        "department": "R&D",
        "role": Role.EMPLOYEE,
        "manager_name": "William Birkin",
        "projects": ["AI Threat Modeling", "Satellite Comms Uplink"],
        "office_location": "Umbrella Asia — Tokyo",
        "leave_balance": 21,
    },
]

DEFAULT_PASSWORD = "demo123"


def _make_employee_id(idx: int) -> str:
    return f"EMP-{idx:03d}"


def _make_profile(
    *,
    employee_id: str,
    full_name: str,
    email: str,
    designation: str,
    department: str,
    role: Role,
    manager_name: str = "",
    projects: list[str] | None = None,
    office_location: str = "",
    leave_balance: int = 0,
    skills: list[str] | None = None,
    phone_number: str = "",
    hire_date: str = "",
    salary: float = 0.0,
) -> EmployeeProfile:
    return EmployeeProfile(
        employee_id=employee_id,
        full_name=full_name,
        email=email,
        phone_number=phone_number or fake.phone_number(),
        designation=designation,
        department=department,
        manager_id="EMP-001" if role != Role.ADMIN else None,
        manager_name=manager_name,
        projects=projects or [],
        skills=skills or random.sample(SKILLS_POOL, k=random.randint(2, 4)),
        office_location=office_location,
        leave_balance=leave_balance,
        hire_date=hire_date or (datetime.now() - timedelta(days=random.randint(180, 365 * 8))).strftime("%Y-%m-%d"),
        salary=salary or round(random.uniform(55_000, 145_000), 2),
        permissions=_default_permissions_for(role),
        role=role,
    )


def _default_permissions_for(role: Role) -> list[str]:
    """Map role to a permission list (matches core.rbac but kept local to avoid
    a circular import at module-load time)."""
    from core.rbac import permissions_for_role

    return [p.value for p in permissions_for_role(role)]


# ----- public API -----------------------------------------------------------

def generate_employee_data(num_employees: int = 5) -> list[dict]:
    """Generate `num_employees` random employee dicts (legacy entrypoint)."""
    out: list[dict] = []
    for i in range(1, num_employees + 1):
        profile = _make_profile(
            employee_id=_make_employee_id(i),
            full_name=fake.name(),
            email=fake.unique.email(),
            designation=random.choice(POSITIONS),
            department=random.choice(DEPARTMENTS),
            role=random.choice([Role.EMPLOYEE, Role.MANAGER, Role.HR, Role.ADMIN]),
            manager_name=fake.name(),
            projects=random.sample(PROJECT_POOL, k=random.randint(1, 3)),
            office_location=random.choice(LOCATIONS),
            leave_balance=random.randint(0, 25),
        )
        out.append(profile.model_dump(mode="json"))
    return out


def seed_user_database(force: bool = False) -> int:
    """Write a fresh `data/users.json` containing the demo accounts.

    Returns the number of users seeded. Skips if the file already exists
    unless `force=True`.
    """
    settings = get_settings()
    if not force:
        existing = read_json(settings.USERS_DB_PATH, default=None)
        if existing:
            return len(existing)

    rows: list[dict] = []
    for idx, spec in enumerate(DEMO_SEED, start=1):
        profile = _make_profile(
            employee_id=_make_employee_id(idx),
            full_name=spec["full_name"],
            email=spec["email"],
            designation=spec["designation"],
            department=spec["department"],
            role=spec["role"],
            manager_name=spec.get("manager_name", ""),
            projects=spec.get("projects", []),
            office_location=spec.get("office_location", ""),
            leave_balance=spec.get("leave_balance", 0),
        )
        user_dict = {
            "id": f"USR-{idx:03d}",
            "email": spec["email"],
            "full_name": spec["full_name"],
            "role": spec["role"].value,
            "password_hash": hash_password(DEFAULT_PASSWORD),
            "employee_profile": profile.model_dump(mode="json"),
            "created_at": datetime.utcnow().isoformat(),
        }
        rows.append(user_dict)

    write_json(settings.USERS_DB_PATH, rows)
    return len(rows)


def load_employee_profile_for_email(email: str) -> dict | None:
    """Return the employee_profile dict for a given email, or None."""
    users = read_json(get_settings().USERS_DB_PATH, default=[])
    for row in users or []:
        if row.get("email", "").lower() == email.lower():
            return row.get("employee_profile")
    return None