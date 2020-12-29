from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def claim(customer, gift):
    customer_doc = frappe.get_doc('Customer', customer)
    gift_doc = frappe.get_doc('Gift', gift)

    if int(customer_doc.total_trophies_collected) >= int(gift_doc.cost):
        gift_claim_doc = frappe.get_doc({
            'doctype': 'Gifts Claim Ledger',
            'gift': gift,
            'trophies_paid': gift_doc.cost,
            'customer': customer
        })

        customer_doc.total_trophies_collected = int(customer_doc.total_trophies_collected) - int(gift_doc.cost)

        trophy_ledger_doc = frappe.get_doc({
            'doctype': 'Trophy Ledger',
            'trophy_count': gift_doc.cost,
            'creditdebit': 'Debit',
            'customer': customer
        })

    elif int(customer_doc.total_trophies_collected) < int(gift_doc.cost):

        gift_claim_doc = frappe.get_doc({
            'doctype': 'Gifts Claim Ledger',
            'gift': gift,
            'trophies_paid': gift_doc.cost,
            'customer': customer,
            'status': 'Failed'
        })

        frappe.throw("Insufficient Trophies")
    
    
    customer_doc.save()
    gift_claim_doc.submit()
    trophy_ledger_doc.submit()