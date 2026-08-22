# REMYBLE (Remy Reminder)

![Language](https://img.shields.io/badge/language-Python-blue)

## Table of Contents
- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Authors and License](#authors-and-license)

## About

REMYBLE is a small Windows desktop prototype, "Remy Reminder," built with PyQt6. It sits in the system tray and shows a frameless, always-on-top popup at scheduled times of day, reading its schedule from a CSV file. The user must actively dismiss a reminder as "Done" or "Doing (Snooze)" rather than it disappearing passively. A companion "Settings" window (also always-on-top) lets the user view, add, edit, and delete rows of the CSV in a table widget, and any save automatically reschedules the next popup. This is an early, working proof-of-concept for a much larger planned mobile app described in the repo's planning notes (see [Roadmap](#roadmap)) — a personal utility/learning project rather than a finished product.

## Prerequisites
- Python 3.x
- PyQt6 (no `requirements.txt` is included in the repository; this dependency is inferred directly from the imports in `current/remy_reminder.py`)

## Installation
```bash
git clone https://github.com/successjoseph/REMYBLE.git
cd REMYBLE/current
pip install PyQt6
```

## Configuration
The app is driven entirely by `reminders.csv` (two columns: `Time`, `Reminder`, e.g. `10:00,Hey Nymo! Time to build Remy!`). If the file doesn't exist when the app starts, it is auto-created with five default entries. There is no `.env` or other config file; `.gitignore` in this repo is empty (0 bytes).

## Usage
```bash
python remy_reminder.py
```
This launches a system tray icon with a right-click menu: **Show Reminder Now** (pops a random reminder immediately), **Settings** (opens the CSV editor table), and **Exit**. The app calculates the soonest upcoming reminder time from the CSV and schedules a single-shot timer for it; if no valid times are found it falls back to firing a random reminder every 2 hours. Each popup has "Done" and "Doing (Snooze)" buttons.

Note: the repository contains two copies of the reminders data — `current/reminders.csv` (used by the script, since it runs from the `current/` directory) and a root-level `reminders.csv` (an older/duplicate copy).

## Testing
No automated tests are currently included.

## Roadmap
The `creation logs/text/` folder contains the original product vision this prototype is working toward — a full Android app named "Remy," described in both `idea.txt` and `Project {NAMELESS} — Your Attentive Task.txt`. The planned app would add: an "Away From Work"-style Focus App detection gate, swipe-based Done/Doing gestures, a gamified profile with streaks and points, four task categories (Major/Minor/Wakeup/Before Bed), a full theme engine, and a freemium Pro tier (Focus Mode, analytics, voice setup, dynamic theming) with a gamified free trial ladder based on completion streaks. None of that mobile/gamification layer is implemented yet — the current code is a Windows desktop CSV-driven precursor to that vision.

## Contributing
This is a personal project and prototype — these notes are for the author's own future reference.

## Authors and License
**Author:** [successjoseph](https://github.com/successjoseph)
No license file included in this repository — all rights reserved by default.
