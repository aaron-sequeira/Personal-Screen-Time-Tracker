# Personal Screen Time Tracker — Data Centric Programming 2026

**Student ID:** A00047976  
**Proposal submission:** GitHub repository, README proposal, and personally observed data  
**Main project:** [Personal Screen Time Tracker](https://github.com/aaron-sequeira/Personal-Screen-Time-Tracker)  
**Measurement tool:** [Daily — my open-source Windows application](https://github.com/aaron-sequeira/Daily)

## 1. Project proposal

### Overview

I plan to investigate how I use my computer each day by building a Python application that stores, validates, analyses and visualises screen-time observations. To measure my activity, I use **Daily**, an open-source Windows application I developed. Daily tracks time spent in applications and windows, provides a daily overview and groups activity into categories. For this assignment I will **look at Daily's Today screen, read the figures myself, and manually enter them into my CSV**. My Python application is a separate project for importing the CSV into SQLite, analysing it with pandas and producing Matplotlib charts.

The purpose is to explore whether my screen time changes between college days and weekends, which activities occupy the most time, and whether daily screen time is related to my self-reported ability to focus.

### Research questions

1. How does my average daily screen time differ between college days and weekends?
2. Which types of activities account for the largest share of my screen time?
3. Is there a relationship between total daily screen time and my own focus rating (1–5)?

These are questions to be tested with my observations; I have not reached any conclusions yet.

## 2. Original data and collection method

I will record **one row per day for my Windows computer**, normally at the end of the day. I will read the values displayed by Daily and manually type them into the Screen Time Tracker, rather than downloading or bulk-exporting Daily's history or accessing an API. I will assign a focus rating on the same day. I will not invent or retrospectively estimate missed days. I will commit the CSV to GitHub on each day I collect data and document gaps or changes to my measurement method.

Daily's native activity categories include **Work, Learning, Communication, Entertainment, Social and Other**. To use the five category columns defined in my Python project consistently, I will record **Learning as education**, **Work as productivity**, **Entertainment as entertainment**, **Social as social**, and **Communication + Other as other**. I will check that the five values total the day's screen time. If Daily's displayed totals do not reconcile because of rounding or classification issues, I will note the issue and resolve the measurement method, not invent an adjustment. Since this measures my PC, `device` will be `Computer`. Daily does not document a device-pickup metric, so I will leave `pickups` blank unless I can personally measure it consistently.

**Important assignment rule:** The dataset is Category 1 (no AI-generated data). I will personally observe and enter the values. The lecturer should confirm that manually recording readings shown by Daily is acceptable for this assignment; I will follow their decision.

### Data dictionary

| Column | Type / unit | How it is recorded |
|---|---|---|
| `date` | Date, YYYY-MM-DD | Date the observation is made |
| `device` | Category | `Computer` (Windows PC monitored by Daily) |
| `total_minutes` | Integer, minutes | Daily total read from Daily |
| `social_minutes` | Integer, minutes | Social category read from Daily |
| `entertainment_minutes` | Integer, minutes | Entertainment category read from Daily |
| `education_minutes` | Integer, minutes | Daily's Learning category |
| `productivity_minutes` | Integer, minutes | Daily's Work category |
| `other_minutes` | Integer, minutes | Daily's Communication and Other categories together |
| `pickups` | Optional integer | Left blank if not directly measurable |
| `day_type` | Category | College, Work, Weekend, Holiday or Other; classified by my day |
| `focus_rating` | Optional integer, 1–5 | My own same-day rating (1 = low focus, 5 = high focus) |

**Data location:** [`data/screen_time.csv`](data/screen_time.csv). The starter CSV contains only a header and is **not yet evidence of collected data**. Real observations must be added before this proposal is submitted as “some data.” At least 20 rows are required for the final assignment; I aim to collect 50 or more if the available time permits.

### Evidence of human collection

I will update the CSV and commit it regularly. I will keep dated collection notes and add genuine photos/screenshots showing my observation process where appropriate, without exposing private window titles or personal content.

## 3. Planned technical implementation

- **CSV / SQLite:** Save manually entered observations in CSV and load them into a local SQLite table.
- **Validation:** Check date format, numeric ranges, permitted categories, uniqueness of date and device, and whether activity minutes add up to the daily total. Optional unavailable values stay blank.
- **SQL:** Use `WHERE`, `GROUP BY`, `ORDER BY`, `AVG` and `COUNT` to answer questions about the dataset.
- **Pandas:** Compare activity categories, daily trends and college-day versus weekend differences.
- **Matplotlib:** Plot total minutes over time, comparisons between categories and a chart of screen time versus focus ratings if enough data is available.
- **Interactive program:** Use a terminal menu to add an observation, view and filter records, run summaries and generate charts with input validation.

## 4. Expected outcomes and limitations

I expect to learn which applications or activities take the most time and whether my habits vary by day type. I will report results only after collecting data. Limitations may include missed days, rounding in Daily's display, changes in category assignment, and the subjectivity of focus ratings. Any correlation between screen time and focus would not prove causation.

## 5. Repository and submission plan

For this **proposal stage**, the repository will contain this `README.md` proposal, the Python project files, and **some real data** in `data/screen_time.csv`. The final submission will include more observations, charts, collection evidence, findings, reflection, and the in-class demonstration required by the brief.

### Project structure

```text
README.md                 # Proposal and project overview
main.py                   # Interactive menu
database.py               # SQLite and CSV validation
analysis.py               # Pandas analysis and charts
requirements.txt          # Python dependencies
tests.py                  # Basic program tests
data/screen_time.csv      # Personally recorded observations (starts empty)
```

### Running the Python project

```bash
python -m pip install -r requirements.txt
python main.py
```

On Windows, `py` may be used instead of `python`. Select the program's option to add today's observation, then commit the updated CSV to GitHub.

### Recording and committing actual observations

```bash
git add README.md data/screen_time.csv
git commit -m "Add screen time observation for YYYY-MM-DD"
git push
```

Use the **actual date** in the commit message. Never commit fabricated or backfilled observations.

## 6. AI use declaration

AI assistance was used to help draft documentation and develop and explain parts of the Python program under the assignment's Category 2 rules. All measured data values must be collected and recorded by me without AI generation, as required by the Category 1 data rule. I will review and be able to explain the submitted code.
