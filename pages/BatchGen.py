"""

Created on Tue Apr 15 10:00:14 2025
 
Daily Ops Batch Gen 
@author: Sapuppo Andre

"""


import streamlit as st
import pandas as pd
#import numpy as np
#from libraries import ReadXML
from datetime import datetime, date, timezone
import re
#import csv
#from io import StringIO
#import time
#from pages.dailyops import parse_and_merge_multiple

def str2datetime(string):
    
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0, tzinfo=timezone.utc)


def parse_and_merge_multiple(files) -> pd.DataFrame:

    if files:
        namespaces = {"cf": "http://eop-cfi.esa.int/CFI"}
        dfs = []

        for uploaded in files:
            #xml_bytes = uploaded.read()
            df = pd.read_xml(uploaded, xpath=".//cf:Event", namespaces=namespaces)
            dfs.append(df)

        merged_df = pd.concat(dfs, ignore_index=True)

        # Optional: parse and sort by time if column exists
        if "UTC_Start_Time" in merged_df.columns:
            merged_df["UTC_Start_Time"].apply(str2datetime)
            merged_df = merged_df.sort_values("UTC_Start_Time").reset_index(drop=True)

        return merged_df


#TO FIX YOU HAVE TO CREATE THE CORRECT MESSAGE FOR THE CORRECT CASE
def Create_FinalCSV(dataframe,ground):
    
    Uber_DF = pd.DataFrame(columns=["#", "TRUE","Type","Group", "D", "Unnamed: 5"])
    dataframe["UTC_Start_Time"] = (dataframe["UTC_Start_Time"] + pd.to_timedelta(dataframe["Duration"], unit="ms")).dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    for row in dataframe.itertuples(index=False):
        if(ground):
                if row.Entity == "SDA4": message_str = f"""<html><body><p>{row.AOS} - AOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp{row.Sat} #{row.Abs_Orb_No} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp #{row.Entity}<br>Insert Pass Text Here<br>{row.LOS} - LOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp KaBAND: N/OK &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp Total packets generated: XX <br>Az/El:xxx.xxx°/x.xxx° &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp WIMPY's Az/El: xxx° / x° </p></body></html>"""
                if row.Entity == "MCM": message_str = f"<html><body><p>{row.AOS} - {row.Sat} &nbsp &nbsp &nbsp &nbsp #{row.Abs_Orb_No} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp #{row.Entity} &nbsp &nbsp &nbsp KaBAND: OK </p></body></html>"
                if row.Entity == "DBA1": message_str = f"<html><body><p>{row.AOS} - AOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp {row.Sat} &nbsp &nbsp &nbsp &nbsp &nbsp #{row.Abs_Orb_No} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp #{row.Entity}  &nbsp &nbsp  &nbsp &nbsp Az/El:  xxx.xxx&deg; / 0.2&deg;<br>Insert Text Here<br>{row.LOS} - LOS  &nbsp &nbsp &nbsp &nbsp X-BAND: OK &nbsp &nbsp Total packets generated:  xxxxxx.0<br></p></body></html>"

                Uber_DF.loc[len(Uber_DF)] = [
                    row.UTC_Start_Time,
                    'Info',
                    'Activity',
                    'Ground Station',
                    message_str,
                    "230"
                    ]
        else:
            Uber_DF.loc[len(Uber_DF)] = [
                row.UTC_Start_Time,
                    'Info',
                    'Activity',
                    'Spacecraft',
                    f"""<html><body><p>{row.AOS} - AOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp#{row.Sat}&nbsp &nbsp &nbsp#{row.Abs_Orb_No} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp{row.Entity}/BBUX &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp TM: OK &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp TC: OK<br>Insert Pass Text Here<br>{row.LOS} - LOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp Az/El:xxx.xxx°/x.xxx° </p></body></html>""",
                    "232"
                    ]
    return(Uber_DF)
def print_validity(filename):

    # Regular expression to extract start and end validity timestamps
    match = re.search(r"S(\d{14})Z_E(\d{14})Z", filename)

    if match:
        start_time_str = match.group(1)
        end_time_str = match.group(2)

        # Convert to datetime objects
        start_time = datetime.strptime(start_time_str, "%Y%m%d%H%M%S")
        end_time = datetime.strptime(end_time_str, "%Y%m%d%H%M%S")

        # Display validity
        st.markdown(f"The validity of the file is from **{start_time.strftime('%Y-%m-%d at %H:%M:%S')}** "
            f"to **{end_time.strftime('%Y-%m-%d at %H:%M:%S')}**")
    else:
        st.markdown("Could not extract validity period from filename.")


st.header("Controller Enhanced", divider="rainbow")
st.subheader("Export Uberlog file")
st.markdown(''' This tool is used to export the CSV files to Uberlog

**How to use this tool:**    
- 1. Upload the xml files containing the information for the passes.
- 2. Select a valid Period of time for the shift.
- 2. Select what type of pases you're about to take (i.e: TTC).
- 3. Check the passes and Download the CSV file.
- 4. Import it on Uberlog 
            
''')


uploaded_files = st.file_uploader(
    "Upload the xml files", accept_multiple_files=True
)
if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        name = uploaded_file.name
        print_validity(name)


Pases_DF = {
    "SGA1": pd.DataFrame,
    "SGA2": pd.DataFrame,
    "SGA3": pd.DataFrame,
    "SGB1": pd.DataFrame,
    "SGB2": pd.DataFrame,
    "SGB3": pd.DataFrame
}

Pases_DF2 = parse_and_merge_multiple(uploaded_files)

    
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
morning_start = "08:00:00"
afternoon_start = "12:30:00"
afternoon_end = "18:30:00"


