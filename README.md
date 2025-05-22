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
| `output.csv`     | Output CSV file path (`-` for stdout). This argument is ignored if `--api-config` is used. |
| `--format`       | Output format: `ynab`, `mint`, `everydollar`, `monarch` (default: `ynab`) |
| `--api-config`   | Path to the API configuration JSON file (e.g., `api-config.json`). If provided, transactions are sent directly to the configured API, and `output.csv` and `--format` arguments are ignored. |

### Example

```bash
payslip2budget my_adp_payslip.pdf -
```

### Using the YNAB API Exporter

To send your transactions directly to YNAB instead of exporting to a CSV file, you'll use the `--api-config` command-line argument. This section guides you through setting up the necessary `api-config.json` file.

#### 1. Obtain Your YNAB Personal Access Token

To allow `payslip2budget` to send transactions to your YNAB account, you need to generate a Personal Access Token (API Key).

Here's how to get it:

1.  Log in to your YNAB account in a web browser.
2.  Go to the "My Account" section. You can usually find this by clicking your budget name in the top-left corner and then selecting "My Account" from the dropdown.
3.  Navigate to the "Developer Settings" tab.
4.  Click "New Token".
5.  Enter a descriptive name for the token (e.g., "payslip2budget_token") and click "Create".
6.  **Important:** YNAB will show you the token only once. Copy it immediately and store it in a safe place. You will need this for the `api-config.json` file.

For more detailed instructions, you can visit the official YNAB documentation: [Link to YNAB API Documentation - To be added]

#### 2. Find Your Budget ID

The `budget_id` tells `payslip2budget` which of your YNAB budgets to use.

1.  In your web browser, open the YNAB budget you want to use.
2.  Look at the URL in your browser's address bar. It will look something like this:
    `https://app.ynab.com/your_long_budget_id_string/budget/2024-07`
3.  The `your_long_budget_id_string` part is your Budget ID. Copy this string.
    *Example:* If your URL is `https://app.ynab.com/a1b2c3d4-e5f6-7890-1234-567890abcdef/budget/2024-07`, your `budget_id` is `a1b2c3d4-e5f6-7890-1234-567890abcdef`.

#### 3. Find Your Account ID

The `account_id` specifies which account within your selected budget will receive the transactions.

1.  In YNAB, navigate to the budget you'vechosen.
2.  Click on the specific account in the left sidebar that you want `payslip2budget` to send transactions to (e.g., "Checking Account").
3.  Look at the URL in your browser's address bar again. It will change to something like:
    `https://app.ynab.com/your_long_budget_id_string/accounts/your_long_account_id_string`
4.  The `your_long_account_id_string` part is your Account ID. Copy this string.
    *Example:* If your URL is `https://app.ynab.com/a1b2c3d4-e5f6-7890-1234-567890abcdef/accounts/z9y8x7w6-v5u4-3210-fedc-ba9876543210`, your `account_id` is `z9y8x7w6-v5u4-3210-fedc-ba9876543210`.

#### 4. Create Your `api-config.json` File

`payslip2budget` uses a configuration file named `api-config.json` to store your YNAB API credentials. You'll need to create this file in the same directory where you run the `payslip2budget` command, or you can provide a path to it using a command-line argument (support for this may vary).

1.  Create a new file named `api-config.json`.
2.  Copy the structure from the example file `payslip2budget/exporters/apihandlers/api-config.json.example`.
3.  Replace the placeholder values with your actual YNAB Personal Access Token, Budget ID, and Account ID that you collected in the previous steps.

Here's what the structure should look like:

```json
{
  "api": {
    "type": "ynab",
    "api_key": "YOUR_YNAB_PERSONAL_ACCESS_TOKEN",
    "budget_id": "YOUR_BUDGET_ID",
    "account_id": "YOUR_ACCOUNT_ID"
  }
}
```

**Important Security Note:** Treat your `api-config.json` file like a password. Do **not** commit it to version control (e.g., Git) if you are working in a shared repository. The `.gitignore` file in this project should already be configured to ignore `api-config.json`, but it's good practice to be aware of this.

#### 5. Ensure Categories Exist in YNAB

The `payslip2budget` tool will attempt to match the categories found in your payslip (as defined in your `categories.json` mapping) to categories in your YNAB budget.

*   **Case Sensitivity:** This matching is case-sensitive. For example, "Medical" is different from "medical".
*   **Category Groups:** If you use category groups in YNAB (e.g., "Obligations:Rent"), ensure both the group and the category name match what `payslip2budget` will use. The YNAB API handler in this tool expects categories in the format `CategoryGroup:CategoryName` (e.g., `Insurance:Medical`). If a category isn't in a group, use just the category name (e.g., `Groceries`).
*   **Missing Categories:** If a category from your payslip data does not exist in YNAB under the specified budget, the API call will fail, and an error message will be displayed.

Before running the exporter, please verify that all categories you expect to be transferred are already set up in your YNAB budget with the exact same naming (including case and group structure if applicable).

#### 6. (Optional) Understanding Payee Handling

The YNAB API handler will attempt to match payee names from your payslip data to existing payees in your YNAB budget.

*   **Matching:** The matching is case-insensitive (e.g., "Employer Name" will match "employer name").
*   **New Payees:** If a payee name from the payslip does not exactly match an existing payee in YNAB, YNAB's API *may* create a new payee. However, for better control and to ensure consistency (e.g., avoiding slight variations like "Employer Inc." vs "Employer Inc"), you might prefer to pre-populate common payees in your YNAB account beforehand.
*   **No Payee ID in `api-config.json`:** Unlike `account_id` or `budget_id`, you do not need to specify individual `payee_id`s in the `api-config.json`. The script looks up payees by name.

