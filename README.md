# payslip2budget

**Convert your payslip PDF into transactions for YNAB, Mint, EveryDollar, or Monarch.**

`payslip2budget` is a command-line tool that extracts deductions and relevant information from payroll documents (like ADP payslips) and transforms them into budget transactions for your preferred financial tool.

## ✨ Features

- ✅ Extracts line items from ADP-style payslip PDFs  
- ✅ Groups deductions into customizable categories (e.g., HSA, insurance, retirement, taxes)  
- ✅ Outputs CSV files compatible with (disclaimer: only tested with YNAB!):
  - [YNAB (You Need A Budget)](https://www.ynab.com/)
  - [Mint](https://mint.intuit.com/)
  - [EveryDollar](https://www.everydollar.com/)
  - [Monarch](https://www.monarchmoney.com/)
- ✅ Adds an automatic offset deposit transaction to prevent double-counting taxes or deductions  
- ✅ Output to file, stdout (`-`), or send transactions directly to an API endpoint
- ✅ Extensible for new payslip formats, transaction data models, exporters, etc 

## 🛠 Installation

```bash
pip install .
```

or for development use:

```bash
pip install -e .[dev]
```

## 🚀 Usage

```bash
payslip2budget input.pdf output.csv
```

### Arguments

| Argument         | Description                                            |
|------------------|--------------------------------------------------------|
| `input.pdf`      | Path to the PDF payslip file                           |
| `output.csv`     | Output CSV file path (`-` for stdout)                  |
| `--format`       | Output format: `ynab`, `mint`, `everydollar`, `monarch` (default: `ynab`) |

### Example

```bash
payslip2budget my_adp_payslip.pdf -
```

## 🧪 Running Tests

```bash
pytest
```

## 🧠 Future Plans

- Let users supply custom formatters via plugins or JSON templates
- Support for non-ADP payslips
- Configurable category mapping

## TODOs
- update date to the check date if its not it
- match total deductions to the gross - net amount to confirm all lines are captured
- allow for batching pdfs in a directory to generate transactions for multiple payslips

## 📄 License

MIT License