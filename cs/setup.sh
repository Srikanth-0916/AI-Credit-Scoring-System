#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  AI Credit Scoring System — Full Setup Script
#  Run:  chmod +x setup.sh && ./setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e  # Exit on any error

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════╗"
echo "║   AI Credit Scoring System — Setup           ║"
echo "║   Team Blind                                 ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Step 1: Backend ───────────────────────────────────────────────────────
echo -e "${YELLOW}[1/5] Installing Python dependencies...${NC}"
cd backend
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Python packages installed${NC}"

# ── Step 2: Environment file ──────────────────────────────────────────────
if [ ! -f .env ]; then
    echo -e "${YELLOW}[2/5] Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env created — edit if needed${NC}"
else
    echo -e "${GREEN}[2/5] .env already exists — skipping${NC}"
fi

# ── Step 3: Generate data & train model ───────────────────────────────────
echo -e "${YELLOW}[3/5] Generating synthetic dataset...${NC}"
python data/generate_data.py
echo -e "${GREEN}✅ Dataset generated${NC}"

echo -e "${YELLOW}[4/5] Training XGBoost model...${NC}"
cd model && python train.py && cd ..
echo -e "${GREEN}✅ Model trained and saved${NC}"

# ── Step 4: Frontend ──────────────────────────────────────────────────────
cd ../frontend
echo -e "${YELLOW}[5/5] Installing Node.js dependencies...${NC}"
npm install --silent
echo -e "${GREEN}✅ Node packages installed${NC}"

# ── Done ──────────────────────────────────────────────────────────────────
cd ..
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗"
echo "║   Setup Complete!                            ║"
echo "╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "  To start the system, open TWO terminals:"
echo ""
echo -e "  ${BLUE}Terminal 1 (Backend):${NC}"
echo "    cd backend && python api/app.py"
echo "    → http://localhost:5000"
echo ""
echo -e "  ${BLUE}Terminal 2 (Frontend):${NC}"
echo "    cd frontend && npm start"
echo "    → http://localhost:3000"
echo ""
echo -e "  ${YELLOW}Or run everything with Docker:${NC}"
echo "    docker-compose up --build"
echo ""
echo -e "  ${YELLOW}Run tests:${NC}"
echo "    cd backend && pytest tests/ -v"
echo ""
