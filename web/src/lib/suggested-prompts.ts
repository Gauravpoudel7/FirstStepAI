export const SUGGESTED_PROMPTS: Record<string, string[]> = {
  employee: [
    "Who is my manager?",
    "How many leave days do I have?",
    "Summarize the company's leave policy",
  ],
  manager: [
    "Show me the performance review template",
    "What projects is my team working on?",
    "Summarize the expense reimbursement policy",
  ],
  hr: [
    "List recent policy updates",
    "Show the onboarding checklist",
    "Explain the parental leave policy",
  ],
  admin: [
    "Summarize the incident-response procedure",
    "Show all audit-log documentation",
    "Give me a system-wide overview",
  ],
};

export const WELCOME_MESSAGE = `👋 **Welcome to FirstStepAI**

I'm your enterprise AI assistant. I can help you with:

- 📋 **HR policies** — leave, benefits, code of conduct
- 🗂️ **Onboarding** — first-week checklist, systems access, training
- 🔐 **Security & compliance** — incident reporting, data classification
- 👤 **Your profile** — projects, manager, skills, leave balance
- 📚 **Engineering & operations** — SOPs, handbooks, internal docs

Ask anything below — I'm here to help. You can also try one of the suggested prompts to get started.
`;
