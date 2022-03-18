# Copyright (c) 2022, Arnold DJAPOU and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus

class LibraryTransaction(Document):

	def before_submit(self):
		if self.type == "Emission":
			self.emission_article()
			self.validation_max_limit()
			article = frappe.get_doc("Articl", self.article)
			article.statut = "Emis"
			article.save()

		elif self.type == "Retour":
			self.retour_article()
			article = frappe.get_doc("Articl", self.article)
			article.statut = "Disponible"
			article.save()

	def emission_article(self):
		self.member_exists()
		article = frappe.get_doc("Articl", self.article)

		if article.statut == "Emis":
			frappe.throw("L\'article a deja ete emis par un autre membre")

	def retour_article(self):
		article = frappe.get_doc("Articl", self.article)

		if article.statut == "Disponible":
			frappe.throw("L\'article ne peut pas etre retourne sans au prealable etre emis")

	def validation_max_limit(self):
		max_number = frappe.db.get_single_value("Library Settings", "max_number")
		count = frappe.db.count(
			"Library Transaction",
			{
				"library_member": self.library_member,
				"type": "Emission",
				"docstatus": DocStatus.submitted(),
			}
		)
		if count >= max_number:
			frappe.throw("La limite maximum d\'emission des articles a ete atteint")


	def member_exists(self):
		exists = frappe.db.exists(
			"Library MemberShip",
			{
				"library member": self.library_member,
				"docstatus": DocStatus.submitted(),
				"from_date": ("&lt;", self.date),
				"to_today": (">", self.date),
			},
		)
		if not exists:
			frappe.throw("Ce membre n\'a pas d\'abonnement actif")