import pdfplumber
from datetime import datetime
import logging
import warnings
import re
import json
import os
import csv

class PayslipParser:
    def __init__(self, category_config=None, payee="Employer"):
        """
        Initialize the parser with an optional category configuration.
        
        Args:
            category_config: Path to JSON config file or a dictionary with 
                             category mappings in format {category: [keywords]}
        """
        self.category_mappings = {
            "Health Savings Account": ["hsa"],
            "Legal": ["legal"],
            "Retirement": ["401(k)", "401k", "roth"],
            "Insurance:Medical": ["medical"],
            "Insurance:Dental": ["dental"],
            "Insurance:Vision": ["vision"],
            "Insurance:Supplemental": [" life"],
            "Taxes:Stock Award Withholding": ["stock offset"],
            "Taxes:Withholding": ["withholding"],
            "Taxes:Social Security": ["social security"],
            "Taxes:Medicare": ["medicare"]
        }
        
        # Load custom configuration if provided
        if category_config:
            self.load_category_config(category_config)

        self.payee = payee
    
    def load_category_config(self, config):
        """
        Load category mappings from a file or dictionary.
        
        Args:
            config: Path to JSON file or dictionary with mappings
        """
        if isinstance(config, str) and os.path.exists(config):
            # Load from file
            try:
                with open(config, 'r') as f:
                    custom_mappings = json.load(f)
                self.category_mappings = custom_mappings
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading category config: {e}")
                print("Using default category mappings")
        elif isinstance(config, dict):
            # Use provided dictionary
            self.category_mappings = config
        else:
            print("Invalid category configuration. Using defaults.")
    
    def categorize_line(self, text):
        """Determine the category of a line item based on configured keywords"""
        text_lower = text.lower()
        
        for category, keywords in self.category_mappings.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                return category
        
        return None

    def parse_payslip(self, pdf_path, output_csv=None):
        """
        Parse a payslip PDF and extract deduction items.
        
        Args:
            pdf_path: Path to the PDF file
            output_csv: Optional path to save results as CSV
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        total_deductions = 0.0
        total_additions = 0.0
        
        # Suppress pdfplumber/pdfminer warnings
        logging.getLogger('pdfminer').setLevel(logging.ERROR)
        warnings.filterwarnings("ignore", message="CropBox missing from /Page, defaulting to MediaBox")
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                lines = page.extract_text().splitlines()
                for line in lines:
                    if "net pay" in line.lower() or "direct deposit" in line.lower():
                        continue
                    
                    # Find all potential deduction items in the line
                    items = self.extract_deduction_items(line)
                    
                    for item_name, amount in items:
                        category = self.categorize_line(item_name)
                        if category:
                            if amount < 0:
                                total_deductions -= amount
                            else:
                                total_additions += amount

                            transactions.append({
                                "Date": datetime.today().strftime('%Y-%m-%d'),
                                "Payee": self.payee,
                                "Category": category,
                                "Memo": item_name.strip(),
                                "Amount": f"{amount:.2f}",
                            })
        
        # Offset deductions with an addition
        if total_deductions > 0:
            transactions.append({
                "Date": datetime.today().strftime('%Y-%m-%d'),
                "Payee": self.payee,
                "Category": "Income:Gross Pay Offset",
                "Memo": "Offset for itemized paycheck deductions",
                "Amount": f"{total_deductions:.2f}"
            })
        
        # Offset additions with a deduction
        if total_additions > 0:
            transactions.append({
                "Date": datetime.today().strftime('%Y-%m-%d'),
                "Payee": self.payee,
                "Category": "Income:Gross Pay Offset",
                "Memo": "Offset for itemized paycheck additions (employer contributions)",
                "Amount": f"-{total_additions:.2f}"
            })

        # Save to CSV if requested
        if output_csv and transactions:
            self.save_to_csv(transactions, output_csv)
        
        return transactions
        
    def save_to_csv(self, transactions, output_path):
        """
        Save transactions to a CSV file.
        
        Args:
            transactions: List of transaction dictionaries
            output_path: Path to save the CSV file
        """
        fieldnames = ["Date", "Payee", "Category", "Memo", "Amount"]
        
        try:
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(transactions)
            print(f"Transactions saved to {output_path}")
        except IOError as e:
            print(f"Error saving CSV: {e}")

    def extract_money_amount(self, text):
        """Extract money amount from text, handling both formats like '100.00' and '100.00-'"""
        # Remove dollar signs and commas
        text = text.replace('$', '').replace(',', '')

        # Handle trailing minus sign
        if text.endswith('-'):
            text = '-' + text[:-1]

        try:
            return float(text)
        except ValueError:
            return None


    def extract_deduction_items(self, line):
        """
        Extract deduction items from a payslip line.
        For each item, grab the first dollar amount (current pay period) and ignore YTD amounts.
        Returns a list of (item_name, amount) tuples for valid deduction items.
        """
        items = []
        
        # Split the line into parts
        parts = line.split()
        if len(parts) < 2:
            return items
        
        # First, identify all text segments that might be item descriptions
        item_segments = []
        current_item = []
        
        for i, part in enumerate(parts):
            # Check if this part is a monetary amount
            amount = self.extract_money_amount(part)
            
            if amount is None:
                # This is part of an item name
                current_item.append(part)
            else:
                # We found a monetary amount - if we have collected words for an item, save it
                if current_item:
                    item_segments.append({
                        'name': ' '.join(current_item),
                        'index': i - len(current_item),
                        'length': len(current_item)
                    })
                    current_item = []
        
        # Add any remaining item at the end
        if current_item:
            item_segments.append({
                'name': ' '.join(current_item),
                'index': len(parts) - len(current_item),
                'length': len(current_item)
            })
        
        # Process each potentially meaningful segment
        for segment in item_segments:
            # Replace * from some items
            item_name = segment['name'].replace("*","")
            category = self.categorize_line(item_name)
            
            if category:
                # Find the first amount that appears after this item name
                start_idx = segment['index'] + segment['length']
                for j in range(start_idx, len(parts)):
                    # If the item is the year-to-date column, then the amount is 0
                    if parts[j] == parts[-1]:
                        amount = 0
                    else:
                        amount = self.extract_money_amount(parts[j])

                    if amount is not None and amount != 0:
                        # We found the first amount for this item - always use the first amount (current period)
                        items.append((item_name, amount))
                        break
        
        # Special handling for items that might need specific detection
        # Flatten all keywords from category mappings to look for special items
        all_keywords = []
        for keywords in self.category_mappings.values():
            all_keywords.extend(keywords)
        
        for keyword in all_keywords:
            if keyword.lower() in line.lower():
                # Find where this keyword appears
                for i, part in enumerate(parts):
                    if keyword.lower() in part.lower():
                        # Check if we already captured this item
                        already_captured = False
                        for item_name, _ in items:
                            if keyword.lower() in item_name.lower():
                                already_captured = True
                                break
                        
                        if already_captured:
                            continue
                        
                        # Find the extent of this item name (look backward and forward)
                        start_idx = i
                        while start_idx > 0 and self.extract_money_amount(parts[start_idx-1]) is None:
                            start_idx -= 1
                        
                        end_idx = i
                        while end_idx < len(parts)-1 and self.extract_money_amount(parts[end_idx+1]) is None:
                            end_idx += 1
                        
                        item_name = ' '.join(parts[start_idx:end_idx+1])
                        
                        # Find the first amount after this item
                        for j in range(end_idx+1, len(parts)):
                            # If the item is the year-to-date column, then the amount is 0
                            if parts[j] == parts[-1]:
                                amount = 0
                            else:
                                amount = self.extract_money_amount(parts[j])

                            if amount is not None and amount != 0:
                                items.append((item_name, amount))
                                break
                        
                        break
        
        # print(f"Extracted items: {items}")
        return items
