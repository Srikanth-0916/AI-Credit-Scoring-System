from sqlalchemy import (
    create_engine, Column, Integer, Float,
    String, Boolean, DateTime, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import config

engine  = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base    = declarative_base()


# ── Models ─────────────────────────────────────────────────────────────────

class ScoringRequest(Base):
    """Every call to /api/score is logged here."""
    __tablename__ = "scoring_requests"

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    request_id            = Column(String(16), unique=True, nullable=False)
    applicant_name        = Column(String(100), nullable=False)
    credit_score          = Column(Integer, nullable=False)
    repayment_probability = Column(Float, nullable=False)
    risk_tier             = Column(String(30), nullable=False)
    eligible              = Column(Boolean, nullable=True)   # None = manual review
    eligibility_message   = Column(String(100))

    # Inputs (stored for audit purposes)
    age                       = Column(Integer)
    monthly_income            = Column(Float)
    employment_type           = Column(String(30))
    upi_txn_per_month         = Column(Integer)
    avg_txn_amount            = Column(Float)
    utility_bills_paid        = Column(Integer)
    rent_payments_on_time     = Column(Integer)
    mobile_recharge_regularity= Column(Float)
    spending_variance         = Column(Float)
    income_stability_ratio    = Column(Float)
    savings_rate              = Column(Float)
    late_payments             = Column(Integer)
    overdraft_count           = Column(Integer)
    loan_amount_requested     = Column(Float)
    loan_tenure_months        = Column(Integer)

    # SHAP top factors (JSON string)
    top_factors = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":                     self.id,
            "request_id":             self.request_id,
            "applicant_name":         self.applicant_name,
            "credit_score":           self.credit_score,
            "repayment_probability":  self.repayment_probability,
            "risk_tier":              self.risk_tier,
            "eligible":               self.eligible,
            "eligibility_message":    self.eligibility_message,
            "employment_type":        self.employment_type,
            "monthly_income":         self.monthly_income,
            "loan_amount_requested":  self.loan_amount_requested,
            "loan_tenure_months":     self.loan_tenure_months,
            "timestamp":              self.created_at.isoformat() if self.created_at else None,
        }


class Applicant(Base):
    """Optional: store applicant profiles separately."""
    __tablename__ = "applicants"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    national_id    = Column(String(30), unique=True)
    full_name      = Column(String(100))
    email          = Column(String(100))
    phone          = Column(String(20))
    consent_given  = Column(Boolean, default=False)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id":           self.id,
            "national_id":  self.national_id,
            "full_name":    self.full_name,
            "email":        self.email,
            "phone":        self.phone,
            "consent_given":self.consent_given,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
        }


def init_db():
    """Create all tables."""
    Base.metadata.create_all(engine)
    print("✅ Database initialized")


def get_session():
    return Session()


if __name__ == "__main__":
    init_db()
