#!/usr/bin/env python3
"""
Philmont Trek Data Importer

This script extracts trek information from Philmont Itinerary Guidebook PDFs
and imports them into the database. It handles multiple years and formats.

The script looks for tables containing:
- Trek codes (12-1, 9-15, 7-3, 1A-N, etc.)
- Difficulty ratings (C, R, S, SS)
- Distance in miles
- Number of trail camps, dry camps
- Program information

Usage:
    python pdf_import_smart.py --pdf legacy_files/2024-Itinerary-Guidebook.pdf --year 2024
    python pdf_import_smart.py --pdf legacy_files/2025-Itinerary-Guidebook.pdf --year 2025
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pdfplumber


class PhilmontTrekImporter:
    """Imports trek data from Philmont Itinerary Guidebook PDFs"""

    def __init__(self, db_path: str = "philmont_selection.db"):
        self.db_path = db_path
        self.trek_patterns = {
            "12-day": re.compile(r"^12-([1-4]?\d)$"),  # 12-1 through 12-49
            "9-day": re.compile(r"^9-([1-4]?\d)$"),  # 9-1 through 9-49
            "7-day": re.compile(r"^7-([1-4]?\d)$"),  # 7-1 through 7-49
            "cavalcade": re.compile(r"^[1-9][A-Z]-[NS]$"),  # 1A-N, 1A-S, 2B-N, etc.
        }
        self.difficulty_map = {
            "C": "Challenging",
            "R": "Rugged",
            "S": "Strenuous",
            "SS": "Super Strenuous",
        }

    def connect_db(self) -> sqlite3.Connection:
        """Connect to the SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            sys.exit(1)

    def identify_trek_type(self, trek_code: str) -> Optional[str]:
        """Identify the type of trek from its code"""
        for trek_type, pattern in self.trek_patterns.items():
            if pattern.match(trek_code):
                return trek_type
        return None

    def find_trek_tables(self, pdf_path: str) -> List[Tuple[int, Dict]]:
        """
        Find pages containing trek data tables.

        Returns list of (page_number, table_data) tuples
        """
        tables_found = []

        # Define specific pages that contain trek summary tables
        # These are known to be consistent across PDFs
        target_pages = self._find_summary_table_pages(pdf_path)

        with pdfplumber.open(pdf_path) as pdf:
            print(f"Analyzing PDF: {pdf_path} ({len(pdf.pages)} pages)")

            for page_num in target_pages:
                if page_num > len(pdf.pages):
                    continue

                page = pdf.pages[page_num - 1]  # 0-indexed
                print(f"Checking summary table on page {page_num}")

                # Extract tables from this page
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        processed_table = self._process_summary_table(table, page_num)
                        if processed_table:
                            tables_found.append((page_num, processed_table))
                            print(f"  - Found {len(processed_table)} trek entries")

        return tables_found

    def _find_summary_table_pages(self, pdf_path: str) -> List[int]:
        """
        Find pages containing summary tables by searching for specific headers.

        Returns list of page numbers
        """
        target_pages = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""

                # Look for specific table headers
                if "Programs Included in 12-Day Itineraries" in text:
                    target_pages.append(page_num)
                    print(f"Found 12-day summary table on page {page_num}")
                elif "Programs Included in 9-Day Itineraries" in text:
                    target_pages.append(page_num)
                    print(f"Found 9-day summary table on page {page_num}")
                elif "Programs Included in 7-Day Itineraries" in text:
                    target_pages.append(page_num)
                    print(f"Found 7-day summary table on page {page_num}")
                elif "Programs Included in Cavalcade Itineraries" in text:
                    target_pages.append(page_num)
                    print(f"Found cavalcade summary table on page {page_num}")

        return target_pages

    def _process_summary_table(
        self, table: List[List[str]], page_num: int
    ) -> Optional[Dict[str, Dict]]:
        """
        Process a summary table where trek codes are columns and data are rows.

        Returns dict mapping trek codes to their data
        """
        if (
            not table or len(table) < 4
        ):  # Need at least header + difficulty + distance + trail camps
            return None

        # First row should contain trek codes
        header_row = table[0]
        if not header_row or len(header_row) < 2:
            return None

        # Extract trek codes from header (skip first column which is the row label)
        trek_codes = []

        # Handle special case for 12-day treks where the prefix and numbers are in separate columns
        if len(header_row) > 2 and str(header_row[1]).strip() == "12-":
            # 12-day format: column 1 is "12-", remaining columns are numbers
            for i in range(2, len(header_row)):
                number = str(header_row[i]).strip() if header_row[i] else ""
                if number and number.isdigit():
                    code = f"12-{number}"
                    if self.identify_trek_type(code):
                        trek_codes.append(code)
        else:
            # Standard format: each column contains a complete trek code
            for i in range(1, len(header_row)):
                code = str(header_row[i]).strip() if header_row[i] else ""
                if code and self.identify_trek_type(code):
                    trek_codes.append(code)

        if not trek_codes:
            print("    No valid trek codes found in header row")
            return None

        print(
            f"    Found {len(trek_codes)} trek codes: {trek_codes[:5]}{'...' if len(trek_codes) > 5 else ''}"
        )

        # Process data rows
        trek_data = {}

        # Initialize trek data for each code
        for code in trek_codes:
            trek_type = self.identify_trek_type(code)
            trek_data[code] = {"trek_type": trek_type}

        # Determine column offset based on table format
        is_12_day_format = len(header_row) > 2 and str(header_row[1]).strip() == "12-"
        column_offset = 2 if is_12_day_format else 1

        # Process each data row
        for row_idx, row in enumerate(table[1:], 1):
            if not row or len(row) < column_offset + 1:
                continue

            row_label = str(row[0]).strip().lower() if row[0] else ""

            # Map row labels to our data fields
            if "difficulty" in row_label:
                for i, code in enumerate(trek_codes, column_offset):
                    if i < len(row) and row[i]:
                        difficulty = str(row[i]).strip().upper()
                        trek_data[code]["difficulty"] = self.difficulty_map.get(
                            difficulty, difficulty
                        )

            elif "distance" in row_label:
                for i, code in enumerate(trek_codes, column_offset):
                    if i < len(row) and row[i]:
                        distance = self._parse_number(str(row[i]))
                        if distance:
                            trek_data[code]["distance"] = distance

            elif "trail" in row_label and "camp" in row_label:
                for i, code in enumerate(trek_codes, column_offset):
                    if i < len(row) and row[i]:
                        trail_camps = self._parse_number(str(row[i]))
                        if trail_camps is not None:
                            trek_data[code]["trail_camps"] = trail_camps

            elif "dry" in row_label and "camp" in row_label:
                for i, code in enumerate(trek_codes, column_offset):
                    if i < len(row) and row[i]:
                        dry_camps = self._parse_number(str(row[i]))
                        if dry_camps is not None:
                            trek_data[code]["dry_camps"] = dry_camps

        # Filter out treks with insufficient data
        valid_treks = {}
        for code, data in trek_data.items():
            if len(data) > 1:  # More than just trek_type
                valid_treks[code] = data
                print(
                    f"    Found: {code} ({data.get('trek_type', 'unknown')}) - {data.get('difficulty', 'N/A')} - {data.get('distance', 'N/A')} mi"
                )

        return valid_treks if valid_treks else None

    def _parse_number(self, text: str) -> Optional[int]:
        """Parse a number from text, handling various formats"""
        if not text:
            return None

        # Extract first number found
        match = re.search(r"\d+", str(text))
        if match:
            return int(match.group())
        return None

    def import_trek_data(self, pdf_path: str, year: int, dry_run: bool = False) -> int:
        """
        Import trek data from PDF into database.

        Returns number of treks imported.
        """
        if not Path(pdf_path).exists():
            print(f"Error: PDF file not found: {pdf_path}")
            sys.exit(1)

        # Find and extract trek tables
        tables = self.find_trek_tables(pdf_path)
        if not tables:
            print("No trek tables found in PDF")
            return 0

        # Consolidate all trek data
        all_treks = {}
        for page_num, table_data in tables:
            all_treks.update(table_data)

        if not all_treks:
            print("No trek data extracted from tables")
            return 0

        print(f"\nFound {len(all_treks)} treks total")

        if dry_run:
            print("\n=== DRY RUN - No database changes will be made ===")
            for code, data in all_treks.items():
                print(f"{code}: {data}")
            return len(all_treks)

        # Import into database
        return self._import_to_database(all_treks, year)

    def _import_to_database(self, trek_data: Dict[str, Dict], year: int) -> int:
        """Import trek data into the database"""
        conn = self.connect_db()
        imported_count = 0

        try:
            cursor = conn.cursor()

            for trek_code, data in trek_data.items():
                try:
                    # Check if itinerary already exists for this year
                    cursor.execute(
                        "SELECT id FROM itineraries WHERE itinerary_code = ? AND year = ?",
                        (trek_code, year),
                    )
                    existing = cursor.fetchone()

                    if existing:
                        print(f"Updating existing trek: {trek_code} (year {year})")
                        self._update_itinerary(cursor, existing["id"], data)
                    else:
                        # Check if there's an entry with the same code but different year
                        cursor.execute(
                            "SELECT id, year FROM itineraries WHERE itinerary_code = ?",
                            (trek_code,),
                        )
                        existing_other_year = cursor.fetchone()

                        if existing_other_year:
                            print(
                                f"Found {trek_code} for year {existing_other_year['year']}, inserting for year {year}"
                            )
                        else:
                            print(f"Inserting new trek: {trek_code} (year {year})")

                        self._insert_itinerary(cursor, trek_code, data, year)

                    imported_count += 1

                except sqlite3.Error as e:
                    print(f"Error importing {trek_code} (year {year}): {e}")
                    continue

            conn.commit()
            print(f"\nSuccessfully imported/updated {imported_count} treks")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            conn.close()

        return imported_count

    def _insert_itinerary(
        self, cursor: sqlite3.Cursor, trek_code: str, data: Dict, year: int
    ):
        """Insert a new itinerary record"""
        cursor.execute(
            """
            INSERT INTO itineraries (
                itinerary_code, trek_type, difficulty, distance, 
                trail_camps, dry_camps, year, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            (
                trek_code,
                data.get("trek_type", "12-day"),
                data.get("difficulty"),
                data.get("distance"),
                data.get("trail_camps"),
                data.get("dry_camps"),
                year,
            ),
        )

    def _update_itinerary(self, cursor: sqlite3.Cursor, itinerary_id: int, data: Dict):
        """Update an existing itinerary record"""
        cursor.execute(
            """
            UPDATE itineraries SET
                difficulty = COALESCE(?, difficulty),
                distance = COALESCE(?, distance),
                trail_camps = COALESCE(?, trail_camps),
                dry_camps = COALESCE(?, dry_camps),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            (
                data.get("difficulty"),
                data.get("distance"),
                data.get("trail_camps"),
                data.get("dry_camps"),
                itinerary_id,
            ),
        )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Import Philmont trek data from PDF guidebooks"
    )
    parser.add_argument("--pdf", required=True, help="Path to the PDF file to import")
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year for the trek data (e.g., 2024, 2025)",
    )
    parser.add_argument(
        "--database",
        default="philmont_selection.db",
        help="Path to SQLite database file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without making changes",
    )

    args = parser.parse_args()

    importer = PhilmontTrekImporter(args.database)

    print(f"Importing trek data from {args.pdf} for year {args.year}")
    if args.dry_run:
        print("(DRY RUN MODE)")

    count = importer.import_trek_data(args.pdf, args.year, args.dry_run)

    if count > 0:
        print(f"\nImport completed: {count} treks processed")
    else:
        print("\nNo treks were imported")


if __name__ == "__main__":
    main()
