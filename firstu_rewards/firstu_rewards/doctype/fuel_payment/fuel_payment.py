# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
from requests.auth import HTTPBasicAuth
#from decouple import config
from firstu_rewards.fuel_transaction import create_contact
from configure import api_key, api_secret, acc_number

#api_key = config('key')
#api_secret = config('secret')


class FuelPayment(Document):
	def validate(self):
		self.customer_doc = frappe.get_doc('Customer', self.customer)
		fuel_doc = frappe.get_doc('Fuel Price')
		fuel_type = self.customer_doc.fuel_type
		membership_type = self.customer_doc.membership_type

		if fuel_type == "Petrol":
			fuel_today = fuel_doc.petrol
			if membership_type == "Status":
				fuel = fuel_doc.petrol_status
			elif membership_type == "Privilege":
				fuel = fuel_doc.petrol_privilege
		elif fuel_type == "Diesel":
			fuel_today = fuel_doc.diesel
			if membership_type == "Status":
				fuel = fuel_doc.diesel_status
			elif membership_type == "Privilege":
				fuel = fuel_doc.diesel_privilege

		litre_filled = round(int(self.amount) / int(fuel_today), 2)
		self.litres = litre_filled
		self.market_value = fuel_today
		self.customer_value = fuel
		cashback = int(fuel_today) * int(litre_filled) - int(fuel) * int(litre_filled)
		self.cashback = cashback

		

	def before_submit(self):
		
		if self.customer_payment_status:
			if self.customer_payment_status == "Success":
				self.status = create_contact("petrol_pump", self.merchant_id, self.amount)
				if self.status == "processed" or self.status == "processing":
					self.cashback_doc = frappe.get_doc({
						'doctype': 'Cashback Ledger',
						'customer': self.customer,
						'amount': self.cashback,
						'fuel_payment': self.name,
						'fuel_paid_amount': self.amount,
						'type': 'Credit',
						'note': 'Cashbhack received for fuel refill'
					})

					self.customer_doc.cashback_balance = int(self.customer_doc.cashback_balance) + int(self.cashback)
					self.customer_doc.lifetime = int(self.customer_doc.lifetime) + int(self.cashback)

					if int(self.customer_doc.refuel_left) == 0:
						trophy_settings = frappe.get_doc("Trophy Settings")
						self.customer_doc.total_trophies_collected = int(self.customer_doc.total_trophies_collected) + int(trophy_settings.trophies)
						self.customer_doc.refuel_left =  int(trophy_settings.frequency)
						trophy_doc = frappe.get_doc({
							'doctype': 'Trophy Ledger',
							'trophy_count': trophy_settings.trophies,
							'creditdebit': "Credit",
							'note': 'Trophy Earned from refuel',
							'customer': self.customer,
							'docstatus': 1
						})
					else:
						self.customer_doc.refuel_left = int(self.customer_doc.refuel_left) - 1

				
					self.customer_doc.save()
					self.cashback_doc.submit()
				elif self.customer_payment_status == "Failure":
					self.status = "Failed"	
			elif self.customer_payment_status == "Failure":
				self.status = "Failed"
		