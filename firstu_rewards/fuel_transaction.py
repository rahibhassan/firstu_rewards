import frappe
import requests
from requests.auth import HTTPBasicAuth
#from decouple import config
from configure import api_key, api_secret, acc_number
import random
import string

#api_key = config('key')
#api_secret = config('secret')


@frappe.whitelist()
def create_contact(customername, upi_id, amount):
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
    return(req.json())