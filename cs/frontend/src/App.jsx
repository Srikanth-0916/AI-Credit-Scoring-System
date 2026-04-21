import { useState, useEffect } from "react";

const API = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

const EMPLOYMENT_TYPES = ["salaried", "self_employed", "gig_worker", "student"];
const TENURES = [6, 12, 24, 36, 48, 60];

const defaultForm = {
  applicant_name: "",
  age: 28,
  monthly_income: 35000,
  employment_type: "salaried",
  upi_txn_per_month: 45,
  avg_txn_amount: 800,
  utility_bills_paid: 10,
  rent_payments_on_time: 10,
  mobile_recharge_regularity: 0.85,
  spending_variance: 0.3,
  income_stability_ratio: 0.8,
  savings_rate: 0.15,
  late_payments: 1,
  overdraft_count: 0,
  loan_amount_requested: 100000,
  loan_tenure_months: 24,
};

function ScoreGauge({ score }) {
  const min = 300, max = 850;
  const pct = ((score - min) / (max - min)) * 100;
  const color =
    score >= 750 ? "#22c55e" :
    score >= 650 ? "#f59e0b" :
    score >= 550 ? "#ef4444" : "#7f1d1d";

  return (
    <div className="gauge-wrapper">
      <svg viewBox="0 0 200 120" width="220" height="130">
        {/* Background arc */}
        <path d="M 20 110 A 90 90 0 0 1 180 110" fill="none" stroke="#e2e8f0" strokeWidth="18" strokeLinecap="round" />
        {/* Score arc */}
        <path
          d="M 20 110 A 90 90 0 0 1 180 110"
          fill="none"
          stroke={color}
          strokeWidth="18"
          strokeLinecap="round"
          strokeDasharray={`${(pct / 100) * 283} 283`}
          style={{ transition: "stroke-dasharray 1s ease" }}
        />
        <text x="100" y="98" textAnchor="middle" fontSize="32" fontWeight="bold" fill={color}>{score}</text>
        <text x="100" y="114" textAnchor="middle" fontSize="11" fill="#94a3b8">out of 850</text>
        <text x="22" y="128" fontSize="10" fill="#94a3b8">300</text>
        <text x="168" y="128" fontSize="10" fill="#94a3b8">850</text>
      </svg>
    </div>
  );
}

function FactorBar({ feature, impact, direction }) {
  const pct = Math.min(Math.abs(impact) * 300, 100);
  const color = direction === "positive" ? "#22c55e" : "#ef4444";
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 3 }}>
        <span style={{ color: "#334155", fontWeight: 500 }}>{feature}</span>
        <span style={{ color, fontWeight: 600 }}>{direction === "positive" ? "▲ Positive" : "▼ Negative"}</span>
      </div>
      <div style={{ background: "#e2e8f0", borderRadius: 4, height: 8, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, background: color, height: "100%", borderRadius: 4, transition: "width 0.8s ease" }} />
      </div>
    </div>
  );
}

