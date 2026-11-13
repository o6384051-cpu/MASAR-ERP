"""Contract tests for the live, company-scoped MASAR dashboard."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "masar_erp" / "masar_erp" / "page" / "masar_dashboard"


def test_dashboard_page_definition_and_role_scope():
    definition = json.loads((PAGE / "masar_dashboard.json").read_text(encoding="utf-8"))
    assert definition["doctype"] == "Page"
    assert definition["page_name"] == "masar-dashboard"
    assert {role["role"] for role in definition["roles"]} == {
        "Accounts User", "Accounts Manager", "System Manager"
    }


def test_dashboard_api_is_authenticated_and_company_scoped():
    source = (PAGE / "masar_dashboard.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    endpoint = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "get_dashboard_data"
    )
    body = ast.unparse(endpoint)
    assert "frappe.session.user == 'Guest'" in body
    assert "_company(company)" in body
    assert "frappe.has_permission" in body
    assert "frappe.get_list" in body
    assert "frappe.get_all" not in body


def test_dashboard_reads_submitted_documents_and_company_currency_values():
    source = (PAGE / "masar_dashboard.py").read_text(encoding="utf-8")
    assert '"docstatus": 1' in source
    assert '"base_grand_total"' in source
    assert '"base_outstanding_amount"' in source
    assert '"GL Entry"' in source
    assert '"Purchase Invoice"' in source
    assert '"Sales Invoice"' in source
    assert '"Journal Entry"' in source


def test_dashboard_javascript_uses_real_api_and_has_no_escaped_template_delimiters():
    source = (PAGE / "masar_dashboard.js").read_text(encoding="utf-8")
    assert "masar_erp.masar_erp.page.masar_dashboard.masar_dashboard.get_dashboard_data" in source
    assert "data-open-doctype" in source
    assert "data-route" in source
    assert "\\\\`" not in source
    assert "\\\\${" not in source
    assert "activeRequest" in source


def test_dashboard_has_mobile_responsive_layout():
    source = (PAGE / "masar_dashboard.css").read_text(encoding="utf-8")
    assert "@media(max-width:900px)" in source
    assert "@media(max-width:520px)" in source
