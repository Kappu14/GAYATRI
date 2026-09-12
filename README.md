# Python Crash Course Project

This workspace contains a small collection of Python experiments and one web app.

## Project structure

- `src/art/` – turtle graphics and visual animation experiments
  - `heart_pattern.py`
  - `love_letter_animation.py`
  - `night_sky_animation.py`
  - `spiral_heart.py`
- `src/web/` – web application and server code
  - `keinstein_app.py`
- `data/` – application data and SQLite database
  - `keinstein.db`
- `main.py` – single entry point to launch the web app

## Run the app

From the project root:

```bash
python main.py
```

Then open:

```text
http://127.0.0.1:8002
```

## Notes

- The art scripts are standalone demos and can be run individually.
- The web app stores its database in the `data/` folder so the project stays organized and portable.
