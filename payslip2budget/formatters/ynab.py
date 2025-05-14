
def format(transactions):
    lines = ["Date,Payee,Category,Memo,Amount"]
    for tx in transactions:
        lines.append(f"{tx['Date']},{tx['Payee']},{tx['Category']},{tx['Memo']},{tx['Amount']}")
    return "\n".join(lines)
