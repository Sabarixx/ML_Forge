# ⚒️ MLForge — ML Experimentation Platform

## 🔍 Overview

**MLForge** is a full-stack machine learning experimentation platform — upload a dataset, train multiple ML algorithms simultaneously, and compare their performance through an interactive dashboard.

Built to demonstrate full-stack engineering skills alongside applied ML — from authentication and database design to model training pipelines and live data visualization.

🔗 **Live Demo:** [https://agent-6a3821c0f88d11--symphonious-phoenix-b11977.netlify.app/signup]

🔗 **API Docs:** https://ml-forge.onrender.com/docs

---

## 🎯 Objectives

- 🔐 Build secure, JWT-based user authentication from scratch
- 📊 Allow users to upload their own datasets and see instant stats
- ⚙️ Train multiple ML algorithms simultaneously on the same data
- 📈 Visually compare model performance through tables and charts
- 🗄️ Persist experiment history per user
- 🚀 Deploy a real, fully working full-stack app — not just a local demo

---

## 🛠️ Technologies Used

### 💻 Programming Languages
- Python
- JavaScript, HTML, CSS

### ⚙️ Backend Framework
- FastAPI
- Uvicorn
- SQLAlchemy + SQLite

### 🤖 Machine Learning
- scikit-learn (Logistic Regression, Decision Tree, Random Forest, KNN)
- pandas

### 🔐 Auth & Security
- python-jose (JWT tokens)
- passlib + bcrypt (password hashing)

### 🎨 Frontend
- Vanilla HTML/CSS/JavaScript
- Chart.js (results visualization)

### ☁️ Deployment
- Render (backend)
- Netlify (frontend)

---

## 🏗️ System Architecture

MLForge follows a clean **client → API → database/ML pipeline** architecture.

**Flow:**
User uploads CSV → Backend parses & stores it → User selects target column → Backend trains 4 models → Results saved & returned → Dashboard renders table + chart

**Detailed Steps:**
1. 🔐 User signs up / logs in → receives a JWT token
2. 📤 User uploads a CSV → backend parses it with pandas, extracts row/column/missing-value stats
3. 🗄️ Dataset metadata is saved to the database, file stored on disk
4. ⚙️ User selects a dataset + target column → clicks "Train All Models"
5. 🧹 Backend auto-cleans the data (drops missing values, encodes categorical columns)
6. 🤖 Trains Logistic Regression, Decision Tree, Random Forest, and KNN on an 80/20 split
7. 📊 Accuracy, precision, and recall for all 4 models returned and displayed

---

## 📂 Project Folder Structure

| Path | Purpose |
|---|---|
| `backend/main.py` | FastAPI entry point, CORS, router wiring |
| `backend/database.py` | SQLAlchemy engine & session setup |
| `backend/models.py` | `User`, `Dataset`, `Experiment` tables |
| `backend/config.py` | Environment variable handling |
| `backend/routers/auth_routes.py` | Signup, login, JWT verification |
| `backend/routers/datasets_routes.py` | Upload & list datasets |
| `backend/routers/experiment_routes.py` | Train models, list experiments |
| `backend/ml/trainer.py` | Model training & evaluation logic |
| `frontend/index.html` | Login page |
| `frontend/signup.html` | Signup page |
| `frontend/dashboard.html` | Main dashboard (upload, train, results) |
| `frontend/js/api.js` | Centralized fetch wrapper with JWT handling |
| `frontend/js/auth.js` | Login/signup form logic |
| `frontend/js/dashboard.js` | Upload, training, and results rendering |

---

## ⚙️ Installation and Setup Guidelines

### 📌 Prerequisites
- Python 3.11+
- A modern web browser
- Basic familiarity with running a local server

### 🔧 Backend Setup
