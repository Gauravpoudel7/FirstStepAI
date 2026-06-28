export interface DemoAccountRow {
  email: string;
  full_name: string;
  role: string;
  default_password: string;
}

export interface UserOut {
  id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: string[];
  must_reset_password: boolean;
  initials?: string;
  employee_profile?: Record<string, unknown> | null;
}

export interface ConversationOut {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  preview?: string | null;
}

export interface MessageOut {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: Array<{ doc_id: string; title: string; chunk_id?: string }>;
  feedback?: "up" | "down" | null;
  created_at: string;
}

export interface DocumentOut {
  id: string;
  title: string;
  doc_type: string;
  department: string;
  required_role: string;
  chunk_count: number;
  indexed_at?: string | null;
  created_at: string;
}

export interface ProjectOut {
  id: string;
  name: string;
  description: string;
  status: string;
  start_date?: string | null;
  end_date?: string | null;
  tags: string[];
  owner_id: string;
  member_ids?: string[];
  members?: Array<{ employee_id: string; full_name: string; role: string }>;
  created_at: string;
}

export interface ProjectEmployeeOption {
  id: string;
  employee_id: string;
  name: string;
  department: string;
}

export interface SettingsOut {
  theme: string;
  language: string;
  notification_prefs: Record<string, unknown>;
  anonymized_telemetry: boolean;
  updated_at?: string | null;
}

export interface BrandingOut {
  company_name: string;
  logo_text: string;
  theme_default: string;
}

export interface AdminUserOut {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  department?: string | null;
  employee_id?: string | null;
}

export interface ActivityLogEntry {
  id: number;
  action: string;
  actor_id?: string | null;
  resource_type?: string | null;
  resource_id?: string | null;
  ip?: string | null;
  created_at: string;
  extra?: Record<string, unknown>;
}

export interface ActivityLogSummary {
  counts_by_action: Record<string, number>;
  total: number;
  recent: ActivityLogEntry[];
  generated_at: string;
}

export interface DashboardSummaryOut {
  full_name: string;
  role: string;
  department: string;
  designation: string;
  leave_balance: number;
  active_projects: number;
  upcoming_holidays: Array<{ date: string; name: string }>;
  announcements: Array<{ title: string; body: string; created_at: string }>;
  ai_usage: { messages_today: number; tokens_this_week: number };
}