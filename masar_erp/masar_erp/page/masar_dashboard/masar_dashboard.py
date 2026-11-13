"""Permission-scoped live dashboard data for MASAR ERP."""
from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_months, get_first_day, get_last_day, getdate, nowdate


def _company(company: str):
    if not company:
        frappe.throw(_("يجب اختيار الشركة"), frappe.ValidationError)
    doc = frappe.get_doc("Company", company)
    if not frappe.has_permission("Company", "read", doc=doc):
        frappe.throw(_("ليس لديك صلاحية الوصول إلى هذه الشركة"), frappe.PermissionError)
    return doc


@frappe.whitelist()
def get_dashboard_data(company: str):
    """Return only live records the logged-in user is allowed to read."""
    if frappe.session.user == "Guest":
        frappe.throw(_("يجب تسجيل الدخول أولاً"), frappe.AuthenticationError)
    _company(company)

    data = {
        "company": company,
        "currency": frappe.get_cached_value("Company", company, "default_currency") or "",
        "period": nowdate(),
        "financial": {"debit": 0, "credit": 0, "net": 0},
        "trend": [],
        "recent_invoices": [],
        "inventory": {"items": 0, "quantity": 0},
    }

    if frappe.has_permission("GL Entry", "read"):
        start = get_first_day(add_months(getdate(nowdate()), -5))
        end = getdate(nowdate())
        entries = frappe.get_list(
            "GL Entry",
            filters={"company": company, "posting_date": ["between", [start, end]], "is_cancelled": 0},
            fields=["debit", "credit", "posting_date"],
            limit_page_length=0,
        )
        monthly = {}
        for row in entries:
            key = row.posting_date.strftime("%Y-%m")
            bucket = monthly.setdefault(key, {"debit": 0, "credit": 0})
            bucket["debit"] += float(row.debit or 0)
            bucket["credit"] += float(row.credit or 0)
            data["financial"]["debit"] += float(row.debit or 0)
            data["financial"]["credit"] += float(row.credit or 0)
        data["financial"]["net"] = data["financial"]["credit"] - data["financial"]["debit"]
        for offset in range(5, -1, -1):
            month = add_months(getdate(nowdate()).replace(day=1), -offset)
            key = month.strftime("%Y-%m")
            values = monthly.get(key, {"debit": 0, "credit": 0})
            data["trend"].append({
                "month": key, "debit": round(values["debit"], 2),
                "credit": round(values["credit"], 2),
            })

    if frappe.has_permission("Sales Invoice", "read"):
        data["recent_invoices"] = frappe.get_list(
            "Sales Invoice",
            filters={"company": company, "docstatus": ["<", 2]},
            fields=["name", "customer", "posting_date", "grand_total", "currency", "status"],
            order_by="posting_date desc, modified desc",
            limit_page_length=6,
        )

    if frappe.has_permission("Bin", "read"):
        warehouses = frappe.get_list(
            "Warehouse", filters={"company": company}, pluck="name", limit_page_length=0
        )
        bins = frappe.get_list(
            "Bin", fields=["item_code", "actual_qty"],
            filters={"warehouse": ["in", warehouses]} if warehouses else {"name": ["=", "__no_matching_warehouse__"]},
            limit_page_length=0,
        )
        data["inventory"] = {
            "items": len({row.item_code for row in bins}),
            "quantity": round(sum(float(row.actual_qty or 0) for row in bins), 3),
        }
    return data
