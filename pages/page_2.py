import streamlit as st
import pandas as pd
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go


def GetAllAngles(FileName,Filename2):
  azimuthss = pd.read_csv(FileName)
  elevationss = pd.read_csv(Filename2)
  df1_unique = azimuthss.drop_duplicates(subset="Date", keep="first")
  df2_unique = elevationss.drop_duplicates(subset="Date", keep="first")
  common_dates = set(df1_unique["Date"]).intersection(set(df2_unique["Date"]))

  # Filtrar los DataFrames para quedarse solo con las fechas comunes
  filtered_df1 = df1_unique[df1_unique["Date"].isin(common_dates)]
  filtered_df2 = df2_unique[df2_unique["Date"].isin(common_dates)]

  # Convertir los valores a numpy arrays
  azim = filtered_df1["Value"].to_numpy()
  ele = filtered_df2["Value"].to_numpy()

  for i in range(len(azim)):
      azim[i] = np.deg2rad(float(azim[i].split(' ')[0]))
      ele[i] = np.deg2rad(float(ele[i].split(' ')[0]))  # Split by space and take the first part
  return([np.asarray(azim),np.asarray(ele)])

def plot_3d_vectors(radius, azimuths, elevations):

  azimuths = np.asarray(azimuths, dtype=np.float64)
  elevations = np.asarray(elevations, dtype=np.float64)

  # Convert spherical coordinates to Cartesian coordinates
  x = radius * np.cos(elevations) * np.cos(azimuths)
  y = radius * np.cos(elevations) * np.sin(azimuths)
  z = radius * np.sin(elevations)

  # Create the 3D plot

  # Plot the vectors
  fig = go.Figure()

    # Add vectors as lines starting from (0,0,0)
  for i in range(len(x)):
      fig.add_trace(go.Scatter3d(
          x=[0, x[i]],  # Vector from (0,0,0) to (x,y,z)
          y=[0, y[i]],
          z=[0, z[i]],
          mode='lines+markers',
          marker=dict(size=4, color='red'),  # Marker at the vector head
          line=dict(width=3, color='blue')   # Line representing the vector
      ))

  # Customize layout
  fig.update_layout(
      title="Interactive 3D Vectors from Origin",
      scene=dict(
          xaxis=dict(title="X Axis", range=[-radius, radius]),
          yaxis=dict(title="Y Axis", range=[-radius, radius]),
          zaxis=dict(title="Z Axis", range=[0, radius])
      )
  )

  # Display the plot
  return(fig)

st.header("Controller Enhanced P2", divider="rainbow")
st.subheader("SDA and DBA pointing")

st.markdown(''' This tool is for Display the azimut and elevation from a DBA file extracted from GSTMC.
            
- 1. click on retrieve logs from azimut and elevations in GSTMC
- 2. Select the period of the pass. (use also the seconds, to only see the full pass)
- 3. click on Generate Reports from retrieve logs.
- 4. Remove the header of the reports and save them as csv files.
- 5. Upload them into this tool.
- 6. Check the pointing of the antena in a circle of 1 u for the full pass.            
''')

uploaded_files = st.file_uploader("Upload azimuts and elevations", accept_multiple_files=True)

if uploaded_files is not None and len(uploaded_files) == 2:
    azel = uploaded_files
    
    # Assuming GetAllAngles(file1, file2) reads azimuths and elevations
    vecs = GetAllAngles(azel[0], azel[1])
    
    azimuths = vecs[0]
    elevations = vecs[1]
    
    st.write("Azimuths:", len(azimuths), "Elevations:", len(elevations))
    
    radius = 1
    st.plotly_chart(plot_3d_vectors(radius, azimuths, elevations))
else:
    st.warning("Please upload exactly two files.")