function AuditTable({ records }) {
  if (!records.length) return <p style={{ color: "#94a3b8", textAlign: "center", padding: 20 }}>No records yet.</p>;
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ background: "#f1f5f9" }}>
            {["Request ID", "Applicant", "Score", "Risk Tier", "Timestamp"].map(h => (
              <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "#64748b", fontWeight: 600 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {records.map((r, i) => (
            <tr key={r.request_id} style={{ background: i % 2 === 0 ? "#fff" : "#f8fafc", borderBottom: "1px solid #e2e8f0" }}>
              <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#3b82f6" }}>{r.request_id}</td>
              <td style={{ padding: "8px 12px", color: "#1e293b", fontWeight: 500 }}>{r.applicant_name}</td>
              <td style={{ padding: "8px 12px", fontWeight: 700, color: r.credit_score >= 700 ? "#22c55e" : r.credit_score >= 550 ? "#f59e0b" : "#ef4444" }}>{r.credit_score}</td>
              <td style={{ padding: "8px 12px" }}>
                <span style={{
                  background: r.risk_tier === "Low Risk" ? "#dcfce7" : r.risk_tier === "Moderate Risk" ? "#fef9c3" : "#fee2e2",
                  color: r.risk_tier === "Low Risk" ? "#166534" : r.risk_tier === "Moderate Risk" ? "#854d0e" : "#991b1b",
                  padding: "2px 10px", borderRadius: 20, fontSize: 11, fontWeight: 600
                }}>{r.risk_tier}</span>
              </td>
              <td style={{ padding: "8px 12px", color: "#94a3b8", fontSize: 11 }}>{new Date(r.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState("score");
  const [form, setForm] = useState(defaultForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    fetch(`${API}/health`)
      .then(r => r.json())
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  const fetchAudit = () => {
    fetch(`${API}/audit`).then(r => r.json()).then(d => setAuditLogs(d.records || []));
    fetch(`${API}/stats`).then(r => r.json()).then(setStats);
  };

  useEffect(() => { if (tab === "audit") fetchAudit(); }, [tab]);

  const handleChange = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    if (!form.applicant_name.trim()) { setError("Please enter applicant name."); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await fetch(`${API}/score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Scoring failed");
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: "100%", padding: "8px 10px", border: "1px solid #e2e8f0",
    borderRadius: 6, fontSize: 13, color: "#1e293b",
    background: "#f8fafc", boxSizing: "border-box"
  };
  const labelStyle = { fontSize: 12, color: "#64748b", fontWeight: 600, display: "block", marginBottom: 4 };
  const fieldWrap = { marginBottom: 14 };

  return (
    <div style={{ fontFamily: "'Inter', 'Segoe UI', sans-serif", minHeight: "100vh", background: "#f1f5f9" }}>
      {/* Header */}
      <div style={{ background: "#0d1b4e", color: "#fff", padding: "14px 30px", display: "flex", alignItems: "center", justifyContent: "space-between", boxShadow: "0 2px 12px rgba(0,0,0,0.2)" }}>
        <div>
          <div style={{ fontWeight: 800, fontSize: 20, letterSpacing: 0.5 }}>
            <span style={{ color: "#00b4d8" }}>AI</span> Credit Scoring System
          </div>
          <div style={{ fontSize: 11, color: "#7a96b0", marginTop: 1 }}>Inclusive Credit for All — Team Blind</div>
        </div>
        <div style={{
          background: apiStatus === "online" ? "#166534" : "#991b1b",
          color: "#fff", padding: "4px 14px", borderRadius: 20, fontSize: 11, fontWeight: 600
        }}>
          ● API {apiStatus.toUpperCase()}
        </div>
      </div>

      {/* Tabs */}
      <div style={{ background: "#fff", borderBottom: "1px solid #e2e8f0", display: "flex", padding: "0 30px" }}>
        {[["score", "Score Applicant"], ["audit", "Audit Log & Stats"]].map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)} style={{
            padding: "12px 22px", border: "none", background: "none", cursor: "pointer",
            fontWeight: 600, fontSize: 14, color: tab === key ? "#0d1b4e" : "#94a3b8",
            borderBottom: tab === key ? "3px solid #00b4d8" : "3px solid transparent",
            marginBottom: -1
          }}>{label}</button>
        ))}
      </div>

      <div style={{ maxWidth: 1100, margin: "30px auto", padding: "0 20px" }}>

        {/* ── SCORE TAB ── */}
        {tab === "score" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>

            {/* Form Panel */}
            <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
              <h2 style={{ margin: "0 0 18px", color: "#0d1b4e", fontSize: 17 }}>Applicant Details</h2>

              <div style={fieldWrap}>
                <label style={labelStyle}>Applicant Name *</label>
                <input style={inputStyle} value={form.applicant_name} onChange={e => handleChange("applicant_name", e.target.value)} placeholder="e.g. Priya Sharma" />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {[["age", "Age", "number"], ["monthly_income", "Monthly Income (₹)", "number"]].map(([k, l, t]) => (
                  <div key={k} style={fieldWrap}>
                    <label style={labelStyle}>{l}</label>
                    <input style={inputStyle} type={t} value={form[k]} onChange={e => handleChange(k, +e.target.value)} />
                  </div>
                ))}
              </div>

              <div style={fieldWrap}>
                <label style={labelStyle}>Employment Type</label>
                <select style={inputStyle} value={form.employment_type} onChange={e => handleChange("employment_type", e.target.value)}>
                  {EMPLOYMENT_TYPES.map(t => <option key={t} value={t}>{t.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase())}</option>)}
                </select>
              </div>

              <div style={{ borderTop: "1px solid #e2e8f0", margin: "16px 0 14px", paddingTop: 14 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#00b4d8", marginBottom: 12, letterSpacing: 1 }}>ALTERNATE FINANCIAL SIGNALS</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  {[
                    ["upi_txn_per_month", "UPI Txns/Month"], ["avg_txn_amount", "Avg Txn Amount (₹)"],
                    ["utility_bills_paid", "Utility Bills Paid (/ 12)"], ["rent_payments_on_time", "Rent Paid On Time (/ 12)"],
                    ["late_payments", "Late Payments"], ["overdraft_count", "Overdraft Count"],
                    ["loan_amount_requested", "Loan Amount (₹)"],
                  ].map(([k, l]) => (
                    <div key={k} style={fieldWrap}>
                      <label style={labelStyle}>{l}</label>
                      <input style={inputStyle} type="number" value={form[k]} onChange={e => handleChange(k, +e.target.value)} />
                    </div>
                  ))}
                  <div style={fieldWrap}>
                    <label style={labelStyle}>Loan Tenure</label>
                    <select style={inputStyle} value={form.loan_tenure_months} onChange={e => handleChange("loan_tenure_months", +e.target.value)}>
                      {TENURES.map(t => <option key={t} value={t}>{t} months</option>)}
                    </select>
                  </div>
                </div>
              </div>

              <div style={{ borderTop: "1px solid #e2e8f0", margin: "4px 0 14px", paddingTop: 14 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#00b4d8", marginBottom: 12, letterSpacing: 1 }}>BEHAVIORAL INDICATORS (0–1)</div>
                {[
                  ["mobile_recharge_regularity", "Mobile Recharge Regularity"],
                  ["spending_variance", "Spending Variance (0=stable)"],
                  ["income_stability_ratio", "Income Stability Ratio"],
                  ["savings_rate", "Savings Rate"],
                ].map(([k, l]) => (
                  <div key={k} style={{ marginBottom: 14 }}>
                    <label style={{ ...labelStyle, display: "flex", justifyContent: "space-between" }}>
                      <span>{l}</span><span style={{ color: "#0d1b4e" }}>{form[k]}</span>
                    </label>
                    <input type="range" min={0} max={1} step={0.05} value={form[k]}
                      onChange={e => handleChange(k, +e.target.value)}
                      style={{ width: "100%", accentColor: "#00b4d8" }} />
                  </div>
                ))}
              </div>

              {error && <div style={{ background: "#fee2e2", color: "#991b1b", borderRadius: 8, padding: "10px 14px", fontSize: 13, marginBottom: 14 }}>⚠ {error}</div>}

              <button onClick={handleSubmit} disabled={loading} style={{
                width: "100%", background: loading ? "#94a3b8" : "#0d1b4e",
                color: "#fff", border: "none", borderRadius: 8,
                padding: "12px 0", fontSize: 15, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
                transition: "background 0.2s"
              }}>
                {loading ? "⏳ Scoring..." : "▶  Generate Credit Score"}
              </button>
            </div>

            {/* Result Panel */}
            <div>
              {!result ? (
                <div style={{ background: "#fff", borderRadius: 12, padding: 40, textAlign: "center", boxShadow: "0 2px 12px rgba(0,0,0,0.06)", color: "#94a3b8" }}>
                  <div style={{ fontSize: 48, marginBottom: 14 }}>📊</div>
                  <div style={{ fontSize: 16, fontWeight: 600 }}>Fill in applicant details and click Generate Credit Score</div>
                  <div style={{ fontSize: 13, marginTop: 8 }}>Score will appear here with SHAP explanation</div>
                </div>
              ) : (
                <div>
                  {/* Score Card */}
                  <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.06)", marginBottom: 18, textAlign: "center" }}>
                    <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 2 }}>Request #{result.request_id}</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: "#0d1b4e", marginBottom: 12 }}>{result.applicant_name}</div>
                    <ScoreGauge score={result.credit_score} />
                    <div style={{
                      display: "inline-block", background: result.risk_color + "22",
                      color: result.risk_color, padding: "5px 18px", borderRadius: 20,
                      fontWeight: 700, fontSize: 14, marginTop: 8, border: `1px solid ${result.risk_color}44`
                    }}>{result.risk_tier}</div>
                    <div style={{ marginTop: 14 }}>
                      <div style={{
                        background: result.eligible === true ? "#dcfce7" : result.eligible === false ? "#fee2e2" : "#fef9c3",
                        color: result.eligible === true ? "#166534" : result.eligible === false ? "#991b1b" : "#854d0e",
                        borderRadius: 8, padding: "10px 16px", fontSize: 14, fontWeight: 600
                      }}>
                        {result.eligible === true ? "✅" : result.eligible === false ? "❌" : "⚠️"} {result.eligibility_message}
                      </div>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 14 }}>
                      {[
                        ["Repayment Probability", (result.repayment_probability * 100).toFixed(1) + "%"],
                        ["Loan Requested", "₹" + result.loan_details.amount_requested?.toLocaleString()],
                        ["Tenure", result.loan_details.tenure_months + " months"],
                        ["Scored At", new Date(result.timestamp).toLocaleTimeString()],
                      ].map(([k, v]) => (
                        <div key={k} style={{ background: "#f8fafc", borderRadius: 8, padding: "10px 12px", textAlign: "left" }}>
                          <div style={{ fontSize: 11, color: "#94a3b8" }}>{k}</div>
                          <div style={{ fontSize: 14, fontWeight: 700, color: "#0d1b4e" }}>{v}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* SHAP Explanation */}
                  <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
                    <h3 style={{ margin: "0 0 16px", color: "#0d1b4e", fontSize: 15 }}>🔍 Score Explanation (SHAP)</h3>
                    <p style={{ fontSize: 12, color: "#94a3b8", margin: "0 0 14px" }}>Top factors influencing this credit score</p>
                    {result.top_factors.map((f, i) => <FactorBar key={i} {...f} />)}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── AUDIT TAB ── */}
        {tab === "audit" && (
          <div>
            {stats && stats.total_applications > 0 && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
                {[
                  ["Total Applications", stats.total_applications, "#3b82f6"],
                  ["Average Score", stats.average_score, "#22c55e"],
                  ["Highest Score", stats.highest_score, "#10b981"],
                  ["Lowest Score", stats.lowest_score, "#ef4444"],
                ].map(([label, val, color]) => (
                  <div key={label} style={{ background: "#fff", borderRadius: 12, padding: "18px 20px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
                    <div style={{ fontSize: 12, color: "#94a3b8", fontWeight: 600 }}>{label}</div>
                    <div style={{ fontSize: 28, fontWeight: 800, color, marginTop: 4 }}>{val}</div>
                  </div>
                ))}
              </div>
            )}
            <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
                <h2 style={{ margin: 0, color: "#0d1b4e", fontSize: 17 }}>Audit Log</h2>
                <button onClick={fetchAudit} style={{ background: "#0d1b4e", color: "#fff", border: "none", borderRadius: 6, padding: "7px 16px", fontSize: 13, cursor: "pointer", fontWeight: 600 }}>↻ Refresh</button>
              </div>
              <AuditTable records={auditLogs} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
