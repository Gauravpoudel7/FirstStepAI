"""My Profile page — view and edit the logged-in user's profile + change password."""
from __future__ import annotations

import streamlit as st

from auth.models import User
from auth.services import get_auth_service
from core.exceptions import InvalidCredentialsError
from services.employee_service import get_employee_profile


def render_profile(user: User) -> None:
    profile = get_employee_profile(user)

    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
          <h1 style="margin: 0; font-size: 1.75rem; letter-spacing: -0.02em;">My Profile</h1>
          <p style="color: var(--text-secondary); margin: 0.25rem 0 0 0;">
            Your personal and employment information.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Profile summary card
    st.markdown(
        f"""
        <div class="glass" style="padding: 1.5rem; margin-bottom: 1rem;">
          <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="avatar" style="width: 64px; height: 64px; font-size: 1.5rem;">
              {user.initials()}
            </div>
            <div>
              <div style="font-size: 1.4rem; font-weight: 700;">{profile.full_name}</div>
              <div style="color: var(--text-secondary);">{profile.designation}</div>
              <div style="color: var(--text-muted); font-size: 0.85rem;">
                {profile.employee_id} · {profile.department}
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Detail grid
    rows = [
        ("Email", profile.email),
        ("Phone", profile.phone_number),
        ("Manager", f"{profile.manager_name or '—'} {('(' + profile.manager_id + ')') if profile.manager_id else ''}"),
        ("Office Location", profile.office_location),
        ("Hire Date", profile.hire_date or "—"),
        ("Leave Balance", f"{profile.leave_balance} days"),
        ("Active Projects", ", ".join(profile.projects) if profile.projects else "—"),
        ("Skills", ", ".join(profile.skills) if profile.skills else "—"),
        ("Permissions", ", ".join(profile.permissions) if profile.permissions else "—"),
    ]
    grid_cols = st.columns(2)
    for col, (label, value) in zip(grid_cols * 2, rows):
        with col:
            st.markdown(
                f"""
                <div style="padding: 0.85rem 1rem; border-radius: var(--radius-md);
                            background: var(--bg-tertiary); border: 1px solid var(--border); margin-bottom: 0.6rem;">
                  <div style="font-size: 0.7rem; font-weight: 600; color: var(--text-muted);
                              text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
                  <div style="font-size: 0.95rem; color: var(--text-primary); margin-top: 0.2rem;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Change password
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='margin: 0 0 0.5rem 0; font-size: 1.1rem;'>Change Password</h3>",
        unsafe_allow_html=True,
    )
    with st.form("change_pw_form"):
        cur = st.text_input("Current password", type="password", key="cp_cur")
        new = st.text_input("New password", type="password", key="cp_new")
        new2 = st.text_input("Confirm new password", type="password", key="cp_new2")
        if st.form_submit_button("Update password", use_container_width=True):
            if not new or new != new2:
                st.error("New passwords do not match.")
            elif len(new) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    get_auth_service().change_password(user, cur, new)
                    st.success("Password updated.")
                except InvalidCredentialsError as e:
                    st.error(str(e))
