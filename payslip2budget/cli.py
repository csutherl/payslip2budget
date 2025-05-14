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
    parser.add_argument("output", help="Path to the output file, '-' for stdout, or 'api' to send via configured API", nargs="?", default="output.csv")
    parser.add_argument("--format", help="Output format", choices=FORMATTERS.keys(), default="ynab")
    parser.add_argument("--categories", help="Path to custom categories JSON file", default=None)
    parser.add_argument("--payee", help="Payee", default="Employer")
    parser.add_argument("--api-config", help="Path to API configuration file (required if output is 'api')", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without making changes")

    args = parser.parse_args()

    # Parse transctions from the payslip
    adp = PayslipParser(args.categories, args.payee)
    transactions = adp.parse_payslip(args.input)

    # Handle output
    # TODO: specifing the api-config arg should be enough, default output to None and send to the api when the config is used or error if no output and no api-config arg
    if args.output == "api":
        if not args.api_config:
            parser.error("--api-config is required when output is 'api'")

        exporter = TransactionExporter(config_path=args.api_config, dry_run=args.dry_run)
        exporter.export(transactions, destination="api")

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
