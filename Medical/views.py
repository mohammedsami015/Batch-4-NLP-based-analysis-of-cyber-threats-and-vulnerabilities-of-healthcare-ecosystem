from sklearn.model_selection import train_test_split
from imodels import TaoTreeClassifier, GreedyTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from sklearn.utils import resample
from imblearn.over_sampling import SMOTE
from django.contrib import messages
from django.contrib.auth import logout as django_logout
from django.conf import settings
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import joblib
import pymysql
import pymysql.cursors
from tqdm import tqdm
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch

import pickle
from collections import Counter
from scipy.special import expit

import seaborn as sns
from wordcloud import WordCloud

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.util import ngrams

from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import Dense, Input, Embedding, Conv1D, GlobalMaxPooling1D, LSTM, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical

from transformers import (
    RobertaTokenizer, RobertaModel,
    BertTokenizer, BertForSequenceClassification,
    XLNetTokenizer, XLNetForSequenceClassification
)
from torch.optim import AdamW

from metrics_calculator import MetricsCalculator
from graphs import GraphPlotter


MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB = 'har_db'

def home_view(request):
    return render(request, "home.html")

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.err.OperationalError as e:
        error_msg = str(e)
        if "Unknown database" in error_msg:
            print(f"Database '{MYSQL_DB}' does not exist. Please create it first.")
        elif "Access denied" in error_msg:
            print(f"Access denied. Please check MySQL username and password.")
        elif "Can't connect" in error_msg:
            print(f"Cannot connect to MySQL server. Please ensure MySQL is running.")
        else:
            print(f"MySQL connection error: {e}")
        return None
    except Exception as e:
        print(f"DB connection failed: {e}")
        return None

def check_user_credentials(username, password):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed. Please check if MySQL is running and the database exists."
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password, role FROM users WHERE username = %s", (username,))
            record = cursor.fetchone()
            if record and record['password'] == password:
                return True, record['role']
            return False, "Invalid username or password."
    except Exception as e:
        print(f"Error checking credentials: {e}")
        return False, f"Database error: {str(e)}"
    finally:
        if conn:
            conn.close()

def register_new_user(username, password, email):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed."
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'user')",
                (username, password, email)
            )
        conn.commit()
        return True, "User registered successfully."
    except pymysql.err.IntegrityError as e:
        if "Duplicate entry" in str(e):
            if "users.username" in str(e):
                return False, "Username already exists."
            elif "users.email" in str(e):
                return False, "Email already exists."
        return False, "Integrity error."
    except Exception as e:
        return False, f"Unexpected error: {e}"
    finally:
        conn.close()

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("username"):
            messages.error(request, "Please log in first.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, "login.html")
        
        valid, result = check_user_credentials(username, password)
        if valid:
            request.session["username"] = username
            request.session["role"] = result
            messages.success(request, f"Welcome, {username}!")
            return redirect("upload_test_dataset")
        else:
            # result contains the error message
            messages.error(request, result if isinstance(result, str) else "Invalid username or password.")
    return render(request, "login.html")

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        success, msg = register_new_user(username, password, email)
        if success:
            messages.success(request, msg)
            return redirect("login")
        else:
            messages.error(request, msg)
    return render(request, "signup.html")

def logout_view(request):
    django_logout(request)
    request.session.flush()
    messages.info(request, "Logged out.")
    return redirect("login")

le = LabelEncoder()
smote = SMOTE(random_state=42)
features_smoted = {}
labels_smoted = {}

def preprocess_data(df, save_path=None, target_cols=None):

    global label_encoders,Y_dict
    label_encoders = {}

    if save_path and os.path.exists(save_path):
        df = pd.read_csv(save_path)
    else:
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))

        def clean_text(text):
            text = str(text).lower()
            tokens = word_tokenize(text)
            tokens = [lemmatizer.lemmatize(t) for t in tokens if t.isalnum() and t not in stop_words]
            return ' '.join(tokens)

        target_df = None
        if target_cols:
            existing_targets = [col for col in target_cols if col in df.columns]
            target_df = df[existing_targets].copy()
            df = df.drop(columns=existing_targets)

        text_columns = df.select_dtypes(include='object').columns
        for col in text_columns:
            df[f'processed_{col}'] = df[col].apply(clean_text)

        df.drop(columns=text_columns, inplace=True)

        if target_df is not None:
            for col in target_df.columns:
                df[col] = target_df[col]

        if save_path:
            df.to_csv(save_path, index=False)

    processed_text_cols = [col for col in df.columns if col.startswith('processed_')]
    non_text_cols = [col for col in df.columns if col not in processed_text_cols + (target_cols if target_cols else [])]

    X_text = df[processed_text_cols].astype(str).agg(' '.join, axis=1)

    X_numeric = df[non_text_cols].values if non_text_cols else None
    if X_numeric is not None and len(X_numeric) > 0:
        X = [f"{text} {' '.join(map(str, numeric))}" for text, numeric in zip(X_text, X_numeric)]
    else:
        X = X_text.tolist()

    Y_dict = {}
    if target_cols:
        for col in target_cols:
            if col in df.columns:
                le = LabelEncoder()
                Y_dict[col] = le.fit_transform(df[col])
                label_encoders[col] = le

    return X, Y_dict

