import streamlit as st
import pandas as pd
from agent import run_agent

st.set_page_config(page_title="Ask the Analyst")

st.title("🧠 Ask the Analyst")
st.caption("Upload a CSV file and ask questions about the data.")

csv_file = st.file_uploader("Upload CSV", type=["csv"])
question = st.text_input("What do you want to know?")

if csv_file and question:
    df = pd.read_csv(csv_file)
    with st.spinner("Analyzing..."):
        result = run_agent(df, question)
        st.write(" Answer:")
        st.write(result)
