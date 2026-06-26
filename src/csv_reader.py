# src/csv_reader.py
# Reads and validates the recipients CSV file

import csv
from dataclasses import dataclass
from src.validators import validate_email_format


@dataclass
class Recipient:
    """Represents a single email recipient row from the CSV."""
    name: str
    email: str
    company: str
    subject: str


def read_recipients(csv_path: str) -> tuple[list[Recipient], list[str]]:
    """
    Parse the CSV file and return a list of Recipient objects.

    Args:
        csv_path: Path to the recipients CSV file.

    Returns:
        A tuple of (valid_recipients, warnings) where warnings is a list
        of human-readable strings describing skipped rows.
    """
    recipients: list[Recipient] = []
    warnings: list[str] = []
    required_columns = {"name", "email", "company", "subject"}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Check that all required columns are present
        if reader.fieldnames is None:
            warnings.append("CSV file appears to be empty.")
            return recipients, warnings

        actual_columns = {col.strip().lower() for col in reader.fieldnames}
        missing_cols = required_columns - actual_columns
        if missing_cols:
            warnings.append(
                f"CSV is missing required column(s): {', '.join(sorted(missing_cols))}"
            )
            return recipients, warnings

        for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            # Normalise column names to lowercase and strip whitespace
            row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}

            name = row.get("name", "")
            email = row.get("email", "")
            company = row.get("company", "")
            subject = row.get("subject", "")

            # Skip rows with empty email
            if not email:
                warnings.append(f"Row {row_num}: skipped — email field is empty.")
                continue

            # Validate email format
            if not validate_email_format(email):
                warnings.append(
                    f"Row {row_num}: skipped — invalid email format '{email}'."
                )
                continue

            recipients.append(Recipient(name=name, email=email,
                                        company=company, subject=subject))

    return recipients, warnings
