"""
CSV Import utility for Prism application.
Handles importing transactions from CSV files with validation and error handling.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CSVImportError(Exception):
    """Custom exception for CSV import errors."""

    pass


class CSVImporter:
    """Handles CSV file imports for transactions."""

    REQUIRED_FIELDS = ["date", "amount", "category"]
    OPTIONAL_FIELDS = ["type", "description"]
    DATE_FORMATS = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
    ]

    def __init__(self, db_manager):
        """
        Initialize CSV importer.

        Args:
            db_manager: DatabaseManager instance for saving transactions
        """
        self.db_manager = db_manager

    def validate_csv_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate CSV file structure and accessibility.

        Args:
            file_path: Path to CSV file

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        # Check file is readable
        if not os.access(file_path, os.R_OK):
            return False, f"File is not readable: {file_path}"

        # Check file extension
        if not file_path.lower().endswith(".csv"):
            return False, "File must be a CSV file (.csv extension)"

        # Check file is not empty
        if os.path.getsize(file_path) == 0:
            return False, "File is empty"

        # Try to read and validate headers
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames

                if not headers:
                    return False, "CSV file has no headers"

                # Normalize headers (lowercase, strip whitespace)
                headers = [h.lower().strip() for h in headers]

                # Check for required fields
                missing_fields = [
                    field for field in self.REQUIRED_FIELDS if field not in headers
                ]

                if missing_fields:
                    return (
                        False,
                        f"Missing required columns: {', '.join(missing_fields)}",
                    )

            return True, ""

        except UnicodeDecodeError:
            return False, "File encoding error. Please use UTF-8 encoding"
        except csv.Error as e:
            return False, f"CSV parsing error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string in various formats.

        Args:
            date_str: Date string to parse

        Returns:
            Date in YYYY-MM-DD format or None if parsing fails
        """
        date_str = date_str.strip()

        for date_format in self.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return None

    def parse_amount(self, amount_str: str) -> Optional[float]:
        """
        Parse amount string, handling various formats.

        Args:
            amount_str: Amount string to parse

        Returns:
            Float amount or None if parsing fails
        """
        # Remove common formatting characters
        amount_str = amount_str.strip()
        amount_str = amount_str.replace("€", "")
        amount_str = amount_str.replace("$", "")
        amount_str = amount_str.replace(",", ".")
        amount_str = amount_str.replace(" ", "")

        # Handle negative amounts in parentheses (accounting format)
        if amount_str.startswith("(") and amount_str.endswith(")"):
            amount_str = "-" + amount_str[1:-1]

        try:
            return float(amount_str)
        except ValueError:
            return None

    def normalize_category(self, category: str) -> str:
        """
        Normalize category name.

        Args:
            category: Raw category string

        Returns:
            Normalized category name
        """
        # Capitalize first letter of each word
        return category.strip().title()

    def import_from_csv(
        self,
        file_path: str,
        skip_duplicates: bool = True,
        default_type: str = "personal",
    ) -> Tuple[int, int, List[str]]:
        """
        Import transactions from CSV file.

        Args:
            file_path: Path to CSV file
            skip_duplicates: Whether to skip duplicate transactions
            default_type: Default transaction type if not specified

        Returns:
            Tuple of (successful_imports, failed_imports, error_messages)
        """
        logger.info(f"Starting CSV import from: {file_path}")

        # Validate file first
        is_valid, error_msg = self.validate_csv_file(file_path)
        if not is_valid:
            logger.error(f"CSV validation failed: {error_msg}")
            raise CSVImportError(error_msg)

        successful = 0
        failed = 0
        errors = []

        # Track existing transactions to detect duplicates
        existing_transactions = set()
        if skip_duplicates:
            all_transactions = self.db_manager.get_all_transactions()
            for trans in all_transactions:
                # Create a tuple of key fields for comparison
                key = (trans["date"], trans["amount"], trans["category"])
                existing_transactions.add(key)

        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)

                # Normalize headers
                reader.fieldnames = [h.lower().strip() for h in reader.fieldnames]

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 (1 is header)
                    try:
                        # Parse date
                        date_str = row.get("date", "").strip()
                        if not date_str:
                            errors.append(f"Row {row_num}: Missing date")
                            failed += 1
                            continue

                        date = self.parse_date(date_str)
                        if not date:
                            errors.append(
                                f"Row {row_num}: Invalid date format '{date_str}'. "
                                f"Expected formats: YYYY-MM-DD, DD/MM/YYYY, etc."
                            )
                            failed += 1
                            continue

                        # Parse amount
                        amount_str = row.get("amount", "").strip()
                        if not amount_str:
                            errors.append(f"Row {row_num}: Missing amount")
                            failed += 1
                            continue

                        amount = self.parse_amount(amount_str)
                        if amount is None:
                            errors.append(
                                f"Row {row_num}: Invalid amount '{amount_str}'"
                            )
                            failed += 1
                            continue

                        # Parse category
                        category = row.get("category", "").strip()
                        if not category:
                            errors.append(f"Row {row_num}: Missing category")
                            failed += 1
                            continue
                        category = self.normalize_category(category)

                        # Parse type (optional)
                        trans_type = row.get("type", default_type).strip().lower()
                        if trans_type not in ["personal", "investment"]:
                            trans_type = default_type

                        # Parse description (optional)
                        description = row.get("description", "").strip()

                        # Check for duplicates
                        if skip_duplicates:
                            key = (date, amount, category)
                            if key in existing_transactions:
                                logger.debug(
                                    f"Row {row_num}: Skipping duplicate transaction"
                                )
                                failed += 1
                                errors.append(
                                    f"Row {row_num}: Duplicate transaction skipped "
                                    f"({date}, {amount}, {category})"
                                )
                                continue

                        # Add transaction to database
                        self.db_manager.add_transaction(
                            date=date,
                            amount=amount,
                            category=category,
                            transaction_type=trans_type,
                            description=description,
                        )

                        # Add to existing set to detect duplicates within the file
                        if skip_duplicates:
                            existing_transactions.add((date, amount, category))

                        successful += 1
                        logger.debug(f"Row {row_num}: Successfully imported")

                    except Exception as e:
                        failed += 1
                        error_msg = f"Row {row_num}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)

        except Exception as e:
            logger.error(f"CSV import error: {str(e)}")
            raise CSVImportError(f"Failed to read CSV file: {str(e)}")

        logger.info(f"CSV import completed: {successful} successful, {failed} failed")
        return successful, failed, errors

    def generate_sample_csv(self, output_path: str) -> None:
        """
        Generate a sample CSV file to help users understand the format.

        Args:
            output_path: Path where sample CSV should be created
        """
        sample_data = [
            {
                "date": "2024-01-15",
                "amount": "-45.50",
                "category": "Food",
                "type": "personal",
                "description": "Grocery shopping",
            },
            {
                "date": "2024-01-20",
                "amount": "3000.00",
                "category": "Salary",
                "type": "personal",
                "description": "Monthly salary",
            },
            {
                "date": "2024-01-22",
                "amount": "-120.00",
                "category": "Transport",
                "type": "personal",
                "description": "Monthly metro pass",
            },
            {
                "date": "2024-01-25",
                "amount": "-89.99",
                "category": "Entertainment",
                "type": "personal",
                "description": "Concert tickets",
            },
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["date", "amount", "category", "type", "description"]
            )
            writer.writeheader()
            writer.writerows(sample_data)

        logger.info(f"Sample CSV generated at: {output_path}")

    def get_import_summary(
        self, successful: int, failed: int, errors: List[str]
    ) -> str:
        """
        Generate a human-readable summary of the import results.

        Args:
            successful: Number of successful imports
            failed: Number of failed imports
            errors: List of error messages

        Returns:
            Formatted summary string
        """
        summary = f"Import Summary:\n"
        summary += f"✓ Successfully imported: {successful} transactions\n"
        summary += f"✗ Failed: {failed} transactions\n"

        if errors:
            summary += f"\nErrors:\n"
            # Show first 10 errors
            for error in errors[:10]:
                summary += f"  • {error}\n"
            if len(errors) > 10:
                summary += f"  ... and {len(errors) - 10} more errors\n"

        return summary
