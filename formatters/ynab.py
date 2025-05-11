
def format(transactions):
    lines = ["Date,Payee,Category,Memo,Outflow,Inflow"]
    for tx in transactions:
        lines.append(f"{tx['Date']},{tx['Payee']},{tx['Category']},{tx['Memo']},{tx['Outflow']},{tx['Inflow']}")
    return "\n".join(lines)
