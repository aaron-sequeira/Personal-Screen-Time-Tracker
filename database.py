"""CSV validation and SQLite persistence for personally observed screen time."""
from __future__ import annotations

import csv
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / 'data' / 'screen_time.csv'
DB_PATH = ROOT / 'data' / 'screen_time.db'
FIELDS = ['date', 'device', 'total_minutes', 'social_minutes',
          'entertainment_minutes', 'education_minutes', 'productivity_minutes',
          'other_minutes', 'pickups', 'day_type', 'focus_rating']
CATEGORIES = ['social_minutes', 'entertainment_minutes', 'education_minutes',
              'productivity_minutes', 'other_minutes']
DAY_TYPES = ('College', 'Work', 'Weekend', 'Holiday', 'Other')
DEVICES = ('Phone', 'Tablet', 'Computer')


def initialize_files() -> None:
    """Create the empty CSV header only if no CSV exists."""
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with CSV_PATH.open('w', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow(FIELDS)


def validate_row(raw: dict[str, str], *, allow_prior_date: bool = True) -> dict:
    """Validate one row without manufacturing missing observations."""
    errors = []
    try:
        observed = date.fromisoformat(str(raw.get('date', '')).strip())
        if observed > date.today():
            errors.append('date must not be in the future')
        if not allow_prior_date and observed != date.today():
            errors.append('new observations must be recorded on the observation date')
    except ValueError:
        errors.append('date must be YYYY-MM-DD')
        observed = None

    device = str(raw.get('device', '')).strip().title()
    if device not in DEVICES:
        errors.append(f'device must be one of {", ".join(DEVICES)}')
    day_type = str(raw.get('day_type', '')).strip().title()
    if day_type not in DAY_TYPES:
        errors.append(f'day_type must be one of {", ".join(DAY_TYPES)}')

    parsed: dict = {'date': observed.isoformat() if observed else None,
                    'device': device, 'day_type': day_type}
    for field in ['total_minutes', *CATEGORIES, 'pickups']:
        value = str(raw.get(field, '')).strip()
        if field == 'pickups' and value == '':
            parsed[field] = None  # Device may not report unlocks/pickups.
            continue
        try:
            number = int(value)
            if str(number) != value and str(number) != value.lstrip('+'):
                raise ValueError
            if number < 0 or number > (1440 if field != 'pickups' else 10000):
                errors.append(f'{field} must be between 0 and {1440 if field != "pickups" else 10000}')
            parsed[field] = number
        except ValueError:
            errors.append(f'{field} must be a whole number' + (' (or blank)' if field == 'pickups' else ''))
            parsed[field] = None

    rating = str(raw.get('focus_rating', '')).strip()
    if rating == '':
        parsed['focus_rating'] = None
    else:
        try:
            n = int(rating)
            if str(n) != rating or not 1 <= n <= 5:
                raise ValueError
            parsed['focus_rating'] = n
        except ValueError:
            errors.append('focus_rating must be 1–5 or blank')
            parsed['focus_rating'] = None

    if all(parsed.get(key) is not None for key in ['total_minutes', *CATEGORIES]):
        if sum(parsed[key] for key in CATEGORIES) != parsed['total_minutes']:
            errors.append('the five category minutes must add up to total_minutes')
    if errors:
        raise ValueError('; '.join(errors))
    return parsed


def read_and_validate_csv() -> list[dict]:
    """Fail the entire import on malformed rows or duplicate dates per device."""
    initialize_files()
    records = []
    problems = []
    seen = set()
    with CSV_PATH.open(newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != FIELDS:
            raise ValueError('CSV header does not match expected columns: ' + ', '.join(FIELDS))
        for line_number, raw in enumerate(reader, start=2):
            try:
                record = validate_row(raw)
                key = (record['date'], record['device'])
                if key in seen:
                    raise ValueError('duplicate date/device: ' + '/'.join(key))
                seen.add(key)
                records.append(record)
            except ValueError as error:
                problems.append(f'Line {line_number}: {error}')
    if problems:
        raise ValueError('CSV validation failed; database was not changed:\n' + '\n'.join(problems))
    return records


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def setup_database(conn: sqlite3.Connection) -> None:
    conn.execute('''CREATE TABLE IF NOT EXISTS screen_time (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        device TEXT NOT NULL CHECK (device IN ('Phone', 'Tablet', 'Computer')),
        total_minutes INTEGER NOT NULL CHECK (total_minutes BETWEEN 0 AND 1440),
        social_minutes INTEGER NOT NULL CHECK (social_minutes BETWEEN 0 AND 1440),
        entertainment_minutes INTEGER NOT NULL CHECK (entertainment_minutes BETWEEN 0 AND 1440),
        education_minutes INTEGER NOT NULL CHECK (education_minutes BETWEEN 0 AND 1440),
        productivity_minutes INTEGER NOT NULL CHECK (productivity_minutes BETWEEN 0 AND 1440),
        other_minutes INTEGER NOT NULL CHECK (other_minutes BETWEEN 0 AND 1440),
        pickups INTEGER CHECK (pickups BETWEEN 0 AND 10000),
        day_type TEXT NOT NULL CHECK (day_type IN ('College', 'Work', 'Weekend', 'Holiday', 'Other')),
        focus_rating INTEGER CHECK (focus_rating BETWEEN 1 AND 5),
        CHECK (social_minutes + entertainment_minutes + education_minutes + productivity_minutes + other_minutes = total_minutes),
        UNIQUE(date, device)
    )''')
    conn.commit()


def load_csv_into_database() -> int:
    """Replace database observations with the fully validated CSV, atomically."""
    rows = read_and_validate_csv()
    with connect() as conn:
        setup_database(conn)
        cols = ', '.join(FIELDS)
        markers = ', '.join('?' for _ in FIELDS)
        with conn:
            conn.execute('DELETE FROM screen_time')
            conn.executemany(f'INSERT INTO screen_time ({cols}) VALUES ({markers})',
                             [[row[field] for field in FIELDS] for row in rows])
    return len(rows)


def add_today_observation(row: dict[str, str]) -> None:
    """Append to the source-of-truth CSV only after validating it and the new row."""
    existing = read_and_validate_csv()
    record = validate_row(row, allow_prior_date=False)
    if any(r['date'] == record['date'] and r['device'] == record['device'] for r in existing):
        raise ValueError('An entry already exists for this date and device; edit the CSV if correcting an observation.')
    with CSV_PATH.open('a', newline='', encoding='utf-8') as file:
        csv.DictWriter(file, fieldnames=FIELDS).writerow(record)
    load_csv_into_database()
