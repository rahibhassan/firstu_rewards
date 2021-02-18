# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.core.doctype.user.user import generate_keys
import random
import string

class Customer(Document):
	def before_save(self):
		if not self.user_id:
			rand_no = random.randrange(10000, 99999, 1)
			rand_string = ''.join(random.choices(string.ascii_lowercase, k = 10))
			service_provider = ['gmail', 'ymail', 'yahoo', 'hotmail']
			provider = random.choices(service_provider)[0]
			rand_email = rand_string + str(rand_no) + '@' + provider + '.com'		
			email = rand_email
		
		
			user_doc = frappe.get_doc({
				'doctype': 'User',
				'email': email,
				'first_name': rand_string,
				'send_welcome_email': 0,
				'role_profile_name': 'FirstU Customer'
				})
			user_doc.insert()

			self.user_id = user_doc.email
			self.api_secret = generate_keys(self.user_id)['api_secret']
			self.api_key = frappe.db.get_value('User', self.user_id, 'api_key')
			frappe.db.commit()

	
			self.owner = self.user_id