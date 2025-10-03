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
            "cavalcade": re.compile(
                r"^([1-9][A-Z]-[NS]|[NS]-[1-9][A-Z])$"
            ),  # 1A-N, 1A-S, N-1A, N-1B, etc.
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

    def extract_program_data(self, pdf_path: str) -> Dict[str, List[str]]:
        """
        Extract program data from the same PDF pages that contain trek summary tables.

        Returns dict mapping program names to lists of itinerary codes that offer them.
        """
        program_data = {}

        # Pages that contain program grids
        program_pages = {
            19: "12-day",  # 12-day programs
            94: "9-day",  # 9-day programs
            131: "7-day",  # 7-day programs
            168: "cavalcade",  # cavalcade programs
        }

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, trek_type in program_pages.items():
                if page_num > len(pdf.pages):
                    continue

                print(f"Extracting program data from page {page_num} ({trek_type})")
                page = pdf.pages[page_num - 1]

                # Extract tables from this page
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        page_programs = self._process_program_table(
                            table, trek_type, page_num
                        )
                        if page_programs:
                            # Merge programs from this page
                            for program_name, itineraries in page_programs.items():
                                if program_name not in program_data:
                                    program_data[program_name] = []
                                program_data[program_name].extend(itineraries)

        return program_data

    def _process_program_table(
        self, table: List[List[str]], trek_type: str, page_num: int
    ) -> Optional[Dict[str, List[str]]]:
        """
        Process a program table where itinerary codes are columns and programs are rows.

        Returns dict mapping program names to lists of itinerary codes.
        """
        if not table or len(table) < 6:  # Need header + data rows
            return None

        # First row should contain itinerary codes
        header_row = table[0]
        if not header_row or len(header_row) < 2:
            return None

        # Extract itinerary codes from header
        itinerary_codes = []

        # Handle different header formats
        if (
            trek_type == "12-day"
            and len(header_row) > 2
            and str(header_row[1]).strip() == "12-"
        ):
            # 12-day format: column 1 is "12-", remaining columns are numbers
            for i in range(2, len(header_row)):
                number = str(header_row[i]).strip() if header_row[i] else ""
                if number and number.isdigit():
                    code = f"12-{number}"
                    itinerary_codes.append(code)
        else:
            # Standard format: each column contains a complete itinerary code
            for i in range(1, len(header_row)):
                code = str(header_row[i]).strip() if header_row[i] else ""
                if code and self.identify_trek_type(code):
                    itinerary_codes.append(code)

        if not itinerary_codes:
            print(
                f"    No valid itinerary codes found in header row on page {page_num}"
            )
            return None

        print(
            f"    Found {len(itinerary_codes)} itinerary codes: {itinerary_codes[:5]}{'...' if len(itinerary_codes) > 5 else ''}"
        )

        # Determine column offset based on table format
        is_12_day_format = (
            trek_type == "12-day"
            and len(header_row) > 2
            and str(header_row[1]).strip() == "12-"
        )
        column_offset = 2 if is_12_day_format else 1

        # Process program rows (skip first 5 rows: header, difficulty, distance, trail camps, dry camps)
        program_data = {}

        for row_idx, row in enumerate(
            table[5:], 5
        ):  # Start from row 5 (programs start there)
            if not row or len(row) < column_offset + 1:
                continue

            program_name = str(row[0]).strip() if row[0] else ""
            if not program_name:
                continue

            # Clean up program name
            program_name = self._normalize_program_name(program_name)
            if not program_name:
                continue

            # Check which itineraries have this program (marked with 'X')
            program_itineraries = []
            for i, code in enumerate(itinerary_codes, column_offset):
                if i < len(row) and row[i]:
                    cell_value = str(row[i]).strip().upper()
                    if cell_value == "X":
                        program_itineraries.append(code)

            if program_itineraries:
                program_data[program_name] = program_itineraries
                if len(program_itineraries) <= 5:
                    print(f"    {program_name}: {program_itineraries}")
                else:
                    print(f"    {program_name}: {len(program_itineraries)} itineraries")

        return program_data if program_data else None

    def _normalize_program_name(self, raw_name: str) -> Optional[str]:
        """
        Normalize program names to match database entries.
        """
        if not raw_name:
            return None

        # Remove extra whitespace
        name = raw_name.strip()
        if not name:
            return None

        # Skip non-program rows
        skip_patterns = [
            "itinerary numbers",
            "hiking difficulty",
            "distance ",
            "trail camps",
            "dry camps",
        ]

        for pattern in skip_patterns:
            if pattern in name.lower():
                return None

        # Some basic name mapping for common variations
        name_mappings = {
            "Archery - 3 Dimensional": "Range Sports: 3D Archery",
            "Atlatl (Dart-Throwing)": "Range Sports: Atlatl Throwing",
            "Baldy Mountain Hike": "Landmarks: Baldy Mountain",
            "Blacksmithing": "Historical: Blacksmithing",
            "Rock Climbing": "Climbing: Rock Climbing",
            "Astronomy": "STEM: Astronomy",
            "Archaeology": "STEM: Archeology",
            "Tomahawk Throwing": "Range Sports: Tomahawk Throwing",
            "Conservation Project": "Low Impact Camping",
        }

        # Check for exact match first
        if name in name_mappings:
            return name_mappings[name]

        # Return original name for database lookup
        return name

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

        # Extract program data from the same PDF
        program_data = self.extract_program_data(pdf_path)
        if program_data:
            print(
                f"Found program data for {sum(len(itins) for itins in program_data.values())} program-itinerary relationships"
            )

        if dry_run:
            print("\n=== DRY RUN - No database changes will be made ===")
            for code, data in all_treks.items():
                print(f"{code}: {data}")
            if program_data:
                print("\nProgram Data Sample:")
                for program_name in list(program_data.keys())[:5]:
                    itineraries = program_data[program_name]
                    print(f"  {program_name}: {len(itineraries)} itineraries")
            return len(all_treks)

        # Clean up existing data for this year before import
        self._cleanup_existing_data(year)

        # Import into database
        imported_count = self._import_to_database(all_treks, year)

        # Import program data
        if program_data:
            self._import_program_data(program_data, year)

        return imported_count

    def _cleanup_existing_data(self, year: int) -> int:
        """Remove all existing data for the specified year before import"""
        conn = self.connect_db()
        removed_count = 0

        try:
            cursor = conn.cursor()

            print(f"Removing existing {year} data...")

            # First, get count of existing entries
            cursor.execute("SELECT COUNT(*) FROM itineraries WHERE year = ?", (year,))
            existing_count = cursor.fetchone()[0]

            if existing_count == 0:
                print(f"No existing {year} data found.")
                return 0

            print(f"Found {existing_count} existing {year} entries to remove")

            # Delete from related tables first (foreign key constraints)
            # Delete from itinerary_programs
            cursor.execute(
                """
                DELETE FROM itinerary_programs 
                WHERE itinerary_id IN (
                    SELECT id FROM itineraries WHERE year = ?
                )
            """,
                (year,),
            )
            programs_removed = cursor.rowcount

            # Delete from itinerary_camps
            cursor.execute(
                """
                DELETE FROM itinerary_camps 
                WHERE itinerary_id IN (
                    SELECT id FROM itineraries WHERE year = ?
                )
            """,
                (year,),
            )
            camps_removed = cursor.rowcount

            # Finally delete from itineraries
            cursor.execute("DELETE FROM itineraries WHERE year = ?", (year,))
            removed_count = cursor.rowcount

            conn.commit()

            print(
                f"Removed {removed_count} itineraries, {programs_removed} program associations, {camps_removed} camp associations for year {year}"
            )

        except sqlite3.Error as e:
            print(f"Error cleaning up existing data: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

        return removed_count

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

    def _import_program_data(
        self, program_data: Dict[str, List[str]], year: int
    ) -> int:
        """
        Import program data into the itinerary_programs table.

        Returns number of program-itinerary relationships imported.
        """
        conn = self.connect_db()
        imported_count = 0

        try:
            cursor = conn.cursor()

            print(f"\nImporting program data for year {year}")

            # First, get all program IDs and names from database
            cursor.execute("SELECT id, name, code FROM programs")
            db_programs = {row[1]: row[0] for row in cursor.fetchall()}  # name -> id

            # Get all itinerary IDs for this year
            cursor.execute(
                "SELECT id, itinerary_code, trek_type FROM itineraries WHERE year = ?",
                (year,),
            )
            db_itineraries = {
                row[1]: (row[0], row[2]) for row in cursor.fetchall()
            }  # code -> (id, trek_type)

            programs_found = 0
            programs_not_found = []

            for program_name, itinerary_codes in program_data.items():
                program_id = None

                # Try to find program by exact name match
                if program_name in db_programs:
                    program_id = db_programs[program_name]
                    programs_found += 1
                else:
                    # Try fuzzy matching for common variations
                    program_id = self._find_program_by_fuzzy_match(
                        program_name, db_programs
                    )
                    if program_id:
                        programs_found += 1
                    else:
                        programs_not_found.append(program_name)
                        continue

                # Import itinerary-program relationships
                for itinerary_code in itinerary_codes:
                    if itinerary_code in db_itineraries:
                        itinerary_id, trek_type = db_itineraries[itinerary_code]

                        try:
                            # Insert or update itinerary_programs relationship
                            cursor.execute(
                                """
                                INSERT OR REPLACE INTO itinerary_programs 
                                (itinerary_id, program_id, trek_type, is_available, year)
                                VALUES (?, ?, ?, ?, ?)
                            """,
                                (itinerary_id, program_id, trek_type, True, year),
                            )

                            imported_count += 1

                        except sqlite3.Error as e:
                            print(
                                f"Error importing program relationship {program_name} -> {itinerary_code}: {e}"
                            )
                            continue

            conn.commit()

            print(
                f"Successfully imported {imported_count} program-itinerary relationships"
            )
            print(f"Programs found in database: {programs_found}")

            if programs_not_found:
                print(f"Programs not found in database ({len(programs_not_found)}):")
                for prog in programs_not_found[:10]:  # Show first 10
                    print(f"  - {prog}")
                if len(programs_not_found) > 10:
                    print(f"  ... and {len(programs_not_found) - 10} more")

        except sqlite3.Error as e:
            print(f"Database error during program import: {e}")
            conn.rollback()
        finally:
            conn.close()

        return imported_count

    def _find_program_by_fuzzy_match(
        self, program_name: str, db_programs: Dict[str, int]
    ) -> Optional[int]:
        """
        Try to find a program by fuzzy name matching.
        """
        program_lower = program_name.lower()

        # Try partial matches
        for db_name, program_id in db_programs.items():
            db_name_lower = db_name.lower()

            # Check if the extracted program name is contained in a database program name
            if program_lower in db_name_lower or db_name_lower in program_lower:
                return program_id

            # Check for key word matches
            program_words = set(program_lower.split())
            db_words = set(db_name_lower.split())

            # If there's significant word overlap, consider it a match
            if len(program_words & db_words) >= min(2, len(program_words)):
                return program_id

        return None


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
