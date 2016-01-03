def getTotalSpendsByMonth(transactionsList):
	bucket = {}
	for trans in transactionsList:
		key = str(trans.date).split("-")[1]
		if key in bucket:
			bucket[key] = bucket[key] + float(trans.amount)
		else:
			bucket[key] = float(trans.amount)
	return bucket

def getTotalSpends(transactionsList):
	sum = 0
	for trans in transactionsList:
		sum += float(trans.amount)
	return sum