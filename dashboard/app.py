from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="LLM Guardian", page_icon="🛡️", layout="wide")
st.title("LLM Guardian")
st.caption("Evidence-first evaluation, adversarial testing, and statistical release gates")

default_path = Path("artifacts/demo/comparison.json")
uploaded = st.file_uploader("Load a comparison artifact", type="json")
if uploaded:
    payload = json.load(uploaded)
elif default_path.exists():
    payload = json.loads(default_path.read_text(encoding="utf-8"))
else:
    st.info("Run `python scripts/run_demo.py` to generate the demonstration artifact.")
    st.stop()

baseline = payload["baseline"]
candidate = payload["candidate"]
gate = payload["release_gate"]

decision, pass_rate, confidence, critical = st.columns(4)
decision.metric("Release gate", "PASS" if gate["passed"] else "FAIL")
pass_rate.metric("Candidate pass rate", f"{candidate['pass_rate']:.1%}")
confidence.metric("95% Wilson lower bound", f"{candidate['wilson_lower_bound']:.1%}")
critical.metric("Critical failures", candidate["critical_failures"])

category_rows = []
for version, data in (("Baseline", baseline), ("Candidate", candidate)):
    for category, rate in data["category_pass_rates"].items():
        category_rows.append({"version": version, "category": category, "pass_rate": rate})
frame = pd.DataFrame(category_rows)
figure = px.bar(
    frame,
    x="category",
    y="pass_rate",
    color="version",
    barmode="group",
    range_y=[0, 1],
    labels={"pass_rate": "Pass rate", "category": "Evaluation category"},
)
st.plotly_chart(figure, use_container_width=True)

st.subheader("Release checks")
checks = pd.DataFrame(gate["checks"])
checks["status"] = checks["passed"].map({True: "PASS", False: "FAIL"})
st.dataframe(checks[["status", "name", "actual", "operator", "threshold"]], hide_index=True)

with st.expander("Evidence boundary"):
    st.write(payload["interpretation"])

