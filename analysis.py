"""Pandas and SQL queries for observed (never generated) screen-time data."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from database import connect, CATEGORIES, ROOT

CHART_DIR = ROOT / 'charts'


def dataframe() -> pd.DataFrame:
    with connect() as conn:
        df = pd.read_sql_query('SELECT * FROM screen_time ORDER BY date, device', conn)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.day_name()
    return df


def summary(df: pd.DataFrame) -> str:
    if df.empty:
        return 'No recorded observations yet. Add real data before analysing.'
    hours = df['total_minutes'].sum() / 60
    output = [f'Observations: {len(df)}', f'Total recorded screen time: {hours:.2f} hours',
              f'Average daily-device screen time: {df.total_minutes.mean():.1f} minutes',
              f'Peak single observation: {df.total_minutes.max()} minutes']
    if df.focus_rating.notna().any():
        output.append(f'Average self-rated focus: {df.focus_rating.mean():.2f}/5')
    return '\n'.join(output)


def sql_insights() -> list[tuple[str, list[tuple]]]:
    queries = [
        ('Average screen time by day type', '''SELECT day_type, ROUND(AVG(total_minutes), 1) AS avg_minutes,
         COUNT(*) AS observations FROM screen_time GROUP BY day_type ORDER BY avg_minutes DESC'''),
        ('Highest screen-time observations', '''SELECT date, device, total_minutes FROM screen_time
         ORDER BY total_minutes DESC LIMIT 5'''),
        ('Average screen time by device', '''SELECT device, ROUND(AVG(total_minutes),1), COUNT(*)
         FROM screen_time GROUP BY device ORDER BY device'''),
        ('Observations with more than 3 hours social use', '''SELECT date, device, social_minutes
         FROM screen_time WHERE social_minutes > 180 ORDER BY social_minutes DESC'''),
    ]
    with connect() as conn:
        return [(title, [tuple(r) for r in conn.execute(query)]) for title, query in queries]


def create_charts(df: pd.DataFrame) -> list[Path]:
    if df.empty:
        return []
    CHART_DIR.mkdir(exist_ok=True)
    saved = []

    def save(filename: str) -> None:
        plt.tight_layout()
        destination = CHART_DIR / filename
        plt.savefig(destination, dpi=150)
        plt.close()
        saved.append(destination)

    daily = df.groupby('date', as_index=True)['total_minutes'].sum().sort_index()
    daily.plot(marker='o', figsize=(9, 4), title='Total Recorded Screen Time by Day')
    plt.xlabel('Date'); plt.ylabel('Minutes (all recorded devices)'); plt.grid(alpha=.25)
    save('daily_screen_time.png')

    df[CATEGORIES].sum().rename(lambda s: s.replace('_minutes', '').title()).plot(
        kind='bar', figsize=(8, 4), title='Screen Time by Activity Category')
    plt.xlabel('Category'); plt.ylabel('Total minutes')
    save('activity_categories.png')

    df.groupby('day_type')['total_minutes'].mean().sort_values().plot(
        kind='barh', figsize=(8, 4), title='Average Screen Time by Day Type')
    plt.xlabel('Average minutes per device observation'); plt.ylabel('Day type')
    save('day_type_comparison.png')

    rated = df.dropna(subset=['focus_rating'])
    if len(rated) >= 2 and rated.focus_rating.nunique() > 1 and rated.total_minutes.nunique() > 1:
        rated.plot.scatter(x='total_minutes', y='focus_rating', figsize=(7, 4),
                           title='Screen Time vs Self-rated Focus')
        plt.xlabel('Minutes'); plt.ylabel('Focus rating (1–5)')
        save('screen_time_vs_focus.png')
    return saved


def filter_records(df: pd.DataFrame, *, device: str = '', day_type: str = '') -> pd.DataFrame:
    result = df
    if device:
        result = result[result.device.str.lower() == device.lower()]
    if day_type:
        result = result[result.day_type.str.lower() == day_type.lower()]
    return result