#Localize the timezone
local_tz = "Europe/Berlin"

# Combine both parts
if option == "Morning":
    date_start_str = f"{current_date}T{morning_start}"
    date_end_str = f"{current_date}T{afternoon_start}"
    start_time = pd.to_datetime(date_start_str)
    # Localize to UTC
    start_time = start_time.tz_localize(local_tz).tz_convert('UTC')
    end_time = pd.to_datetime(date_end_str)
    # Localize to UTC
    end_time = end_time.tz_localize(local_tz).tz_convert('UTC')
elif option == "Afternoon":
    date_start_str = f"{current_date}T{afternoon_start}"
    date_end_str = f"{current_date}T{afternoon_end}"
    start_time = pd.to_datetime(date_start_str)
    # Localize to UTC
    start_time = start_time.tz_localize(local_tz).tz_convert('UTC')
    end_time = pd.to_datetime(date_end_str)
    # Localize to UTC
    end_time = end_time.tz_localize(local_tz).tz_convert('UTC')
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
        start_time = start_time.tz_localize(local_tz).tz_convert('UTC')
        date_end_str = str(s_end) + "T" + str(te)+"Z"
        end_time = pd.to_datetime(date_end_str)
        # Localize to UTC
        end_time = end_time.tz_localize(local_tz).tz_convert('UTC')
    else:
            st.error("Introdue a valid time window ", icon="🚨")
            start_time = int(0) #Placeholders
            end_time = int(0) #Placeholders
else:
    st.error("Introdue a valid shift ", icon="🚨")
    start_time = int(0) #Placeholders
    end_time = int(0) #Placeholders


#--------------- END SELECTION BOX FOR SHIFT ----------------------------


#--------------- START SELECTION BOX FOR GROUND/SPACE -------------------------

#Select if Spacon or Groundcon
label2 = "Are you Groundcon or Spacon?"
list_2 = ("Groundcon", "Spacon")

option2 = st.selectbox(
    label2,
    list_2,
    placeholder="Select shift...",
)
#--------------- END SELECTION BOX FOR GROUND/SPACE ----------------------------

if option2 == 'Groundcon':
     stations = ['SDA4', 'DBA1', 'MCM']
     groundcon = True #This variable is created to simplify the other if cases lather
else:
     stations = ['TTC3']
     groundcon = False

event_types_to_keep = ["STAT_VIS_Z"]  #I only keep tha AOS0!

if (start_time < end_time) and option and option2:
            #ttc_check = st.toggle("Take TTC3 passes")
            #sda5_passes = st.toggle("Take SDA5 passes")
            #sda4_passes = st.toggle("Take SDA4 passes")
            #dba_passes = st.toggle("Take DBA passes")
            

                #The first row of the df. Everything will be concatenated from this one.
                Uber_DF = pd.DataFrame(columns=["#", "TRUE","Type","Group", "D", "Unnamed: 5"])
                if uploaded_files:
                    print(uploaded_files)
                    
                
                    #data_name = file.name

                    # Assign the DataFrame correctly
                    
                    #Pases_DF2 = ReadXML.Read_XML(file) #Already created the Merged DF!
                    Pases_DF2["UTC_Start_Time"] = pd.to_datetime(Pases_DF2["UTC_Start_Time"])
                    df_filtered = Pases_DF2[Pases_DF2["Event_Type"].isin(event_types_to_keep)] #I'm filtering the columns
                    df_filtered = df_filtered[df_filtered['Entity'].isin(stations)]
                    st.markdown(f"You are {option2}, you will check {stations} stations")
                    
                    df_filtered = df_filtered[(df_filtered["UTC_Start_Time"] >= start_time) & (df_filtered["UTC_Start_Time"] <= end_time)]
                    df_filtered = df_filtered.loc[df_filtered.groupby(['Abs_Orb_No', 'Entity'])['Duration'].idxmax()]
                    df_filtered["AOS"] = df_filtered["UTC_Start_Time"].dt.strftime("%H:%M")
                    df_filtered["LOS"] = (df_filtered["UTC_Start_Time"] + pd.to_timedelta(df_filtered["Duration"], unit="ms")).dt.strftime("%H:%M")
                    st.dataframe(
                                df_filtered[["Sat","Abs_Orb_No","AOS", "LOS","Entity"]],
                                column_config={
                                    "Sat": "Satellite",
                                    "Abs_Orb_no": "Orbit Number",
                                    "AOS": "AoS",
                                    "LOS": "LoS",
                                    "Entity": "Antenna",
                                },
                                hide_index=True,
                            )
                    df_filtered = df_filtered.sort_values("UTC_Start_Time").reset_index(drop=True)
                    Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered, groundcon)], ignore_index=True)

                
                #Uber_DF = Uber_DF.reset_index(drop=True) 
                Uber_DF['#'] = pd.to_datetime(Uber_DF['#']).dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


                # Trim milliseconds to 2 decimal places
                Uber_DF['#'] = Uber_DF['#'].str[:-4] + 'Z'
                
                new_row = pd.DataFrame([{'#': '#', 'TRUE': 'true',"Type": "D"}])
                Uber_DF = pd.concat([new_row,Uber_DF],ignore_index=True)
    
                csv_file = Uber_DF.to_csv(index=False, header=False)
    
                # Use StringIO to simulate a file
                st.download_button(
                    label="Download CSV",
                    data=csv_file,
                    file_name=f"Batch_{option}_{option2}.csv",
                    mime="text/csv",
                    #icon=":material/download:",
                    )  
else:
            st.markdown("Introdue a valid start and end Date ")



