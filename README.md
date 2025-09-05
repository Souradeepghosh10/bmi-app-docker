# BMI App (Flask + SQLite)

Simple BMI calculator + reports for **boys and girls**.

## Features
- Add entries: name, age, sex, height (cm), weight (kg)
- Automatic BMI + **category** (Underweight / Healthy / Overweight / Obese)
- List & delete entries
- **Reports**: averages by sex, age-band breakdown, distribution chart
- **CSV export**
- Clean **Bootstrap** UI and **Chart.js** charts

> Pediatric note: BMI cutoffs for children should ideally use **age & sex percentiles** (WHO/IOTF). 
> This starter uses general categories for simplicity. You can integrate WHO tables later (see comments in `app.py`).

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FLASK_APP=app.py       # Windows: set FLASK_APP=app.py
flask run --debug
```
Open http://127.0.0.1:5000
