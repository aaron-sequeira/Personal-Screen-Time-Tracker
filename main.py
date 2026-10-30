"""Interactive terminal interface for the Screen Time Tracker assignment."""
from datetime import date
from database import (FIELDS, DEVICES, DAY_TYPES, initialize_files,
                      load_csv_into_database, add_today_observation)
from analysis import dataframe, summary, sql_insights, create_charts, filter_records


def ask_choice(label: str, options: tuple[str, ...]) -> str:
    while True:
        entry = input(f'{label} ({"/".join(options)}): ').strip().title()
        if entry in options:
            return entry
        print('Invalid choice. Please try again.')


def add_observation() -> None:
    print('\nOnly enter data you actually read and recorded TODAY.')
    row = {'date': date.today().isoformat()}
    row['device'] = ask_choice('Device', DEVICES)
    row['day_type'] = ask_choice('Day type', DAY_TYPES)
    for key in ['total_minutes', 'social_minutes', 'entertainment_minutes',
                'education_minutes', 'productivity_minutes', 'other_minutes']:
        row[key] = input(f'{key} (whole minutes): ').strip()
    row['pickups'] = input('Pickups/unlocks (blank if unavailable): ').strip()
    row['focus_rating'] = input('Self-rated focus 1–5 (blank if not recorded): ').strip()
    try:
        add_today_observation(row)
        print('Saved to CSV and SQLite. Commit the CSV to GitHub today.')
    except ValueError as exc:
        print(f'Entry not saved: {exc}')


def menu() -> None:
    initialize_files()
    try:
        count = load_csv_into_database()
        print(f'Loaded {count} validated observations from CSV.')
    except ValueError as exc:
        print(exc)
        print('Correct the CSV and select Reload before analysing.')
    while True:
        print('\n=== SCREEN TIME TRACKER ===')
        print('1. Add today\'s observation')
        print('2. View records / filter')
        print('3. Pandas statistics')
        print('4. SQL queries')
        print('5. Generate charts')
        print('6. Validate and reload CSV')
        print('0. Exit')
        choice = input('Choose an option: ').strip()
        try:
            if choice == '1':
                add_observation()
            elif choice == '2':
                df = dataframe()
                if df.empty:
                    print('No observations yet.')
                    continue
                device = input('Filter by device (or Enter for all): ').strip()
                day_type = input('Filter by day type (or Enter for all): ').strip()
                filtered = filter_records(df, device=device, day_type=day_type)
                print(filtered.to_string(index=False) if not filtered.empty else 'No matching records.')
            elif choice == '3':
                print(summary(dataframe()))
            elif choice == '4':
                for title, rows in sql_insights():
                    print(f'\n{title}:')
                    for row in rows:
                        print('  ', row)
                    if not rows:
                        print('  No matching observations')
            elif choice == '5':
                paths = create_charts(dataframe())
                print('\n'.join(f'Saved: {p}' for p in paths) if paths else 'No data to chart.')
            elif choice == '6':
                print(f'Reloaded {load_csv_into_database()} validated rows.')
            elif choice == '0':
                print('Goodbye!')
                break
            else:
                print('Please enter 0–6.')
        except (ValueError, OSError) as exc:
            print(f'Error: {exc}')
        except (KeyboardInterrupt, EOFError):
            print('\nReturning to menu.')


if __name__ == '__main__':
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print('\nExiting.')
