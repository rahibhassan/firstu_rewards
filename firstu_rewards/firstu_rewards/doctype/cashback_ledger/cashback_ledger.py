# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CashbackLedger(Document):
	pass
	# def on_submit(self):
	# 	self.status = "Success"

	# def after_insert(self):
	# 	if self.type == "Debit":
	# 		cus_doc = frappe.get_doc("Customer", self.customer)
	# 		if int(cus_doc.cashback_balance) >= int(self.amount):
	# 			cus_doc.cashback_balance = int(cus_doc.cashback_balance) - int(self.amount)
	# 			self.note = "Cashback transferred succesfully"
	# 			self.status = "Success"
	# 			cus_doc.save()
	# 		else:
	# 			self.status = "Failed"
	# 			self.note = "Not enough balance"

	# 	doc = frappe.get_doc("Cashback Ledger", self.name)
	# 	doc.submit()