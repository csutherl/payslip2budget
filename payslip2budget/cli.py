import argparse
from payslip2budget.parsers.adp import PayslipParser
from payslip2budget.formatters import ynab, mint, everydollar, monarch
from payslip2budget.exporters.exporter import TransactionExporter

FORMATTERS = {
    "ynab": ynab.format,
    "mint": mint.format,
    "everydollar": everydollar.format,
    "monarch": monarch.format,
}

def main():
    parser = argparse.ArgumentParser(description="Convert payslip PDF to budget transactions.")
    parser.add_argument("input", help="Path to the input PDF payslip")
    parser.add_argument("output", help="Path to the output file (e.g. 'output.csv'), '-' for stdout. Omit this when using '--api-config'", nargs="?", default="output.csv")
    parser.add_argument("--format", help="Output format", choices=FORMATTERS.keys(), default="ynab")
    parser.add_argument("--categories", help="Path to custom categories JSON file", default=None)
    parser.add_argument("--payee", help="Payee", default="Employer")
    parser.add_argument("--api-config", help="Path to API configuration file. If set, output is sent to the API and the output arg is unused.", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without making changes")

    args = parser.parse_args()

    # Parse transctions from the payslip
    adp = PayslipParser(args.categories, args.payee)
    transactions = adp.parse_payslip(args.input)

    # Handle output
    if args.api_config is not None:
        exporter = TransactionExporter(config_path=args.api_config, dry_run=args.dry_run)
        exporter.export(transactions, destination="api")
        # args.output is unused so it doesn't matter what the value us
    else:
        formatter = FORMATTERS[args.format]
        formatted_output = formatter(transactions)

        if args.output == "-":
            print(formatted_output)
        else:
            with open(args.output, "w") as f:
                f.write(formatted_output)

if __name__ == "__main__":
    main()
