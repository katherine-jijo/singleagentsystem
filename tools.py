import os
import streamlit as st

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# TOOL FUNCTIONS
def summarize_data(df):
    return df.describe().to_dict()

def get_column_names(df):
    return list(df.columns)

def average_by_column(df, question):
    for col in df.columns:
        if col.lower() in question.lower():
            return df.groupby(col).mean(numeric_only=True).to_dict()
    return {"error": "Couldn't determine the column to group by."}


# TOOL REGISTRY
TOOLS = {
    "summarize_data": summarize_data,
    "get_column_names": get_column_names,
    "average_by_column": average_by_column,
}