def deberta_feature_extraction(texts, model_name='microsoft/deberta-base', batch_size=32, pooling='mean'):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()

    all_embeddings = []

    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i:i+batch_size]
        encoded_input = tokenizer(batch_texts, padding=True, truncation=True, return_tensors='pt')

        with torch.no_grad():
            model_output = model(**encoded_input)

        token_embeddings = model_output.last_hidden_state
        attention_mask = encoded_input['attention_mask']
        mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

        if pooling == 'mean':
            sum_embeddings = torch.sum(token_embeddings * mask, dim=1)
            sum_mask = mask.sum(dim=1)
            embeddings = sum_embeddings / sum_mask
        else:
            embeddings = token_embeddings[:, 0, :]

        all_embeddings.append(embeddings.cpu().numpy())

    X = np.vstack(all_embeddings)
    return X, model

def feature_extraction(X_text, method='DeBERTa_word_embeddings', model_dir='model', is_train=True):
    x_file = os.path.join(model_dir, f'X_{method}.pkl')

    model_name = 'microsoft/deberta-base'

    if is_train:
        if os.path.exists(x_file):
            X = joblib.load(x_file)
        else:
            X, model = deberta_feature_extraction(X_text, model_name=model_name, pooling='mean')
            os.makedirs(model_dir, exist_ok=True)
            joblib.dump(X, x_file)
    else:
        X, model = deberta_feature_extraction(X_text, model_name=model_name, pooling='mean')

    return X


label_mapping = {
    "Threat Category": ['DDoS', 'Malware', 'Phishing', 'Ransomware'],
    "Severity Score": [1, 2, 3, 4, 5],
    "Suggested Defense Mechanism": [
        'Increase Web Security',
        'Monitor for Phishing',
        'Patch Vulnerability',
        'Quarantine'
    ]
}

# Get the base directory (Medical_cyber_security folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

Proposed_Model = {
    "Threat Category_GREEDY_TREE": joblib.load(os.path.join(MODEL_DIR, "RoBERT-WE_Threat Category_GREEDY_TREE_model.pkl")),
    "Severity Score_GREEDY_TREE": joblib.load(os.path.join(MODEL_DIR, "RoBERT-WE_Severity Score_GREEDY_TREE_model.pkl")),
    "Suggested Defense Mechanism_GREEDY_TREE": joblib.load(os.path.join(MODEL_DIR, "RoBERT-WE_Suggested Defense Mechanism_GREEDY_TREE_model.pkl")),
}


@login_required
def upload_test_dataset_view(request):
    return render(request, "upload_test_dataset.html")

@login_required
def predict_view(request):
    if request.method == "POST" and request.FILES.get("testfile"):
        try:
            print("File uploaded:", request.FILES["testfile"].name)

            # Read CSV directly from uploaded file (NO saving)
            df_test = pd.read_csv(request.FILES["testfile"])

            if df_test.empty:
                return render(request, "prediction.html", {
                    "table": "<h3 style='color:red;'>Uploaded file is empty!</h3>"
                })

            # Preprocess
            X_test_text, _ = preprocess_data(df_test, save_path=None, target_cols=None)

            # DeBERTa Features
            features_test = feature_extraction(
                X_test_text,
                method='DeBERTa_word_embeddings',
                is_train=False
            )

            df_result = df_test.copy()

            # Predictions
            predictions_by_target = {}
            for target in ['Threat Category', 'Severity Score', 'Suggested Defense Mechanism']:
                model_key = f"{target}_GREEDY_TREE"

                print("Predicting:", model_key)

                y_pred = Proposed_Model[model_key].predict(features_test)
                predictions_by_target[target] = y_pred
                mapped_labels = [label_mapping[target][int(i)] for i in y_pred]
                df_result[f'Predicted_{target}'] = mapped_labels

            # If the uploaded file already contains ground-truth columns, compute metrics and save graphs
            performance_notes = []
            metrics_tables = {}

            for target in ['Threat Category', 'Severity Score', 'Suggested Defense Mechanism']:
                if target not in df_test.columns:
                    continue  # no ground truth provided for this target

                try:
                    true_values = df_test[target].tolist()
                    mapping = label_mapping[target]
                    # Convert true labels to index positions matching the model outputs
                    y_true = [mapping.index(val) for val in true_values]
                    y_pred = predictions_by_target.get(target)
                    if y_pred is None:
                        performance_notes.append(f"{target}: predictions not available, skipped.")
                        continue
                    model_key = f"{target}_GREEDY_TREE"
                    model = Proposed_Model[model_key]

                    # Try to fetch probability scores for ROC if the model supports it
                    y_score = None
                    if hasattr(model, "predict_proba"):
                        try:
                            y_score = model.predict_proba(features_test)
                        except Exception as prob_err:
                            print(f"predict_proba unavailable for {model_key}: {prob_err}")

                    mc = MetricsCalculator(labels=mapping)
                    mc.calculate_metrics(model_key, y_pred, y_true, y_score=y_score)
                    metrics_tables[target] = mc.plot_classification_graphs().to_html(index=False)

                    performance_notes.append(f"{target}: saved graphs in 'results' folder.")
                except ValueError as ve:
                    # True labels in file did not match expected mapping
                    performance_notes.append(f"{target}: skipped metrics (label mismatch: {ve}).")
                except Exception as eval_err:
                    performance_notes.append(f"{target}: skipped metrics due to error: {eval_err}")

            print("Final Result:")
            print(df_result.head())

            return render(request, "prediction.html", {
                "table": df_result.to_html(index=False),
                "metrics_tables": metrics_tables,
                "performance_notes": performance_notes,
            })

        except Exception as e:
            return render(request, "prediction.html", {
                "table": f"<h3 style='color:red;'>Error: {str(e)}</h3>"
            })

    return render(request, "upload_test_dataset.html")
