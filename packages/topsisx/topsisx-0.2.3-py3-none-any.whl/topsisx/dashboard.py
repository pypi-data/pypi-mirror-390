import streamlit as st
import pandas as pd
from topsisx.pipeline import DecisionPipeline
from topsisx.reports import generate_report

st.title("Decision Making Dashboard (TOPSISX)")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Input Data", df)

    weights_method = st.selectbox("Choose weighting method:", ["entropy", "ahp", "equal"])
    ranking_method = st.selectbox("Choose decision method:", ["topsis", "vikor", "ahp"])
    impacts = st.text_input("Enter impacts (+,-,+,...)", "+,-")

    if st.button("Run Decision Analysis"):
        pipe = DecisionPipeline(weights=weights_method, method=ranking_method)
        result = pipe.run(df.iloc[:, 1:], impacts=impacts.split(","))
        st.write("### Results", result)

        if st.button("Generate PDF Report"):
            generate_report(result, method=ranking_method)
            st.success("PDF report generated (decision_report.pdf)")
