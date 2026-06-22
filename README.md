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
Once running:
- 🌐 Swagger UI: `http://127.0.0.1:8000/docs`

### 🖥️ Running the Frontend
Open `frontend/index.html` directly in a browser, or serve it with any static file server.

---

## 🔌 API Reference

### 🔐 Auth
| Endpoint | Method | Description |
|---|---|---|
| `/auth/signup` | POST | Create account, returns JWT token |
| `/auth/login` | POST | Authenticate, returns JWT token |

### 📊 Datasets
| Endpoint | Method | Description |
|---|---|---|
| `/datasets/upload` | POST | Upload a CSV, returns row/column/missing-value stats |
| `/datasets/` | GET | List the logged-in user's uploaded datasets |

### ⚙️ Experiments
| Endpoint | Method | Description |
|---|---|---|
| `/experiments/train` | POST | Train all 4 models on a chosen dataset + target column |
| `/experiments/` | GET | List the logged-in user's past experiments |

---

## 🐛 Key Engineering Challenges Solved

- 🔐 **CORS blocking signup/login** — diagnosed via browser console (`405 Method Not Allowed` on `OPTIONS`), fixed by adding `CORSMiddleware` to the FastAPI app
- 🧹 **"Could not convert string to float" training error** — fixed by forcing pandas to create true independent copies (`.copy()`) before encoding categorical columns, since in-place edits on dataframe views were silently failing
- 💥 **Frontend crash on signup page** — `auth.js` was attaching a listener to a `loginForm` element that didn't exist on the signup page; fixed with null-checks before attaching event listeners
- 🐍 **PowerShell + curl quoting issues** — switched to PowerShell's native `Invoke-RestMethod` for reliable JSON API testing instead of fighting `curl.exe`'s quote escaping

---

## 🧩 Developer Guidance & Improvements

### 📖 Understanding the Project
- Start with `backend/main.py` to see how everything is wired together
- Follow `backend/ml/trainer.py` to understand the actual training/evaluation logic
- Trace a request from `frontend/js/dashboard.js` → `api.js` → backend routes to see the full flow

### 🚀 Improvement Ideas
- 🎯 Add a prediction endpoint — use a trained model to predict on new user-provided input
- 🗄️ Switch from SQLite to PostgreSQL for persistent production storage
- 📈 Add more algorithms and hyperparameter tuning options
- 🔁 Add experiment history view on the dashboard (not just the latest run)

---

## 🔮 Future Scope

- 🎯 Live prediction interface
- 📊 Support for regression tasks, not just classification
- 🗄️ Persistent cloud database
- 👥 Multi-user collaboration on shared datasets
- 📱 Responsive mobile-first redesign

---

## 🌍 Real-World Applications

- 🎓 Educational tool for understanding model comparison
- 🧪 Rapid prototyping for choosing a baseline ML algorithm
- 💼 Portfolio demonstration of full-stack + ML engineering skills

---

## ✅ Conclusion

MLForge demonstrates a complete, deployed full-stack ML application — from secure authentication and a real data pipeline to multi-model training and live result visualization. Built end-to-end, including learning JavaScript fundamentals from scratch during the project, and deployed live on Render and Netlify.

---

## 👤 Author

**Sabarish** — B.Tech Computer Science, Sathyabama Institute of Science and Technology
🔗 [GitHub](https://github.com/sabarixx)
