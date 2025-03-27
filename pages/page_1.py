import streamlit as st
import pandas as pd
import numpy as np
from libraries import ReadXML
from datetime import datetime
import re
import csv
from io import StringIO
def Create_FinalCSV(dataframe,ground):
    
    Uber_DF = pd.DataFrame(columns=["#", "TRUE","Type","Group", "D", "Unnamed: 5"])
    dataframe["UTC_Start_Time"] = (dataframe["UTC_Start_Time"] + pd.to_timedelta(dataframe["Duration"], unit="ms")).dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    for row in dataframe.itertuples(index=False):
        if(ground):
                Uber_DF.loc[len(Uber_DF)] = [
                    row.UTC_Start_Time,
                    'Info',
                    'Activity',
                    'Ground Station',
                    f"""<html><body><p>{row.AOS} - AOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp{row.Sat} #{row.Abs_Orb_No} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp #{row.Entity}<br>Insert Pass Text Here<br>{row.LOS} - LOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp KaBAND: N/OK &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp Total packets generated: XX <br>Az/El:xxx.xxx°/x.xxx° &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp WIMPY's Az/El: xxx° / x° </p></body></html>""",
                    "230"
                    ]
        else:
            Uber_DF.loc[len(Uber_DF)] = [
                row.UTC_Start_Time,
                    'Info',
                    'Activity',
                    'Spacecraft',
                    f"""<html><body><p>{row.AOS} - AOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp{row.Sat}#{row.Abs_Orb_No} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp{row.Entity}/BBUX &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp TM: OK &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp TC: OK<br>Insert Pass Text Here<br>{row.LOS} - LOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp Az/El:xxx.xxx°/x.xxx° </p></body></html>""",
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
    if (start_time < end_time):
        ttc_check = st.toggle("Take TTC3 passes")
        sda5_passes = st.toggle("Take SDA5 passes")
        sda4_passes = st.toggle("Take SDA4 passes")
        dba_passes = st.toggle("Take DBA passes")
        if ttc_check or sda4_passes or sda5_passes or dba_passes:
            Uber_DF = pd.DataFrame(columns=["#", "TRUE","Type","Group", "D", "Unnamed: 5"])
            if uploaded_files is not None:
                
                for file in uploaded_files:
                    data_name = file.name

                    # Assign the DataFrame correctly
                    if "SGA1" in data_name:
                        Pases_DF["SGA1"] = ReadXML.Read_XML(file)
                        Pases_DF["SGA1"]["UTC_Start_Time"] = pd.to_datetime(Pases_DF["SGA1"]["UTC_Start_Time"])
                        if ttc_check:
                            st.markdown("TTC3 selected")
                            df_filtered = Pases_DF["SGA1"][Pases_DF["SGA1"]["Entity"] == "TTC3"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,False)], ignore_index=True)

                            

                        if sda5_passes:
                            st.markdown("SDA5 selected")
                            df_filtered = Pases_DF["SGA1"][Pases_DF["SGA1"]["Entity"] == "SDA5"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if sda4_passes:
                            st.markdown("SDA4 selected")
                            df_filtered = Pases_DF["SGA1"][Pases_DF["SGA1"]["Entity"] == "SDA4"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if dba_passes:
                            st.markdown("DBA1 selected")
                            df_filtered = Pases_DF["SGA1"][Pases_DF["SGA1"]["Entity"] == "DBA1"]
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
                            for row in df_filtered.itertuples(index=False):
                                Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
#-------------------------------SGA2----------------------------------------------------------
                    elif "SGA2" in data_name:
                        Pases_DF["SGA2"] = ReadXML.Read_XML(file)
                        Pases_DF["SGA2"]["UTC_Start_Time"] = pd.to_datetime(Pases_DF["SGA2"]["UTC_Start_Time"])
                        if ttc_check:
                            st.markdown("TTC3 selected")
                            df_filtered = Pases_DF["SGA2"][Pases_DF["SGA2"]["Entity"] == "TTC3"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,False)], ignore_index=True)

                            

                        if sda5_passes:
                            st.markdown("SDA5 selected")
                            df_filtered = Pases_DF["SGA2"][Pases_DF["SGA2"]["Entity"] == "SDA5"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if sda4_passes:
                            st.markdown("SDA4 selected")
                            df_filtered = Pases_DF["SGA2"][Pases_DF["SGA2"]["Entity"] == "SDA4"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if dba_passes:
                            st.markdown("DBA1 selected")
                            df_filtered = Pases_DF["SGA2"][Pases_DF["SGA2"]["Entity"] == "DBA1"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
#----------------------------------------SGA3-------------------------------------------------
                    elif "SGA3" in data_name:
                        Pases_DF["SGA3"] = ReadXML.Read_XML(file)
                        Pases_DF["SGA3"]["UTC_Start_Time"] = pd.to_datetime(Pases_DF["SGA3"]["UTC_Start_Time"])
                        if ttc_check:
                            st.markdown("TTC3 selected")
                            df_filtered = Pases_DF["SGA3"][Pases_DF["SGA3"]["Entity"] == "TTC3"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,False)], ignore_index=True)

                            

                        if sda5_passes:
                            st.markdown("SDA5 selected")
                            df_filtered = Pases_DF["SGA3"][Pases_DF["SGA3"]["Entity"] == "SDA5"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if sda4_passes:
                            st.markdown("SDA4 selected")
                            df_filtered = Pases_DF["SGA3"][Pases_DF["SGA3"]["Entity"] == "SDA4"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if dba_passes:
                            st.markdown("DBA1 selected")
                            df_filtered = Pases_DF["SGA3"][Pases_DF["SGA3"]["Entity"] == "DBA1"]
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
                            for row in df_filtered.itertuples(index=False):
                                Uber_DF.loc[len(Uber_DF)] = [
                                    row.UTC_Start_Time,
                                    'Entry',
                                    f"#{row.Abs_Orb_No}",
                                    row.Sat,
                                    f"""<html><body><p>{row.AOS} - AOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp{row.Sat} #{row.Abs_Orb_No} &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp{row.Entity}<br>Insert Pass Text Here<br> {row.LOS} - LOS &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp Az/El:xxx.xxx/x.xxx </p></body></html>""",
                                    "5ad5c6b7a585c614bac889cd"
                                ]
                    elif "SGB1" in data_name:
                        Pases_DF["SGB1"] = ReadXML.Read_XML(file)
                        Pases_DF["SGB1"]["UTC_Start_Time"] = pd.to_datetime(Pases_DF["SGB1"]["UTC_Start_Time"])
                        if ttc_check:
                            st.markdown("TTC3 selected")
                            df_filtered = Pases_DF["SGB1"][Pases_DF["SGB1"]["Entity"] == "TTC3"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,False)], ignore_index=True)

                            

                        if sda5_passes:
                            st.markdown("SDA5 selected")
                            df_filtered = Pases_DF["SGB1"][Pases_DF["SGB1"]["Entity"] == "SDA5"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if sda4_passes:
                            st.markdown("SDA4 selected")
                            df_filtered = Pases_DF["SGB1"][Pases_DF["SGB1"]["Entity"] == "SDA4"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if dba_passes:
                            st.markdown("DBA1 selected")
                            df_filtered = Pases_DF["SGB1"][Pases_DF["SGB1"]["Entity"] == "DBA1"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                    elif "SGB2" in data_name:
                        Pases_DF["SGB2"] = ReadXML.Read_XML(file)
                        Pases_DF["SGB2"]["UTC_Start_Time"] = pd.to_datetime(Pases_DF["SGB2"]["UTC_Start_Time"])
                        if ttc_check:
                            st.markdown("TTC3 selected")
                            df_filtered = Pases_DF["SGB2"][Pases_DF["SGB2"]["Entity"] == "TTC3"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,False)], ignore_index=True)

                            

                        if sda5_passes:
                            st.markdown("SDA5 selected")
                            df_filtered = Pases_DF["SGB2"][Pases_DF["SGB2"]["Entity"] == "SDA5"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if sda4_passes:
                            st.markdown("SDA4 selected")
                            df_filtered = Pases_DF["SGB2"][Pases_DF["SGB2"]["Entity"] == "SDA4"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if dba_passes:
                            st.markdown("DBA1 selected")
                            df_filtered = Pases_DF["SGB2"][Pases_DF["SGB2"]["Entity"] == "DBA1"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                    elif "SGB3" in data_name:
                        Pases_DF["SGB3"] = ReadXML.Read_XML(file)
                        Pases_DF["SGB3"]["UTC_Start_Time"] = pd.to_datetime(Pases_DF["SGB3"]["UTC_Start_Time"])
                        if ttc_check:
                            st.markdown("TTC3 selected")
                            df_filtered = Pases_DF["SGB3"][Pases_DF["SGB3"]["Entity"] == "TTC3"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,False)], ignore_index=True)

                            

                        if sda5_passes:
                            st.markdown("SDA5 selected")
                            df_filtered = Pases_DF["SGB3"][Pases_DF["SGB3"]["Entity"] == "SDA5"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if sda4_passes:
                            st.markdown("SDA4 selected")
                            df_filtered = Pases_DF["SGB3"][Pases_DF["SGB3"]["Entity"] == "SDA4"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
                        if dba_passes:
                            st.markdown("DBA1 selected")
                            df_filtered = Pases_DF["SGB3"][Pases_DF["SGB3"]["Entity"] == "DBA1"]
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
                            Uber_DF = pd.concat([Uber_DF, Create_FinalCSV(df_filtered,True)], ignore_index=True)
            Uber_DF = Uber_DF.reset_index(drop=True) 
            # Uber_DF['#'] = pd.to_datetime(Uber_DF['#']).dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            # Trim milliseconds to 2 decimal places
            Uber_DF['#'] = Uber_DF['#'].str[:-4] + 'Z'
            new_row = pd.DataFrame([{'#': '#', 'TRUE': 'true',"Type": "D"}])
            Uber_DF = pd.concat([new_row,Uber_DF],ignore_index=True)

            csv_file = Uber_DF.to_csv(index=False, header=False)

            # Use StringIO to simulate a file
            st.download_button(
                label="Download CSV",
                data=csv_file,
                file_name="data.csv",
                mime="text/csv",
                icon=":material/download:",
                )  
        else:
              st.markdown("Introdue a valid Station ")
    else:
        st.markdown("Introdue a valid start and end Date ")
else:
    st.markdown("Introdue a valid start and end Date ")


