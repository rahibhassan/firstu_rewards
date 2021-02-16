import frappe
import requests
from requests.auth import HTTPBasicAuth

@frappe.whitelist()
def create_contact(customername, customermobile, upi_id, amount):

    # Razor pay accepts amount in paisa. This amount is converted to Rupee for calculation inside frappe document
    doc_amount = amount
    amount = amount*100

    # selecting the customer doc
    contact_exist = frappe.db.get_list('Customer',filters={'phone_number': customermobile}, fields=['name'])
    customer = frappe.get_doc("Customer", contact_exist[0]['name'])

    # creating a contact_id for new customer
    if customer.contact_id:
        contact_id = customer.contact_id
    else:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        url = "https://api.razorpay.com/v1/contacts"
        auth = HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
        body =  {
                    "name": customername,
                    "contact": customermobile,
                    "type": "customer",
                }
        req = requests.post(url, headers=headers , auth=auth, json=body)

        contact_id = req.json()['id']    

        customer.contact_id = contact_id
        customer.save()
    
    # Checking if customer has enough cashback balance
    if int(customer.cashback_balance) >= int(doc_amount):
        customer.cashback_balance = int(customer.cashback_balance) - int(doc_amount)
        customer.save()
        resp = create_fund_acc(contact_id, upi_id=upi_id, amount=amount)

        status = resp['status']

        cashback_doc = frappe.get_doc(
        {
            "doctype": "Cashback Ledger",
            "status": status,
            "amount": doc_amount,
            "customer": customer.name,
            "type": "Debit",
            "note": "Cashback Redeemed"
        })
        cashback_doc.submit()
        return(resp)

    else:
        cashback_doc = frappe.get_doc(
        {
            "doctype": "Cashback Ledger",
            "status": "Failed",
            "amount": doc_amount,
            "customer": customer.name,
            "type": "Debit",
            "note": "Cashback Redeem Failed"
        })
        cashback_doc.submit()
        return ("You do not have enough Cashback Balance.")

@frappe.whitelist()
def create_fund_acc(contact_id, upi_id, amount):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    url = "https://api.razorpay.com/v1/fund_accounts"
    auth = HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
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
    auth = HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
    body =  {
                "account_number": "2323230011738168",
                "fund_account_id": fund_id,
                "amount": amount,
                "currency": "INR",
                "mode": "UPI",
                "purpose": "cashback",
                "queue_if_low_balance": False,
            }

    req = requests.post(url, headers=headers , auth=auth, json=body)
    return(req.json())