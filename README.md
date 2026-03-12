## Medical Cyber Security – Django & ML Project

### 1. Overview
This project is a **Django-based web application** for medical cyber security analysis.  
It allows users to upload a CSV file containing medical cyber incident descriptions and predicts:
- **Threat Category** (e.g., DDoS, Malware, Phishing, Ransomware)
- **Severity Score** (1–5)
- **Suggested Defense Mechanism** (e.g., Increase Web Security, Monitor for Phishing)

Behind the scenes, the app uses:
- **DeBERTa-based text embeddings** (`transformers`, `torch`)
- **Interpretable ML models** (`imodels`, GREEDY TREE / TAO Tree, KNN, Naive Bayes)
- **Custom evaluation utilities** that generate performance graphs.

The web front-end provides **user authentication**, CSV upload, tabular display of predictions, and visual performance reports.

---

### 2. Tech Stack
- **Backend / Web Framework**: Django 2.1.7
- **Language**: Python 3
- **ML / NLP**:
  - `scikit-learn`, `imodels`, `imbalanced-learn`, `numpy`, `scipy`
  - `transformers`, `torch`, `tensorflow`
  - `pandas`, `matplotlib`, `seaborn`, `wordcloud`, `nltk`
- **Database**:
  - **Django default**: SQLite (`db.sqlite3`) for Django internals
  - **Application auth users**: MySQL database `har_db` (table `users`) via `pymysql`
- **Front-end**:
  - Django templates (`Medical/templates/…`)
  - Static CSS (`styles.css`, `src/*.css`, images in `Medical/static/`)

All Python dependencies are listed in `requirements.txt`.

---

### 3. Project Structure (Key Files & Folders)
- `manage.py` – Django entry point to run the server and management commands.
- `Medical_cyber_security/`
  - `settings.py` – Django configuration (apps, templates, static files, SQLite DB, etc.).
  - `urls.py` – Root URL routing.
  - `wsgi.py` – WSGI entry point.
- `Medical/` – Main application.
  - `views.py` – Core logic:
    - User signup / login / logout using **MySQL** (`har_db.users` table).
    - CSV upload and validation.
    - Pre-processing text with **NLTK** and DeBERTa-based embeddings.
    - Loading pre-trained models from the `model/` folder.
    - Generating predictions and performance metrics/graphs.
  - `models.py` – Django models (if any are defined).
  - `templates/` – HTML templates:
    - `home.html`, `homepage.html` – Landing pages.
    - `login.html`, `signup.html` – Authentication pages.
    - `upload_test_dataset.html` – CSV upload page.
    - `prediction.html` – Shows prediction table and metrics.
    - `base.html` – Base layout.
  - `static/` – Static images used by templates.
- `model/` – Pre-trained ML artifacts:
  - `RoBERT-WE_Threat Category_*.pkl`
  - `RoBERT-WE_Severity Score_*.pkl`
  - `RoBERT-WE_Suggested Defense Mechanism_*.pkl`
  - `X_DeBERTa_word_embeddings.pkl`
- `metrics_calculator.py` – Utility class `MetricsCalculator`:
  - Computes accuracy, precision, recall, F1.
  - Generates confusion matrices and ROC curves.
  - Saves plots to the `results/` folder.
- `graphs.py` – Additional plotting utilities for classifier performance.
- `Dataset/`
  - `Medical_Cybersecurity_Dataset.csv` – Main dataset.
  - `Test_Less.csv` – Smaller test subset.
- `results/` – Auto-generated result plots (`*.png`) for classifiers and metrics.
- `cleaned_data.csv` – Pre-processed version of the dataset (if generated).
- `db.sqlite3` – Django default SQLite database.
- `requirements.txt` – Python dependencies.
- `run_server.bat`, `run_server.ps1`, `run3120.bat` – Helper scripts to run the Django server on Windows.
- `SETUP_DATABASE.md` & `DataBase Code.md` – **MySQL setup instructions** for the `har_db` database and `users` table.

---

### 4. Prerequisites
- **Python** 3.x
- **pip** (Python package manager)
- **MySQL Server** (for the `har_db` database)
- Recommended: **virtual environment** (e.g., `venv`)

On Windows, run commands from **PowerShell** or **Command Prompt**.

---

### 5. Installation & Environment Setup

1. **Clone or extract the project**
   - Place the project folder (this directory) somewhere on your system.

2. **Create and activate a virtual environment (recommended)**
   ```bash
   cd "Medical_cyber_security"
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK resources (first-time only)**
   Inside a Python shell:
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('wordnet')
   ```

5. **Ensure pre-trained model files are present**
   - Confirm that the `model/` directory contains the `.pkl` model files and `X_DeBERTa_word_embeddings.pkl`.
   - These are loaded in `Medical/views.py` as part of the inference pipeline.

---

### 6. MySQL Database Setup (`har_db`)

The application uses a **MySQL database** for user accounts (signup/login).  
Default connection parameters (in `Medical/views.py`):
- **Host**: `localhost`
- **User**: `root`
- **Password**: `root`
- **Database**: `har_db`

You can follow either:
- `SETUP_DATABASE.md` – human-readable guide with SQL commands, or  
- `DataBase Code.md` – formatted SQL script to run.

**Essential steps:**
1. Start MySQL server.
2. Open MySQL Workbench or terminal and run:
   ```sql
   CREATE DATABASE IF NOT EXISTS har_db;
   USE har_db;

   CREATE TABLE IF NOT EXISTS users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(100) NOT NULL UNIQUE,
       password VARCHAR(255) NOT NULL,
       email VARCHAR(150) NOT NULL UNIQUE,
       role VARCHAR(50) DEFAULT 'user',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
   ```
3. If your MySQL credentials differ, edit these constants in `Medical/views.py`:
   - `MYSQL_HOST`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DB`

---

### 7. Django Database Setup (SQLite) & Migrations

Django itself is configured to use **SQLite** (`db.sqlite3`) in `Medical_cyber_security/settings.py`.  
"# Major-Project-Batch-04" 
"# Major-Project-Batch-04" 
