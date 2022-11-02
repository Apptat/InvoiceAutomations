import requests
import json
import csv
from datetime import datetime
import stripe
import math
import os

def createInvoice():
    dateRangeStart, dateRangeEnd = getDateRanges()
    timesheetJson = getTimeSheetForDateRange(dateRangeStart=dateRangeStart, dateRangeEnd=dateRangeEnd)
    moneyCents = getMoneyInCents(timesheetJson=timesheetJson)
    createStripeInvoice(moneyCents=moneyCents)
    os.system("open \"\" https://dashboard.stripe.com/test/invoices")

def getDateRanges():
    year = datetime.now().year
    month = getMonth()
    day = getDay(month=month)

    dateRangeStart = str(year) + "-" + month + "-01T00:00:00.000" 
    dateRangeEnd = str(year) + "-" + month + "-" + str(day) + "T23:59:59.000" 

    return dateRangeStart, dateRangeEnd
def getMonth():
    month = input("Enter invoice month: ")
    if int(month) < 10:
        month = "0" + month
    return month
def getDay(month):
    day = 31
    if month == "04" or month == "06" or month == "09" or month == "11": 
        day = 30
    elif month == "02":
        day = 28
    return day    
def getTimeSheetForDateRange(dateRangeStart, dateRangeEnd):
    url = ""
    workspace = ""
    apiKey = ""

    body = json.dumps({
    "dateRangeStart": dateRangeStart,
    "dateRangeEnd": dateRangeEnd,
    "summaryFilter": {
        "groups": [
        "MONTH"
        ]
    },
    "exportType": "JSON"
    })

    headers = {
    'X-Api-Key': apiKey,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=body)
    responseJson = json.loads(response.content)
    return responseJson

def getMoneyInCents(timesheetJson):
    totalSeconds = timesheetJson["totals"][0]["totalTime"]
    hours = totalSeconds / 60 / 60

    # rounds up to nearest 2 decimal places
    def ceil(number, digits) -> float: return math.ceil((10.0 ** digits) * number) / (10.0 ** digits)
    money = ceil((hours * 85) * 1.015, 2)

    moneyCents = int(money * 100)
    return moneyCents

def createStripeInvoice(moneyCents):
    stripe.api_key = ""
    testCustomer = ""
    invoicePrice = buildStripeProduct(moneyCents=moneyCents)
    buildStripeInvoice(invoicePrice=invoicePrice, customer=testCustomer)


def buildStripeProduct(moneyCents):
    price = stripe.Product.create(
        name="Agro-K Development",
        default_price_data={
            "unit_amount": moneyCents,
            "currency": "usd",
        },
        expand=["default_price"],
        )

    prices = stripe.Price.list(limit=1)
    invoicePrice = prices["data"][0]["id"]
    return invoicePrice

def buildStripeInvoice(invoicePrice, customer):
    # Create an Invoice
    invoice = stripe.Invoice.create(
        customer=customer,
        collection_method='send_invoice',
        days_until_due=30,
    )

    stripe.InvoiceItem.create(
        customer=customer,
        price=invoicePrice,
        invoice=invoice.id
    )

if __name__ == "__main__":
    createInvoice()