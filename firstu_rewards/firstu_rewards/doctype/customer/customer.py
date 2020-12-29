# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Customer(Document):
	pass
	# def validate(self):
	# 	trophy = frappe.get_doc('Trophy Settings')
	# 	if int(self.total_fuel_paid) == 0:
	# 		self.total_trophies_collected = int(self.total_trophies_collected) + int(trophy.trophies)
	# 		self.total_fuel_paid = self.total_fuel_paid 
	# 	# if int(self.total_fuel_paid) == int(trophy.frequency):
	# 	# 	self.total_trophies_collected = int(self.total_trophies_collected) + int(trophy.trophies)
	# 	# 	self.total_fuel_paid = 0

