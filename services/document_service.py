"""Document service — list the documents a user is allowed to see."""
from __future__ import annotations

from auth.models import User
from core.rbac import allowed_doc_roles


def list_accessible_documents(user: User) -> list[dict]:
    """Return metadata for documents the user can access.

    For now, the bundled policies PDF is the only indexed source. We tag it
    with `required_role=all` so everyone can see it.
    """
    from config.settings import get_settings

    pdf_name = "umbrella_corp_policies.pdf"
    pdf_path = get_settings().POLICIES_PDF
    allowed = set(allowed_doc_roles(user.role))
    docs = [
        {
            "id": "doc-policies",
            "title": "Employee Handbook & HR Policies",
            "doc_type": "policy",
            "department": "HR",
            "required_role": "all",
            "source": pdf_name,
            "summary": (
                "Umbrella Corporation's official handbook covering onboarding, "
                "leave, conduct, security protocols, and benefits."
            ),
        },
        {
            "id": "doc-eng-handbook",
            "title": "Engineering Practices Handbook",
            "doc_type": "handbook",
            "department": "Engineering",
            "required_role": "employee",
            "source": "engineering_practices.md",
            "summary": (
                "Coding standards, code-review process, deployment pipeline, "
                "and on-call rotation."
            ),
        },
        {
            "id": "doc-finance",
            "title": "Finance & Expense Policies",
            "doc_type": "policy",
            "department": "Finance",
            "required_role": "hr",
            "source": "finance_policies.md",
            "summary": (
                "Expense reimbursement, travel booking, vendor onboarding, "
                "and procurement thresholds."
            ),
        },
        {
            "id": "doc-mgmt",
            "title": "Manager's Guide to Performance Reviews",
            "doc_type": "sop",
            "department": "HR",
            "required_role": "manager",
            "source": "manager_review_sop.md",
            "summary": (
                "Quarterly review template, calibration process, and PIP "
                "guidance for people managers."
            ),
        },
        {
            "id": "doc-audit",
            "title": "Security & Audit Log Reference",
            "doc_type": "tech_doc",
            "department": "Security",
            "required_role": "admin",
            "source": "audit_log_reference.md",
            "summary": (
                "Reference for accessing and interpreting the corporate audit "
                "log and incident-response procedures."
            ),
        },
    ]
    return [d for d in docs if d["required_role"] in allowed]


def recent_documents(user: User, limit: int = 5) -> list[dict]:
    """Subset of `list_accessible_documents` for the dashboard."""
    return list_accessible_documents(user)[:limit]