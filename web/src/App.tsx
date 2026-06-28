import { Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { LoginPage } from "@/features/auth/LoginPage";
import ForgotPasswordPage from "@/features/auth/ForgotPasswordPage";
import ResetPasswordPage from "@/features/auth/ResetPasswordPage";
import { ProtectedRoute } from "@/routes/ProtectedRoute";
import DashboardPage from "@/features/dashboard/DashboardPage";
import KnowledgeBasePage from "@/features/knowledge/KnowledgeBasePage";
import ProjectsPage from "@/features/projects/ProjectsPage";
import DocumentsPage from "@/features/documents/DocumentsPage";
import AnalyticsPage from "@/features/analytics/AnalyticsPage";
import ChatHistoryPage from "@/features/history/ChatHistoryPage";
import SettingsPage from "@/features/settings/SettingsPage";
import ProfilePage from "@/features/profile/ProfilePage";
import AdminPage from "@/features/admin/AdminPage";
import ChatPage from "@/features/chat/ChatPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      <Route
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="knowledge" element={<KnowledgeBasePage />} />
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="history" element={<ChatHistoryPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route
          path="admin"
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminPage />
            </ProtectedRoute>
          }
        />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}