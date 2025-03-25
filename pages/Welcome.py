import streamlit as st
import pandas as pd
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go

st.header("Controller Enhanced", divider="rainbow")
st.subheader("Welcome to Controller Enhanced – Your Gateway to Smarter Satellite Control")

st.markdown('''Navigating the complexities of satellite operations requires precision, reliability, and the right set of tools. CE is your all-in-one platform designed to streamline and enhance the daily workflows of satellite controllers.

From real-time telemetry analysis and anomaly detection to automation frameworks and visualization dashboards, our curated suite of software tools empowers you to operate with greater efficiency, situational awareness, and confidence. 

Explore. Integrate. Elevate your satellite operations.            
''')

st.markdown("**Tools:**")
st.page_link("pages/Download_xmlfiles.py", label="Download FDS xml files", icon="⬇")
st.page_link("pages/page_1.py", label="Export CSV to Uberlog", icon="✍️")
st.page_link("pages/page_2.py", label="Display antennae pointing", icon="📈")
st.page_link("https://masif.eumetsat.int/mediawiki/epssg/index.php/Main_Page", label="EPS-SG Knowledge base", icon="🕵️‍♂️")

