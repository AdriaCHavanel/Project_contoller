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
from bs4 import BeautifulSoup
import os

import time
from selenium.webdriver.chrome.options import Options

import json


st.header("Controller Enhanced P2", divider="rainbow")
st.subheader("Download FDS xml updated files")

st.markdown(''' This tool is for Download FDS updated xml files

- 1. Wait until download buttons appear.             
- 2. Click on Download buttons to dowload all the xml files.       
''')
#url = "http://10.5.129.79/mfz/events.html"
url = "http://10.5.129.79/mfz/geoevt.json" #where the txt filename is!
#Aurl = "http://10.5.129.79/mfz/geoevt/SGA1_FDP_FDS__OPE_GEOEV______G20250411063815Z_S20250411000000Z_E20250526000000Z.xml"
baseurl = "http://10.5.129.79/mfz/"
# Make the request to the page
try:
    response = requests.get(url, timeout=120)
    
    if response.status_code == 200:
        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")
        links = [requests.compat.urljoin(url, a['href']) for a in soup.find_all("a") if a['href'].endswith(".xml")]
        print(f"\n \n {soup} \n \n")
        y = json.loads(str(soup))
        print(y[0]["url"])
        # Directory simulation: collect XML files
        files = []
        filenames = []

        for file in y:
            if file["url"].endswith(".xml"):
                st.info(f"Found XML: {file["url"]}")
                full_url = requests.compat.urljoin(baseurl, file["url"])
                # Download the XML file
                file_response = requests.get(full_url)
                if file_response.status_code == 200:
                    files.append(file_response.content)
                    filenames.append(full_url)
                else:
                    st.warning(f"Failed to download {file["url"]}")

        # Display download buttons
        for i, file in enumerate(files):
            try:
                SAT = filenames[i].split("_")[0].split("/")[-1]
            except IndexError:
                SAT = f"file_{i+1}.xml"

            print("\\n \\n PAOLONEEEE \\n \\n")
            st.download_button(
                label=f"📥 Download {SAT}",
                data=file,
                file_name=SAT + ".xml",
                mime="application/xml"
            )

    else:
        st.error(f"Failed to access page. Status code: {response.status_code}")

except Exception as e:
    st.error(f"An error occurred: {e}")

#
#chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in background
#chrome_options.add_argument("--disable-gpu")  # Fixes issues on some systems
#chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--disable-dev-shm-usage")  # Helps with resource limits
# 
##chrome_options.binary_location = "/usr/bin/chromium"
#
## Setup Chrome WebDriver
#service = Service(ChromeDriverManager().install())
#
## Point to where the chromedriver is installed
##service = Service("/usr/bin/chromedriver")
#driver = webdriver.Chrome(service=service, options=chrome_options)
# 
## Setup Chrome WebDriver
# 
## Target URL
#
#url = "http://10.5.129.79/mfz/events.html"
#
#driver.get(url)
# 
## Wait for the page to load (adjust as needed)
#
#time.sleep(5)
# 
## Extract all links from the page
#
#links = driver.find_elements(By.TAG_NAME, "a")
# 
## Directory to save XML files
#
#SAVE_DIR = "downloaded_xml"
#
##SAVE_DIR = "C:\Users\Sapuppo\OneDrive - eumetsat.int\Desktop\AutoUberlog\\downloaded_xml"
#
#os.makedirs(SAVE_DIR, exist_ok=True)
# 
## Identify and download XML files
#files = []
#filenames = []
#for link in links:
#
#    href = link.get_attribute("href")
#
#    if href and href.endswith(".xml"):
#
#        print(f"Found XML file: {href}")
#
#        # Download the XML file using requests
#
#        response = requests.get(href)
#
#        if response.status_code == 200:
#            files.append(response.content)
#            filenames.append(href)
#
#            #filename = os.path.join(SAVE_DIR, os.path.basename(href))
#
#            #with open(filename, "wb") as file:
#
#             #   file.write(response.content)
#
#            #print(f"Downloaded: {filename}")
#
#        else:
#
#            st.warning(f"Failed to download {href}")
# 
## Close browser
#i = 0
#for file in files:
#    SAT = filenames[i].split("_")[0].split("/")[5]
#
#    st.download_button(
#                label=f"Download {SAT}",
#                data=file,
#                file_name=filenames[i],
#                mime="text/xml",
#                #icon=":material/download:",
#                ) 
#    i += 1
#driver.quit()
#
 
