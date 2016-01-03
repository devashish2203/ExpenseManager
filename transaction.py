from enum import Enum
from datetime import datetime


class Transaction(object):
	"""Class Representing a single transaction"""
	def __init__(self, matcher, bank):
		#__metaclass__ = MetaTransaction
		self.merchant = matcher.group("merchant").strip()[:-1]
		self.date = datetime.strptime(matcher.group("date"), "%d-%b-%y").date()
		self.cardNo = matcher.group("cardNo")
		self.amount = matcher.group("amount").replace(",","")
		self.cardType = matcher.group("cardType")
		self.bankName = bank.name
		self.transactionType = bank.transactionType

	def __repr__(self):
		return "Transaction: {5} -> {0} was spent from {1} card with number {2} at {3} on {4}".format(self.amount, self.cardType, self.cardNo, self.merchant, self.date, self.bankName)


class Pattern(Enum):
    CITIBANK_CC = "Rs (?P<amount>[\d,]+\.\d{2}).*(?P<cardType>Credit).*(?P<cardNo>\d{4}X{8}\d{4}) on (?P<date>.*) at (?P<merchant>.*)"
    CITIBANK_DC = "Rs (?P<amount>[\d,]+\.\d{2}).*(?P<cardType>Debit).*(?P<cardNo>\d{4}X{8}\d{4}) on (?P<date>.*) at (?P<merchant>.*)"

class Query(Enum):
    CITIBANK_CC = 'from:citialert.india@citicorp.com subject:Transaction Confirmation'
    CITIBANK_DC = 'from:citialert.indiaDebit@citicorp.com subject:Transaction Confirmation'

class TransactionType(Enum):
	CASH = 0
	CREDITCARD = 1
	DEBITCARD = 2
	NETBANKING = 3

class BankDetails:
	def __init__(self, name, query, pattern, transType):
		self.name = name
		self.query = query
		self.regexPattern = pattern
		self.transactionType = transType


class BankDetails(Enum):
	CITIBANK_CC = BankDetails("CITIBANK_CC", Query.CITIBANK_CC, Pattern.CITIBANK_CC, TransactionType.CREDITCARD)
	CITIBANK_DC = BankDetails("CITIBANK_DC", Query.CITIBANK_DC, Pattern.CITIBANK_DC, TransactionType.DEBITCARD)


if __name__ == "__main__":
	pass