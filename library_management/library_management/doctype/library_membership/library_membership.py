# Copyright (c) 2022, Arnold DJAPOU and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus

class LibraryMemberShip(Document):

	def before_submit(self):

		exists = frappe.db.exists(
			"Library MemberShip",
			{
				"library_member": self.library_member,
				"docstatus": DocStatus.submitted(),
				"to_today": (">", self.from_date),
			},
		)
		if exists:
			frappe.throw("Un abonnement actif existe deja pour ce membre")

		period_pret = frappe.db.get_single_value("Library Settings", "period_pret")
		self.to_today = frappe.utils.add_days(self.from_date, period_pret or 30)

