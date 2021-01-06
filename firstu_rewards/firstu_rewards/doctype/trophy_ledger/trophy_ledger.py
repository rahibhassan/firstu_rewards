# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document



class TrophyLedger(Document):
	def on_submit(self):
		doc = frappe.get_doc('Customer', self.customer)
		if self.creditdebit == "Credit":
			doc.total_trophies_collected = int(doc.total_trophies_collected) + int(self.trophy_count)
		elif self.creditdebit == "Debit":
			doc.total_trophies_collected = int(doc.total_trophies_collected) - int(self.trophy_count)
		doc.save()
