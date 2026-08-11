import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="LogSentinel Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
    )

# ---------------------------------------------------------
# Auxiliary functions
# ---------------------------------------------------------

def load_json_file(file_path):
    if not os.path.exists(file_path):
        return []

    data = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line.strip()))
            except:
                pass
    return data

# ---------------------------------------------------------
# Loading data
# ---------------------------------------------------------

events = load_json_file("data/events.jsonl")
alerts = load_json_file("data/alerts.jsonl")

events_df = pd.DataFrame(events)
alerts_df = pd.DataFrame(alerts)

st.title("LogSentinel Dashboard")
st.markdown("Realtime log monitoring and alerting system.")

# ---------------------------------------------------------
# General Statistics
# ---------------------------------------------------------

st.header("General Statistics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Events", len(events_df))
col2.metric("Total Alerts", len(alerts_df))
col3.metric("Unique IP Addresses", events_df['ip'].nunique() if 'ip' in events_df else 0)

# ---------------------------------------------------------
# Graphs: Events by type
# ---------------------------------------------------------

st.header("Events by Type")

if 'event_type' in events_df:
    event_counts = events_df['event_type'].value_counts()
    st.bar_chart(event_counts)
else:
    st.info("No event type data available.")

# ---------------------------------------------------------
# Graphs: Events by IP Address
# ---------------------------------------------------------

st.header("Events by IP Address")

if 'ip' in events_df:
    ip_counts = events_df['ip'].value_counts().head(10)
    st.bar_chart(ip_counts)
else:
    st.info("No IP address data available.")

# ---------------------------------------------------------
# Events Table
# ---------------------------------------------------------

st.header("Recent Events")

if not events_df.empty:
    st.dataframe(events_df.tail(50))
else:
    st.info("No events recorded.")

# ---------------------------------------------------------
# Alerts Table
# ---------------------------------------------------------

st.header("Alerts")

if not alerts_df.empty:
    st.dataframe(alerts_df.tail(50))
else:
    st.info("No alerts recorded.") 

