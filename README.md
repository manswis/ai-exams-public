# Mock Exam Simulator (Astro)

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

To append grouped JSON (the format you shared) into the three domain files:

```bash
python3 scripts/append_questions.py path/to/grouped.json
```

The script validates domains, skips duplicate `id`s, and appends new questions.

## Access codes

The app prompts for a PIN:
- Admin PIN: `M271-1983-AX1Z`
- User PIN: `N271-1983-AX2Z`
