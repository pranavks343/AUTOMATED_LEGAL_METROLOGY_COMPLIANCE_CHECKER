import streamlit as st
import json, pandas as pd
from pathlib import Path
from core.auth import require_auth

# Require authentication
require_auth()

st.title("📊 Dashboard")

report_path = Path("app/data/reports/validated.jsonl")
if not report_path.exists():
    st.warning("No validations yet. Run some validations first.")
    st.stop()

rows = []
for line in report_path.read_text().splitlines():
    try:
        rows.append(json.loads(line))
    except Exception:
        pass

if not rows:
    st.warning("Report file is empty.")
    st.stop()

df = pd.json_normalize(rows)
df['date'] = pd.to_datetime('today').normalize()
st.dataframe(df[['file','is_compliant','score']])

st.subheader("Aggregates")
comp_rate = df['is_compliant'].mean()*100
st.metric("Compliance Rate", f"{comp_rate:.1f}%")
st.bar_chart(df['score'])
