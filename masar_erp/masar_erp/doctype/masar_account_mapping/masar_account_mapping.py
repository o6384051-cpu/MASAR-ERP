"""Validation for company-scoped MASAR posting-account mappings."""
from __future__ import annotations

import frappe
from frappe.model.document import Document


class MasarAccountMapping(Document):
    def validate(self):
        if not self.company or not self.mapping_type or not self.account:
            frappe.throw("الشركة ونوع التوجيه والحساب حقول إلزامية", frappe.ValidationError)

        account = frappe.get_doc("Account", self.account)
        if account.company != self.company:
            frappe.throw("يجب أن ينتمي الحساب إلى الشركة المحددة", frappe.ValidationError)
        if account.is_group:
            frappe.throw("لا يمكن توجيه الحركة إلى حساب تجميعي", frappe.ValidationError)
        if account.disabled:
            frappe.throw("لا يمكن استخدام حساب معطل في التوجيه", frappe.ValidationError)

        if self.cost_center:
            cost_center = frappe.get_doc("Cost Center", self.cost_center)
            if cost_center.company != self.company:
                frappe.throw("يجب أن ينتمي مركز التكلفة إلى الشركة المحددة", frappe.ValidationError)

        existing = frappe.get_all(
            "MASAR Account Mapping",
            filters={"company": self.company, "mapping_type": self.mapping_type},
            pluck="name",
            limit_page_length=2,
        )
        if any(name != self.name for name in existing):
            frappe.throw("يوجد توجيه نشط أو محفوظ لهذا النوع في الشركة", frappe.ValidationError)
