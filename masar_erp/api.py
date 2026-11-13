"""Small authenticated API surface for MASAR ERP."""

import frappe


@frappe.whitelist()
def health():
    """Return application readiness metadata; requires an authenticated session."""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.AuthenticationError)
    return {"status": "ok", "app": "masar_erp", "version": "0.1.0"}
