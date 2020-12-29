# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CashbackLedger(Document):
	def on_submit(self):
		doc = frappe.get_doc('Customer', self.customer)
		if self.type == "Credit":
			doc.cashback_balance = int(doc.cashback_balance) + int(self.amount)
			doc.lifetime = int(doc.lifetime) + int(self.amount)
		elif self.type == "Debit":
			doc.cashback_balance = int(doc.cashback_balance) - int(self.amount)
		doc.save()
