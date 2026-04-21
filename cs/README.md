# AI Credit Scoring System

An end-to-end full-stack web application that evaluates loan applicants using machine learning. Developed by **Team Blind**, this system handles everything from synthetic data generation and predictive modeling to an interactive React dashboard for visualization.

## 🌟 Key Features

- **Predictive ML Engine:** Uses an optimized **XGBoost** model to predict credit scores and repayment probabilities based on applicant data (income, transactions, bills, savings, etc.).
- **Model Explainability:** Integrates **SHAP** (SHapley Additive exPlanations) to provide the top driving factors for every credit decision, ensuring transparency.
- **RESTful API Backend:** A robust **Flask** backend with **SQLAlchemy** (SQLite) to log applicant data, store scoring audits, and expose model predictions.
- **Interactive Dashboard:** A dynamic **React.js** frontend to register applicants, request credit scores, and review analytical metrics.
- **Easy Setup & Deployment:** Fully containerized via **Docker Compose**, alongside a comprehensive `setup.sh` script for local bare-metal installations.

## 🛠️ Tech Stack

**Frontend:**
- **React.js** (Create React App)
- HTML5 / CSS3

**Backend & Data:**
- **Python 3** framework with **Flask**
- **SQLAlchemy** & **SQLite** (Relational Database)
- Pytest (for API unit tests)

**Machine Learning:**
- **XGBoost**, **Scikit-learn**, **Imbalanced-learn**
- **SHAP** for interpretability
- **Pandas** & **Numpy** for data manipulation

**DevOps & Infrastructure:**
- **Docker** & **Docker Compose**
- Bash automation (`setup.sh`)

## 📂 Project Structure

```
.
├── backend/
│   ├── api/             # Flask API endpoints (app.py)
│   ├── data/            # Synthetic dataset generator
│   ├── model/           # XGBoost training pipeline
│   ├── tests/           # Unit tests
│   ├── database.py      # SQLAlchemy schemas
│   ├── requirements.txt # Python dependencies
│   └── score_cli.py     # Command-line scoring tool
├── frontend/
│   ├── public/
│   ├── src/             # React App components and logic
│   └── package.json     # Node modules and scripts
├── docker-compose.yml   # Multi-container orchestration
└── setup.sh             # Interactive local setup script
```

## 🚀 Getting Started

### Option 1: Docker (Recommended)
Make sure you have [Docker](https://www.docker.com/) and Docker Compose installed.

```bash
# Build and run all services in the background
docker-compose up --build -d
```
- **Frontend Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:5000

---

### Option 2: Automated Local Setup
If you are on Linux/macOS or Git Bash (Windows), use the enclosed setup script. It generates the data, trains the initial model, and links the environments.

```bash
chmod +x setup.sh
./setup.sh
```

### Option 3: Manual Installation

**1. Setup Backend & Train Model**
```bash
cd backend
pip install -r requirements.txt
python data/generate_data.py   # Generate synthetic applicants
python model/train.py          # Train the XGBoost model
python api/app.py              # Start the API server
```

**2. Setup Frontend**
*In a new terminal window:*
```bash
cd frontend
npm install
npm start                      # Start the React development server
```

## 🧪 Running Tests
You can verify the backend integrity by running `pytest`.
```bash
cd backend
pytest tests/ -v
```

## 📝 License
This project was developed by **Team Blind**. Please feel free to use, modify, or extend the system as needed.
