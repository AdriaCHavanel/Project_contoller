import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go


#!streamlit run ../main.py

# Load CSV data
csv_filename = uploaded_files = st.file_uploader(
    "Upload the csv file", accept_multiple_files=False
) # Ensure this is in the same directory
df = pd.read_csv(csv_filename, parse_dates=["Time"])

st.title("🌍 Real-Time Satellite Groundtrack Viewer")
st.write("Tracking a simulated LEO sun-synchronous orbit.")
bg_image_path = "../background.jpg"
# Create a Plotly figure
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Azimuth'], y=df['Elevation'], mode='lines', name='Groundtrack'))
fig.update_layout(title="Satellite Groundtrack", xaxis_title="Azimuth (°)", yaxis_title="Elevation (°)", images=[dict(
        source=bg_image_path,  # Use the image path
        x=0, y=1,  # Position: Bottom-left
        xref="paper", yref="paper",
        sizex=1, sizey=1,  # Full size
        xanchor="left", yanchor="top",
        layer="below"  # Ensures the image is behind the data
    )])

# Set axis limits
fig.update_xaxes(range=[0, 360], title="Azimuth (°)")
fig.update_yaxes(range=[-90, 90], title="Elevation (°)")
# Display the plot
chart = st.plotly_chart(fig, use_container_width=False)

# Auto-refresh mechanism to simulate real-time update
placeholder = st.empty()

i = 0
while True:
    i = (i + 1) % len(df)  # Loop through data
    fig.data[0].x = df['Azimuth'][:i]
    fig.data[0].y = df['Elevation'][:i]
    placeholder.plotly_chart(fig, use_container_width=False)
    time.sleep(0.1)  # Update every second
