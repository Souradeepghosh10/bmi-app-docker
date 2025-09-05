import os
from datetime import datetime, date
from math import isnan
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, instance_relative_config=True)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
os.makedirs(app.instance_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "bmi.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---------------- Models ----------------
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sex = db.Column(db.String(10), nullable=False)     # 'Boy' or 'Girl'
    age = db.Column(db.Float, nullable=False)          # years (e.g., 12.5)
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --------------- Helpers ----------------
def compute_bmi(weight_kg: float, height_cm: float) -> float:
    h_m = height_cm / 100.0
    if h_m <= 0: return 0.0
    return round(weight_kg / (h_m*h_m), 2)

def bmi_category(bmi: float) -> str:
    # NOTE: For children/adolescents, use BMI-for-age percentiles by sex (WHO/IOTF).
    # This is a simple categorical fallback.
    if bmi <= 0: return "Unknown"
    if bmi < 18.5: return "Underweight"
    if bmi < 25: return "Healthy"
    if bmi < 30: return "Overweight"
    return "Obese"

def age_band(age: float) -> str:
    if age < 6: return "0-5"
    if age < 13: return "6-12"
    if age < 20: return "13-19"
    if age < 40: return "20-39"
    if age < 60: return "40-59"
    return "60+"

# --------------- Routes -----------------
@app.route("/")
def index():
    # Dashboard-like summary
    people = Person.query.order_by(Person.created_at.desc()).limit(10).all()
    total = Person.query.count()
    return render_template("index.html", people=people, total=total)

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        name = request.form["name"].strip()
        sex = request.form["sex"]
        age = float(request.form["age"])
        height_cm = float(request.form["height_cm"])
        weight_kg = float(request.form["weight_kg"])
        bmi = compute_bmi(weight_kg, height_cm)
        cat = bmi_category(bmi)

        p = Person(name=name, sex=sex, age=age, height_cm=height_cm, weight_kg=weight_kg, bmi=bmi, category=cat)
        db.session.add(p); db.session.commit()
        flash("Entry added", "success")
        return redirect(url_for("index"))
    return render_template("add.html", today=date.today().isoformat())

@app.route("/people")
def people():
    q = request.args.get("q", "").strip().lower()
    qry = Person.query
    if q:
        qry = qry.filter(Person.name.ilike(f"%{q}%"))
    rows = qry.order_by(Person.created_at.desc()).all()
    return render_template("people.html", rows=rows, q=q)

@app.post("/delete/<int:pid>")
def delete(pid):
    p = Person.query.get_or_404(pid)
    db.session.delete(p); db.session.commit()
    flash("Deleted", "info")
    return redirect(request.referrer or url_for("people"))

@app.route("/report")
def report():
    # Build data frame
    rows = [{
        "Name": p.name, "Sex": p.sex, "Age": p.age,
        "Height_cm": p.height_cm, "Weight_kg": p.weight_kg,
        "BMI": p.bmi, "Category": p.category,
        "AgeBand": age_band(p.age)
    } for p in Person.query.order_by(Person.created_at.desc()).all()]
    df = pd.DataFrame(rows)
    # Aggregates
    if df.empty:
        sex_avg = {}; band_avg = {}; cat_counts = {}; overall = {"count":0,"avg_bmi":0}
    else:
        sex_avg = df.groupby("Sex")["BMI"].mean().round(2).to_dict()
        band_avg = df.groupby("AgeBand")["BMI"].mean().round(2).to_dict()
        cat_counts = df["Category"].value_counts().to_dict()
        overall = {"count": int(len(df)), "avg_bmi": round(df["BMI"].mean(),2)}
    # Prepare chart data
    chart_sex_labels = list(sex_avg.keys())
    chart_sex_values = list(sex_avg.values())
    chart_band_labels = list(band_avg.keys())
    chart_band_values = list(band_avg.values())
    chart_cat_labels = list(cat_counts.keys())
    chart_cat_values = list(cat_counts.values())
    return render_template("report.html",
                           overall=overall,
                           chart_sex_labels=chart_sex_labels, chart_sex_values=chart_sex_values,
                           chart_band_labels=chart_band_labels, chart_band_values=chart_band_values,
                           chart_cat_labels=chart_cat_labels, chart_cat_values=chart_cat_values,
                           has_data=(not df.empty))

@app.get("/export.csv")
def export_csv():
    rows = [{
        "Name": p.name, "Sex": p.sex, "Age": p.age,
        "Height_cm": p.height_cm, "Weight_kg": p.weight_kg,
        "BMI": p.bmi, "Category": p.category
    } for p in Person.query.order_by(Person.created_at.asc()).all()]
    df = pd.DataFrame(rows)
    csv = df.to_csv(index=False).encode("utf-8")
    return Response(csv, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=bmi-data.csv"})

# --------------- WHO/IOTF integration (optional) ---------------
# To integrate pediatric percentiles:
# 1) Add a table with WHO LMS parameters for BMI-for-age (by sex).
# 2) Compute z-score with LMS and map to percentile bands (e.g., <5th underweight, 5-85 healthy, etc.).
# 3) Replace bmi_category() logic accordingly.
# Keeping this minimal to stay beginner-friendly for now.

if __name__ == "__main__":
    app.run(debug=True)
