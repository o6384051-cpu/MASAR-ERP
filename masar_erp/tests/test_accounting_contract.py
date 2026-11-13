"""Contract tests for MASAR's ERPNext-backed chart-of-accounts API."""
import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_accounting_api_uses_erpnext_account_doctype():
    source = (ROOT / "masar_erp" / "accounting.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

    assert "get_chart_of_accounts" in functions
    assert "create_account" in functions
    assert '@frappe.whitelist()' in source
    assert '"Account"' in source
    assert '"parent_account"' in source
    assert "account.insert()" in source


def test_account_creation_checks_company_parent_and_permissions():
    source = (ROOT / "masar_erp" / "accounting.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    create = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "create_account")
    calls = [node for node in ast.walk(create) if isinstance(node, ast.Call)]
    call_names = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in calls
        if isinstance(node.func, (ast.Attribute, ast.Name))
    }

    assert "has_permission" in call_names
    assert "get_doc" in call_names
    assert "throw" in call_names
    assert "insert" in call_names
    assert "commit" not in call_names  # request transaction is managed by Frappe


def test_account_tree_is_read_in_nested_set_order():
    source = (ROOT / "masar_erp" / "accounting.py").read_text(encoding="utf-8")
    assert 'order_by="lft asc, name asc"' in source
    assert 'filters={"company": company}' in source
