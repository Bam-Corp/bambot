import streamlit as st
import os
import subprocess
from pathlib import Path
import pandas as pd

def read_logs(log_dir):
    log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
    log_data = []
    for log_file in log_files:
        log_file_path = os.path.join(log_dir, log_file)
        with open(log_file_path, "r") as file:
            for line in file:
                log_data.append(line.strip())
    return pd.DataFrame({"Log": log_data})

def main():
    st.set_page_config(page_title="Bam AI Agent Dashboard", layout="wide", page_icon=":robot_face:")

    # Add a header
    st.markdown("""
        <div style="text-align: center;">
            <h1>Bam AI Agent Dashboard</h1>
            <hr>
        </div>
    """, unsafe_allow_html=True)

    # Add a sidebar for navigation
    sidebar = st.sidebar
    sidebar.title("Navigation")
    option = sidebar.selectbox("Select an option", ["Overview", "Logs", "Metrics"])

    if option == "Overview":
        st.header("Overview")
        st.markdown("""
            <div style="text-align: center;">
                <p>Welcome to the Bam AI Agent Dashboard!</p>
                <p>This dashboard provides an overview of your AI agent's performance, logs, and metrics.</p>
            </div>
        """, unsafe_allow_html=True)

    elif option == "Logs":
        st.header("Logs")
        log_dir = os.path.join(os.getcwd(), "logs")
        if os.path.exists(log_dir):
            log_data = read_logs(log_dir)
            st.dataframe(log_data, height=600)
        else:
            st.warning("No log files found.")

    elif option == "Metrics":
        st.header("Metrics")
        st.markdown("""
            <div style="text-align: center;">
                <p>Metrics coming soon!</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()