Reviewing your YNAB payees after the first few imports can help you manage and merge any unintentionally created duplicates.

### Using the Google Sheets API Exporter

This exporter allows you to send your processed payslip transactions directly to a Google Sheet. It is also invoked using the `--api-config` flag, but you will need to create a specific configuration file for Google Sheets.

#### 1. Prerequisites - Google Cloud Setup

Before you can use this exporter, you need to set up a project in Google Cloud Console and get API credentials.

1.  **Create or Select a Project:** Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project or select an existing one.
2.  **Enable Google Sheets API:**
    *   Navigate to the "APIs & Services" > "Library".
    *   Search for "Google Sheets API" and enable it for your project.
3.  **Create OAuth 2.0 Credentials:**
    *   Go to "APIs & Services" > "Credentials".
    *   Click "+ CREATE CREDENTIALS" and select "OAuth client ID".
    *   For "Application type", choose "Desktop app".
    *   Give it a name (e.g., "payslip2budget-sheets-client").
    *   After creation, a pop-up will show your Client ID and Client Secret. Click "OK".
    *   On the Credentials page, find your newly created OAuth client ID and click the **download icon (JSON)** (⬇️) on the right. This will download a `client_secret_*.json` file.
4.  **Place `credentials.json`:**
    *   Rename the downloaded file to `credentials.json`.
    *   Place this `credentials.json` file in the root directory of the `payslip2budget` project, or in a custom location that you will specify in your `google-sheets-config.json` file (see below).

#### 2. Authentication Flow (`token.json`)

*   **First Run:** The first time you run `payslip2budget` with a Google Sheets API configuration, the tool will attempt to open a web browser. You will be prompted to log in with your Google account and authorize the application to access your Google Sheets on your behalf.
*   **`token.json` Creation:** Upon successful authorization, a `token.json` file will be created in the same directory as your `credentials.json` file. This file stores your access and refresh tokens, so you don't have to re-authorize every time.
*   **Subsequent Runs:** On subsequent runs, the tool will use the stored `token.json` to authenticate. If the token is expired or revoked (e.g., if you manually delete `token.json` or revoke access via your Google account settings), the browser-based authorization flow will be triggered again.
*   **Security Note:** The `credentials.json` and `token.json` files contain sensitive information. **Do NOT commit them to version control (e.g., Git).** Ensure they are listed in your project's `.gitignore` file. The default names `credentials.json` and `token.json` are used by the authentication script.

#### 3. Configuration File (`google-sheets-config.json`)

You need to create a JSON configuration file to tell `payslip2budget` how to connect to your Google Sheet. You will then provide the path to this file using the `--api-config` command-line argument.

See the example configuration file: `payslip2budget/exporters/apihandlers/google-sheets-config.json.example`.

The configuration file requires the following fields:

*   `"api"`: An object containing the Google Sheets specific configuration.
    *   `"type"`: Must be set to `"google_sheets"`.
    *   `"spreadsheet_id"`: The ID of your target Google Spreadsheet. You can find this in the spreadsheet's URL. For example, if your URL is `https://docs.google.com/spreadsheets/d/ABC123xyz789_defGHI/edit#gid=0`, your `spreadsheet_id` is `ABC123xyz789_defGHI`.
    *   `"worksheet_name"` (optional): The name of the specific worksheet (tab) within your spreadsheet where the transactions should be added. If omitted, it defaults to `"Transactions"`. The script will append rows to this worksheet.
    *   `"credentials_json_path"` (optional): The path to your `credentials.json` file. If omitted, it defaults to `"credentials.json"` (expected to be in the current working directory when you run the script).
    *   `"write_mode"` (optional): Specifies how data should be written to the sheet.
        *   `"append"` (default): Adds new transactions after the last existing row in the sheet.
        *   `"overwrite"`: Clears all existing data in the worksheet (including headers) and writes the new transactions. The header row (`Date, Payee, Category, Amount, Memo`) will be written first.

Here's an example of what your `google-sheets-config.json` might look like:

```json
{
  "api": {
    "type": "google_sheets",
    "spreadsheet_id": "YOUR_ACTUAL_SPREADSHEET_ID",
    "worksheet_name": "My Payslip Imports",
    "credentials_json_path": "path/to/your/credentials.json" 
  }
}
```
*(Remember to replace placeholders with your actual data and ensure the path to `credentials.json` is correct if it's not in the default location.)*

#### 4. Usage Example

Once your `credentials.json` is in place and your `google-sheets-config.json` file is created, you can run the exporter:

```bash
payslip2budget your_payslip.pdf --api-config path/to/your/google-sheets-config.json
```

#### 5. Output Columns

The exporter will append rows to your specified worksheet with the following columns, creating the header row if the sheet is empty or the header doesn't match:

1.  `Date`
2.  `Payee`
3.  `Category`
4.  `Amount` (negative for outflows, positive for inflows)
5.  `Memo`

#### 6. Dry Run

You can use the `--dry-run` global flag to see what data would be sent to your Google Sheet without actually writing any data. This is useful for verifying your setup and the parsed transaction data.

```bash
payslip2budget your_payslip.pdf --api-config path/to/your/google-sheets-config.json --dry-run
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