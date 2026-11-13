"""Contract tests for MASAR's ERPNext-backed accounting APIs."""
import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_accounting_api_uses_erpnext_account_doctype():
    source = (ROOT / "masar_erp" / "accounting.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}

    assert {"get_chart_of_accounts", "create_account", "get_account_mappings"} <= set(functions)
    assert source.count("@frappe.whitelist()") == 3
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

    assert {"has_permission", "get_doc", "throw", "insert"} <= call_names
    assert "commit" not in call_names  # Frappe owns the request transaction


def test_account_tree_is_read_in_nested_set_order():
    source = (ROOT / "masar_erp" / "accounting.py").read_text(encoding="utf-8")
    assert 'order_by="lft asc, name asc"' in source
    assert 'filters={"company": company}' in source


def test_mapping_doctype_is_company_scoped_and_role_protected():
    path = ROOT / "masar_erp" / "masar_erp" / "doctype" / "masar_account_mapping" / "masar_account_mapping.json"
    definition = json.loads(path.read_text(encoding="utf-8"))
    fields = {field["fieldname"]: field for field in definition["fields"]}
    roles = {permission["role"] for permission in definition["permissions"]}

    assert {"company", "mapping_type", "account", "cost_center", "active"} <= set(fields)
    assert fields["company"]["options"] == "Company"
    assert fields["account"]["options"] == "Account"
    assert {"Accounts Manager", "System Manager", "Accounts User"} <= roles


def test_mapping_controller_rejects_cross_company_and_group_accounts():
    source = (
        ROOT / "masar_erp" / "masar_erp" / "doctype" / "masar_account_mapping" /
        "masar_account_mapping.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    validate = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "validate"
    )
    checks = ast.unparse(validate)

    assert "account.company != self.company" in checks
    assert "account.is_group" in checks
    assert "account.disabled" in checks
    assert "cost_center.company != self.company" in checks
