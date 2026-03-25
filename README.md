# 🔬 LabTrack — Laboratory Sample Management System

A clean, fast, and fully offline-capable sample management app built with **Streamlit + SQLite**.

---

## 📁 Project Structure

```
lab_system/
├── app.py               # Main Streamlit application
├── database.py          # All SQLite CRUD + search operations
├── requirements.txt     # Python dependencies
├── sample_data.csv      # Demo data reference (pre-loaded automatically)
├── lab_samples.db       # SQLite DB (auto-created on first run)
└── .streamlit/
    └── config.toml      # Theme + server config
```

---

## 🚀 Local Setup & Run

### 1. Clone / download the project
```bash
git clone https://github.com/YOUR_USERNAME/labtrack.git
cd labtrack
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```
The app opens at **http://localhost:8501**. The SQLite database and 10 demo records are created automatically on first launch.

---

## 📦 Features

| Module | Capability |
|--------|-----------|
| **Dashboard** | KPI cards (total, businesses, this month, today) · bar chart by business · recent submissions |
| **Add Sample** | Validated form · duplicate Sample ID check · sample stage tracking |
| **Search** | Filter by ID, business, person, stage, date range · sortable results table · CSV export |
| **Edit / Delete** | Full record edit · confirmed permanent delete |

### Sample Stages
`Received → In Progress → Analysis Complete → Report Issued → Archived`

---

## ☁️ Deploy on Streamlit Cloud (Free)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: LabTrack v1.0"
git remote add origin https://github.com/YOUR_USERNAME/labtrack.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New App**
4. Select your repo → branch `main` → Main file path `app.py`
5. Click **Deploy**

> ⚠️ **SQLite persistence note:** Streamlit Cloud's filesystem resets on each deployment.  
> For persistent production storage, replace SQLite with **Supabase (PostgreSQL)** or **TiDB Serverless** — just swap `database.py` connection logic.

---

## 🔄 Updating the App

```bash
# After making changes locally:
git add .
git commit -m "Update: describe your change"
git push origin main
# Streamlit Cloud redeploys automatically within ~30 seconds
```

---

## 🛠️ Customisation Tips

- **Add more sample types:** Edit the `selectbox` list in `app.py`
- **Add authentication:** Use `streamlit-authenticator` package
- **Switch to PostgreSQL:** Replace `sqlite3` in `database.py` with `psycopg2`
- **Add email notifications:** Use `smtplib` after insert in `add_sample()`

---

## 📋 Requirements

- Python 3.9+
- streamlit ≥ 1.32
- pandas ≥ 2.0

---

## 📄 License
MIT — free for personal and commercial use.
