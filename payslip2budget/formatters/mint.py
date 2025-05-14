
def format(transactions):
    lines = ["Date,Payee,Category,Memo,Amount"]
    for tx in transactions:
        lines.append(f"{tx['date']},{tx['payee']},{tx['category']},{tx['memo']},{tx['amount']}")
    return "\n".join(lines)
