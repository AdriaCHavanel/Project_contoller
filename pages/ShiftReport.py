"""

Created on Tue Apr 15 10:00:14 2025
 
Daily Ops Batch Gen 
@author: Sapuppo Andre

"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timezone

st.header("Shift Reports Downloader", divider="rainbow")
st.subheader("Create Word Shift Reports")
st.markdown(''' This tool is used to generate the CSV files useful for the Shift Reports

**How to use this tool:**    
- 1. Upload the csv files containing the Uberlog info for the day.
- 2. Select a valid Period of time for the shift.
- 3. Download the CSV file.
- 4. Copy-paste it in the Word template. 
            
''')

# Step 1: Load CSV into DataFrame


uploaded_file = st.file_uploader(
    "Upload the csv Uberlog export", accept_multiple_files=False
)
if uploaded_file is None:
    st.error("Upload a valid file!")
    


#--------------- START SELECTION BOX FOR SHIFT ----------------------------

#Adding a selection box instead of writing the date everytime
#This will need an update when we will have the real shifts    
label = "When is your shift?"
list_ = ("Morning", "Afternoon", "Other")

option = st.selectbox(
    label,
    list_,
    index=None,
    placeholder="Select shift...",
)

# Get the current date in "YYYY-MM-DD" format
current_date = datetime.utcnow().strftime("%Y-%m-%d")

# Define the fixed time (To fix when the date changes again!)
morning_start = "06:00:00Z"
afternoon_start = "10:30:00Z"
afternoon_end = "16:30:00Z"


# Combine both parts
if option == "Morning":
    date_start_str = f"{current_date}T{morning_start}"
    date_end_str = f"{current_date}T{afternoon_start}"
    start_time = pd.to_datetime(date_start_str)
    # Localize to UTC
    start_time = start_time.tz_convert('UTC')
    end_time = pd.to_datetime(date_end_str)
    # Localize to UTC
    end_time = end_time.tz_convert('UTC')
elif option == "Afternoon":
    date_start_str = f"{current_date}T{afternoon_start}"
    date_end_str = f"{current_date}T{afternoon_end}"
    start_time = pd.to_datetime(date_start_str)
    # Localize to UTC
    start_time = start_time.tz_convert('UTC')
    end_time = pd.to_datetime(date_end_str)
    # Localize to UTC
    end_time = end_time.tz_convert('UTC')
elif option == "Other":
    s_start = st.date_input("Start of the shift:", value=None)
    ts = st.time_input("At start time:", value=None)
    st.write("Your Shift starts at:", s_start,"-",ts)
    s_end = st.date_input("End of the shift:", value=None)
    te = st.time_input("At end time:", value=None)
    st.write("Your Shift ends at:", s_end,"-",te)
    if(s_start != None and s_end != None and ts != None and te != None):
        date_start_str = str(s_start) + "T" + str(ts)+"Z"
        start_time = pd.to_datetime(date_start_str)
        # Localize to UTC
        start_time = start_time.tz_convert('UTC')
        date_end_str = str(s_end) + "T" + str(te)+"Z"
        end_time = pd.to_datetime(date_end_str)
        # Localize to UTC
        end_time = end_time.tz_convert('UTC')
    else:
            st.error("Introdue a valid time window ", icon="🚨")
            start_time = int(0) #Placeholders
            end_time = int(0) #Placeholders
else:
    st.error("Introdue a valid shift ", icon="🚨")
    start_time = int(0) #Placeholders
    end_time = int(0) #Placeholders


#--------------- END SELECTION BOX FOR SHIFT ----------------------------



if (start_time < end_time) and option:
    if uploaded_file:
        print(uploaded_file.name)
        df = pd.read_csv(uploaded_file)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        # Step 2: Filter rows where "Time" column contains a specific value (e.g. "12:00")
        df_filtered = df[(df["timestamp"] >= start_time) & (df["timestamp"] <= end_time)]
    
        # Create empty new DataFrame with specific columns
        new_df_GND = pd.DataFrame(columns=["Satellite", "Orbit", "Antenna", "DOY", "AOS", "LOS", "SMD", "Comments"])
        new_df_SPACE = pd.DataFrame(columns=["Satellite", "Orbit", "Antenna", "DOY", "AOS", "LOS", "SMD","TM","TC", "Comments"])

        # Loop through each row of the original DataFrame
        for index, row in df_filtered.iterrows():
            # Apply transformation logic per row
            if "AOS" in row["text"]:
                
                if "TTC3" in row["text"]:
                    orbit = row["text"].split("#")[1][:5]
                    antenna = "TTC3"
                    AOS = row["text"].split("AOS")[0][:5]
                    LOS = row["text"].split("LOS")[0][-8:-3]
                    TM = row["text"].split("TM")[1][1:4]
                    TC = row["text"].split("TC")[2][1:4]
                    comment = row["text"]
                    print(TM)
                    print(TC)

                    new_row = {
                        "Satellite": row["type"] if row["type"] in ["EPSSG-A1", "EPSSG-B1"] else None,                    
                        "Orbit": orbit.replace('\xa0', '').strip(),
                        "Antenna": antenna,
                        "DOY": datetime.now().timetuple().tm_yday,  # returns DOY
                        "AOS": AOS,
                        "LOS": LOS,
                        "SMD": "N", #At the moment will be always N!
                        "TM": TM,
                        "TC": TC,
                        "Comments": comment.replace('\xa0', '').strip(),
                    }
                    new_df_SPACE = pd.concat([new_df_SPACE, pd.DataFrame([new_row])], ignore_index=True)

                else:
                    orbit = row["text"].split("#")[1][:5]
                    antenna = row["text"].split("#")[2][:4]
                    AOS = row["text"].split("AOS")[0][:5]
                    LOS = row["text"].split("LOS")[0][-8:-3]
                    comment = row["text"]

                    new_row = {
                        "Satellite": row["type"] if row["type"] in ["EPSSG-A1", "EPSSG-B1"] else None,                    
                        "Orbit": orbit.replace('\xa0', '').strip(),
                        "Antenna": antenna,
                        "DOY": datetime.now().timetuple().tm_yday,  # returns DOY
                        "AOS": AOS,
                        "LOS": LOS,
                        "SMD": "N", #At the moment will be always N!
                        "Comments": comment.replace('\xa0', '').strip(),
                    }

                    new_df_GND = pd.concat([new_df_GND, pd.DataFrame([new_row])], ignore_index=True)

        # Step 4: Export to a new file
        try:
            new_df = new_df_SPACE
        except NameError:
            new_df = new_df_SPACE
        csv_file = new_df.to_csv(index=False, header=True)
        # Or to Excel:
        #csv_file = new_df.to_excel('ShiftRepor.xlsx', index=False)
        # Use StringIO to simulate a file
        st.download_button(
            label="Download CSV",
            data=csv_file,
            file_name="ShiftRepor.csv",
            mime="text/csv", #csv
            #icon=":material/download:",
            )  
