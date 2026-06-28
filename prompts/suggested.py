"""Per-role suggested prompts shown above the chat input."""
from auth.models import Role


SUGGESTED_PROMPTS: dict[Role, list[str]] = {
    Role.EMPLOYEE: [
        "Who is my manager?",
        "How many leave days do I have?",
        "Summarize the company's leave policy",
    ],
    Role.MANAGER: [
        "Show me the performance review template",
        "What projects is my team working on?",
        "Summarize the expense reimbursement policy",
    ],
    Role.HR: [
        "List recent policy updates",
        "Show the onboarding checklist",
        "Explain the parental leave policy",
    ],
    Role.ADMIN: [
        "Summarize the incident-response procedure",
        "Show all audit-log documentation",
        "Give me a system-wide overview",
    ],
}
