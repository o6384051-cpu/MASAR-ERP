"""MASAR accounting APIs built on ERPNext's canonical Account DocType.

The ERPNext Account tree and General Ledger remain the source of truth.
"""
from __future__ import annotations

import frappe


ACCOUNT_FIELDS = [
    "name",
    "account_name",
    "parent_account",
    "root_type",
    "report_type",
    "account_type",
    "is_group",
    "disabled",
    "lft",
    "rgt",
]


def _require_authenticated_user() -> None:
    if frappe.session.user == "Guest":
        frappe.throw("يجب تسجيل الدخول أولاً", frappe.AuthenticationError)


def _get_authorized_company(company: str):
    if not company:
        frappe.throw("يجب تحديد الشركة", frappe.ValidationError)
    company_doc = frappe.get_doc("Company", company)
    if not frappe.has_permission("Company", "read", doc=company_doc):
        frappe.throw("ليس لديك صلاحية الوصول إلى هذه الشركة", frappe.PermissionError)
    return company_doc


@frappe.whitelist()
def get_chart_of_accounts(company: str):
    """Return the permitted company's ERPNext account tree in nested-set order."""
    _require_authenticated_user()
    _get_authorized_company(company)
    if not frappe.has_permission("Account", "read"):
        frappe.throw("ليس لديك صلاحية قراءة دليل الحسابات", frappe.PermissionError)

    return frappe.get_list(
        "Account",
        filters={"company": company},
        fields=ACCOUNT_FIELDS,
        order_by="lft asc, name asc",
        limit_page_length=0,
    )


@frappe.whitelist()
def create_account(
    company: str,
    account_name: str,
    parent_account: str,
    is_group: int = 0,
    account_type: str | None = None,
):
    """Create a child account through ERPNext's normal validation and insert path.

    Root accounts and direct ledger mutations are intentionally not exposed here.
    """
    _require_authenticated_user()
    _get_authorized_company(company)

    if not frappe.has_permission("Account", "create"):
        frappe.throw("ليس لديك صلاحية إنشاء حساب", frappe.PermissionError)

    account_name = (account_name or "").strip()
    parent_account = (parent_account or "").strip()
    if not account_name:
        frappe.throw("اسم الحساب مطلوب", frappe.ValidationError)
    if not parent_account:
        frappe.throw("يجب اختيار الحساب الأب", frappe.ValidationError)

    try:
        is_group = int(is_group)
    except (TypeError, ValueError):
        frappe.throw("قيمة نوع الحساب غير صحيحة", frappe.ValidationError)
    if is_group not in (0, 1):
        frappe.throw("قيمة نوع الحساب غير صحيحة", frappe.ValidationError)

    parent = frappe.get_doc("Account", parent_account)
    if parent.company != company:
        frappe.throw("لا يمكن ربط الحساب بحساب أب من شركة أخرى", frappe.ValidationError)
    if not parent.is_group:
        frappe.throw("الحساب الأب يجب أن يكون حساباً تجميعياً", frappe.ValidationError)
    if parent.disabled:
        frappe.throw("لا يمكن إضافة حساب تحت حساب أب معطل", frappe.ValidationError)

    values = {
        "doctype": "Account",
        "account_name": account_name,
        "company": company,
        "parent_account": parent_account,
        "is_group": is_group,
    }
    if account_type and not is_group:
        values["account_type"] = account_type.strip()

    account = frappe.get_doc(values)
    account.insert()
    return {
        "name": account.name,
        "account_name": account.account_name,
        "parent_account": account.parent_account,
        "company": account.company,
        "is_group": account.is_group,
        "root_type": account.root_type,
        "report_type": account.report_type,
    }
