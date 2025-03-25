# -*- coding: utf-8 -*-

"""

Created on Thu Mar 12 19:21:14 2025
 
XML Downloader
 
@author: Sapuppo Andre

"""
 
import streamlit as st
from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

import requests

import os

import time
from selenium.webdriver.chrome.options import Options
st.header("Controller Enhanced P2", divider="rainbow")
st.subheader("Download FDS xml updated files")

st.markdown(''' This tool is for Download FDS updated xml files

- 1. Wait until download buttons appear.             
- 2. Click on Download buttons to dowload all the xml files.       
''')

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--disable-gpu")  # Fixes issues on some systems
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")  # Helps with resource limits
 

 
# Setup Chrome WebDriver

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service,options=chrome_options)
 
# Target URL

url = "http://10.5.129.79/mfz/events.html"

driver.get(url)
 
# Wait for the page to load (adjust as needed)

time.sleep(5)
 
# Extract all links from the page

links = driver.find_elements(By.TAG_NAME, "a")
 
# Directory to save XML files

SAVE_DIR = "downloaded_xml"

#SAVE_DIR = "C:\Users\Sapuppo\OneDrive - eumetsat.int\Desktop\AutoUberlog\\downloaded_xml"

os.makedirs(SAVE_DIR, exist_ok=True)
 
# Identify and download XML files
files = []
filenames = []
for link in links:

    href = link.get_attribute("href")

    if href and href.endswith(".xml"):

        print(f"Found XML file: {href}")

        # Download the XML file using requests

        response = requests.get(href)

        if response.status_code == 200:
            files.append(response.content)
            filenames.append(href)

            #filename = os.path.join(SAVE_DIR, os.path.basename(href))

            #with open(filename, "wb") as file:

             #   file.write(response.content)

            #print(f"Downloaded: {filename}")

        else:

            st.warning(f"Failed to download {href}")
 
# Close browser
i = 0
for file in files:
    SAT = filenames[i].split("_")[0].split("/")[5]

    st.download_button(
                label=f"Download {SAT}",
                data=file,
                file_name=filenames[i],
                mime="text/xml",
                icon=":material/download:",
                ) 
    i += 1
driver.quit()


 