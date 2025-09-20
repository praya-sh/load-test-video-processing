import streamlit as st
import pandas as pd
import numpy as np
import random
import altair as alt
import plotly.graph_objects as go

def generate_metrics(num_streams=120):
    data = []
    for stream_id in range(num_streams):
        latency = random.randint(50, 500)  # ms
        success = random.choice([1]*9 + [0])  # 90% success
        bitrate = random.randint(800, 1500)   # kbps
        jitter = random.uniform(5, 50)        # ms
        data.append([stream_id, latency, success, bitrate, jitter])
    df = pd.DataFrame(data, columns=["Stream ID", "Latency (ms)", "Success", "Bitrate (kbps)", "Jitter (ms)"])
    return df

if "df" not in st.session_state:
    st.session_state.df = generate_metrics()

st.set_page_config(page_title="Video Metrics Dashboard", layout="wide")
st.title("Video Data Quality Dashboard (Enhanced & Editable)")

# Editable Data Table
st.subheader(" Edit Metrics Data")
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True
)
st.session_state.df = edited_df

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Latency (ms)", f"{edited_df['Latency (ms)'].mean():.1f}")
with col2:
    st.metric("Error Rate (%)", f"{100 - edited_df['Success'].mean()*100:.1f}%")
with col3:
    st.metric("Avg Bitrate (kbps)", f"{edited_df['Bitrate (kbps)'].mean():.1f}")
with col4:
    st.metric("Avg Jitter (ms)", f"{edited_df['Jitter (ms)'].mean():.1f}")

st.markdown("---")

col1, col2 = st.columns(2)

# Latency Distribution Histogram
with col1:
    st.subheader("Latency Distribution (Histogram)")
    st.bar_chart(edited_df["Latency (ms)"])

# Success vs Failure Bar Chart
with col2:
    st.subheader("Stream Success vs Failures (Bar)")
    success_counts = edited_df["Success"].value_counts().rename({1: "Success", 0: "Failure"})
    st.bar_chart(success_counts)

# Bitrate Trends
st.subheader("Bitrate Trends per Stream")
st.line_chart(edited_df.set_index("Stream ID")["Bitrate (kbps)"])

# Boxplot for Latency
st.subheader("Latency Distribution (Boxplot)")
latency_box = alt.Chart(edited_df).mark_boxplot().encode(
    y="Latency (ms):Q"
)
st.altair_chart(latency_box, use_container_width=True)

# Scatter Plot: Bitrate vs Latency
st.subheader("Bitrate vs Latency (Colored by Success)")
scatter = alt.Chart(edited_df).mark_circle(size=70).encode(
    x="Bitrate (kbps):Q",
    y="Latency (ms):Q",
    color=alt.Color("Success:N", scale=alt.Scale(domain=[0,1], range=["red","green"])),
    tooltip=["Stream ID", "Bitrate (kbps)", "Latency (ms)", "Success"]
)
st.altair_chart(scatter, use_container_width=True)

# Jitter per Stream
st.subheader("Jitter per Stream")
st.line_chart(edited_df.set_index("Stream ID")["Jitter (ms)"])

# Pie Chart: Success vs Failure
st.subheader("Success vs Failure (Pie)")
fig = go.Figure(data=[go.Pie(
    labels=["Success", "Failure"],
    values=[success_counts.get("Success", 0), success_counts.get("Failure", 0)],
    hole=0.4
)])
st.plotly_chart(fig, use_container_width=True)

# Heatmap of Metrics per Stream
st.subheader("Heatmap of Metrics per Stream")
heatmap = alt.Chart(edited_df).mark_rect().encode(
    x="Stream ID:O",
    y="metric:N",
    color="value:Q"
).transform_fold(
    ["Latency (ms)", "Bitrate (kbps)", "Jitter (ms)"],
    as_=["metric", "value"]
)
st.altair_chart(heatmap, use_container_width=True)

# Correlation Matrix
st.subheader("Correlation Matrix")
corr = edited_df[["Latency (ms)", "Bitrate (kbps)", "Jitter (ms)", "Success"]].corr()
st.dataframe(corr.style.background_gradient(cmap="RdYlGn", axis=None))