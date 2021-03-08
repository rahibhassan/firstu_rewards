import frappe
import requests
from requests.auth import HTTPBasicAuth
#from decouple import config
from configure import api_key, api_secret, acc_number
import random
import string
import json

#api_key = config('key')
#api_secret = config('secret')


@frappe.whitelist()
def create_contact(upi_id, amount):
    rand_string = ''.join(random.choices(string.ascii_lowercase, k = 7))
    amount = int(amount)
    amount = amount*100
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    url = "https://api.razorpay.com/v1/contacts"
    auth = HTTPBasicAuth(api_key, api_secret)
    body =  {
                "name": rand_string,
                "type": "customer"
            }
    req = requests.post(url, headers=headers , auth=auth, json=body)
    contact_id = req.json()['id']
    resp = create_fund_acc(contact_id, upi_id=upi_id, amount=amount)
    return resp['status'], resp['id']
    
    

@frappe.whitelist()
def create_fund_acc(contact_id, upi_id, amount):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    url = "https://api.razorpay.com/v1/fund_accounts"
    auth = HTTPBasicAuth(api_key, api_secret)
    body =  {
                "contact_id": contact_id,
                "account_type": "vpa",
                "vpa":
                {
                    "address": upi_id
                }
            }

    req = requests.post(url, headers=headers , auth=auth, json=body)
    val = req.json()
    if "error" in val:
        frappe.throw(req.json()["error"]["description"])
    fund_id = req.json()['id']
    resp = create_payout(fund_id, amount)
    return (resp)


@frappe.whitelist()
def create_payout(fund_id, amount):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    url = "https://api.razorpay.com/v1/payouts"
    auth = HTTPBasicAuth(api_key, api_secret)
    body =  {
                "account_number": acc_number,
                "fund_account_id": fund_id,
                "amount": amount,
                "currency": "INR",
                "mode": "UPI",
                "purpose": "cashback",
                "queue_if_low_balance": False,
            }
    req = requests.post(url, headers=headers , auth=auth, json=body)
    val = req.json()
    if "error" in val:
        frappe.throw(req.json()["error"]["description"])
    return(req.json())


@frappe.whitelist(allow_guest=True)
def payout_webhook():
    body = json.loads(frappe.request.data)
    payout_id = body['payload']['payout']['entity']['id']
    payout_status = body['payload']['payout']['entity']['status']
    fuel_doc_exist = frappe.db.get_list('Fuel Payment',filters={'transaction_id': payout_id}, fields=['name'])
    fuel_doc = frappe.get_doc("Fuel Payment", fuel_doc_exist[0]['name'])
    customer = fuel_doc.customer
    customer_doc = frappe.get_doc("Customer", customer)

    if payout_status == "processed":
        fuel_doc.status = payout_status
        fuel_doc.save()

        cashback_doc = frappe.get_doc({
            'doctype': 'Cashback Ledger',
            'customer': customer,
            'amount': fuel_doc.cashback,
            'fuel_payment': fuel_doc.name,
            'fuel_paid_amount': fuel_doc.amount,
            'type': 'Credit',
            'note': 'Cashbhack received for fuel refill',
            'docstatus': 1
        })
        cashback_doc.insert()

        customer_doc.cashback_balance = int(customer_doc.cashback_balance) + int(fuel_doc.cashback)
        customer_doc.lifetime = int(customer_doc.lifetime) + int(fuel_doc.cashback)

        if int(customer_doc.refuel_left) == 0:
            trophy_settings = frappe.get_doc("Trophy Settings")
            customer_doc.total_trophies_collected = int(customer_doc.total_trophies_collected) + int(trophy_settings.trophies)
            customer_doc.refuel_left =  int(trophy_settings.frequency)
            trophy_doc = frappe.get_doc({
                'doctype': 'Trophy Ledger',
                'trophy_count': trophy_settings.trophies,
                'creditdebit': "Credit",
                'note': 'Trophy Earned from refuel',
                'customer': customer,
                'docstatus': 1
            })
            trophy_doc.insert()
        else:
            customer_doc.refuel_left = int(customer_doc.refuel_left) - 1

        customer_doc.save()

    elif payout_status == "pending" or payout_status == "rejected" or payout_status == "failed":
        return ("Something went wrong")

    return(fuel_doc.status)