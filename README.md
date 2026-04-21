# 🚀 AI Credit Scoring System

## 📌 Description
This project is an AI-powered alternative credit scoring system that evaluates loan applicants using transaction history, utility bill payments, and behavioral data. It combines machine learning with explainable AI to deliver accurate, transparent, and reliable credit decisions through a full-stack web application.

---

## 🚀 Features
- 📊 Predicts creditworthiness using XGBoost  
- 🔍 Explainable AI with SHAP  
- ⚡ REST API built using Flask  
- 💾 Data storage with SQLAlchemy + SQLite  
- 🖥️ Interactive frontend using React.js  
- 🐳 Docker support for deployment  
- 🧪 Backend testing using Pytest  

---

## 🛠️ Tech Stack

### 🎨 Frontend
- React.js  
- HTML5 / CSS3  

### ⚙️ Backend
- Python  
- Flask  
- SQLAlchemy  
- SQLite  

### 🤖 Machine Learning
- XGBoost  
- Scikit-learn  
- Imbalanced-learn  
- SHAP  
- Pandas  
- NumPy  

### 🐳 DevOps
- Docker  
- Docker Compose  
- Bash scripting  

---

## 📂 Project Structure

.
├── backend/
│   ├── api/
│   ├── data/
│   ├── model/
│   ├── tests/
│   ├── database.py
│   ├── requirements.txt
│   └── score_cli.py
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
├── docker-compose.yml
└── setup.sh

---

## ⚡ Getting Started

### ▶️ Run with Docker (Recommended)
docker-compose up --build -d

Frontend → http://localhost:3000  
Backend → http://localhost:5000  

---

### 🔹 Automated Setup
chmod +x setup.sh  
./setup.sh  

---

### 🔹 Manual Setup

Backend:
cd backend  
pip install -r requirements.txt  
python data/generate_data.py  
python model/train.py  
python api/app.py  

Frontend:
cd frontend  
npm install  
npm start  

---

## 🧪 Running Tests
cd backend  
pytest tests/ -v  

---

## ⚙️ How It Works
1. Generate synthetic applicant data  
2. Train ML model  
3. Send data via API  
4. Predict credit score  
5. Explain using SHAP  
6. Display results  

---

## 🔮 Future Improvements
- Authentication system  
- Cloud deployment  
- Advanced analytics  
- Export reports  
- Real-world dataset integration  

---

## 🤝 Contributing
Feel free to fork and contribute.

---

## 📝 License
Free to use and modify for educational purposes.
