# Mock Exam Simulator (Astro)

A domain-balanced mock exam simulator with timed exams, persistent progress, analytics, and mobile-friendly UI.

## Quick start

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Deploy (GitHub Pages)

This repo is configured to deploy on pushes to `main` via GitHub Actions.

1. In GitHub repo settings, enable Pages and set Source to **GitHub Actions**.
2. Push to `main`.

## Data files

Question banks are loaded from static JSON files in `public/data`:
- `public/data/questions_people.json`
- `public/data/questions_process.json`
- `public/data/questions_business.json`

## Append grouped questions

To append grouped JSON (the format with `group` + `questions`) into the three domain files:

```bash
python3 public/data/append_questions.py path/to/grouped.json
```

The script:
- Validates domains and required fields
- De-dupes by `questionText`
- Auto-reassigns IDs if a text is new but the ID already exists
- Prints summary counts per domain and group

### Input-only summary

```bash
python3 public/data/append_questions.py --summary-input path/to/grouped.json
```

### Duplicate report (by question text)

```bash
python3 public/data/append_questions.py --report-duplicates path/to/grouped.json
```

### Bank summary (no arguments)

```bash
python3 public/data/append_questions.py
```

## Features

- Domain-balanced exam generation with adjustable ratios
- Strict non-repetition across exams until a domain is exhausted
- Multiple question types: single, multiselect, drag-drop, hotspot, fill-in
- Timer with pause/resume
- Autosave and resume
- Results breakdown by domain + review list
- History analytics with filters
- Mobile layout: stacked question/answers, bottom action bar, navigator drawer
- Resizable panels on desktop (left/right) and mobile (up/down), persisted in localStorage
- Factory reset and layout reset
- Theme switcher (system/light/dark)

