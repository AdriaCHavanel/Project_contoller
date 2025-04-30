"""

Created on Tue Apr 08 10:00:14 2025
 
Daily Ops Batch Gen 
@author: Sapuppo Andre

"""

import streamlit as st
import pandas as pd
#import numpy as np
from datetime import datetime, date, timezone


def str2datetime(string):
    
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0, tzinfo=timezone.utc)

def ReadFirstPass(df, station, shift):

    if df is not None:
        print(uploaded_files)

        # Define the fixed time
        morning_start = "08:00:00"
        afternoon_start = "12:30:00"
        afternoon_end = "18:30:00"
        night_end = "23:30:00"

        #Localize the timezone
        local_tz = "Europe/Berlin"
        
        # Combine both parts
        if shift == "Morning":
            date_start_str = f"{current_date}T{morning_start}"
            date_end_str = f"{current_date}T{afternoon_start}"
            start_time = pd.to_datetime(date_start_str)
            # Localize to UTC
            start_time = start_time.tz_localize(local_tz).tz_convert('UTC')
            end_time = pd.to_datetime(date_end_str)
            # Localize to UTC
            end_time = end_time.tz_localize(local_tz).tz_convert('UTC')
        elif shift == "Afternoon":
            date_start_str = f"{current_date}T{afternoon_start}"
            date_end_str = f"{current_date}T{afternoon_end}"
            start_time = pd.to_datetime(date_start_str)
            # Localize to UTC
            start_time = start_time.tz_localize(local_tz).tz_convert('UTC')
            end_time = pd.to_datetime(date_end_str)
            # Localize to UTC
            end_time = end_time.tz_localize(local_tz).tz_convert('UTC')
        elif shift == "Night":
            date_start_str = f"{current_date}T{afternoon_end}"
            date_end_str = f"{current_date}T{night_end}"
            start_time = pd.to_datetime(date_start_str)
            # Localize to UTC
            start_time = start_time.tz_localize(local_tz).tz_convert('UTC')
            end_time = pd.to_datetime(date_end_str)
            # Localize to UTC
            end_time = end_time.tz_localize(local_tz).tz_convert('UTC')
            
            
            
        
        event_types_to_keep = ["STAT_VIS_Z"]  #STAT_VIS_Z should be AOS0!!!

        # Filter Station (Depends if I am searching for the first SDA, DBA or TTC3)

        filtered_df = df[df["Event_Type"].isin(event_types_to_keep)] #I'm filtering the columns
        filtered_df = filtered_df[filtered_df['Entity'].isin(station)]
        filtered_df = filtered_df[(filtered_df["UTC_Start_Time"].apply(str2datetime)  >= start_time) & 
        (filtered_df["UTC_Start_Time"].apply(str2datetime)  <= end_time)]
            
            #first shift pass of the station:
            #print(type(filtered_df['UTC_Start_Time'].iloc[0])) #It.s DONE, just put return instead of print!!!

        return filtered_df['UTC_Start_Time'].iloc[0]



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


uploaded_files = st.file_uploader(
    "Upload the xml files", accept_multiple_files=True
    )


merged_df = parse_and_merge_multiple(uploaded_files)

#Adding a selection box to divide AM tasks to Once every shift or Once every pass
#This will need an update when we will have the real shifts    
label2 = "When is your shift?"
list_2 = ("Morning", "Afternoon", "Night")

option2 = st.selectbox(
    label2,
    list_2,
    placeholder="Select shift...",
)

# Get the current date in "YYYY-MM-DD" format
current_date = datetime.utcnow().strftime("%Y-%m-%d")

# Define the fixed time (To fix when the date changes again!)
morning_start = "06:00:00Z"
afternoon_start = "10:30:00Z"
afternoon_end = "16:30:00Z"

#Select if Spacon or Groundcon
label = "Are you Groundcon or Spacon?"
list_ = ("Groundcon", "Spacon")

option = st.selectbox(
    label,
    list_,
    placeholder="Select shift...",

)

if option2 == 'Night':
    st.warning("Be careful, we are not doing Night shifts yet! The time slots are not reliable.")

Uber_DF = pd.DataFrame(columns=["#", "TRUE","Type","Group", "D", "Unnamed: 5"])

#datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
# Get the current date in "YYYY-MM-DD" format
#current_date = datetime.utcnow().strftime("%Y-%m-%d")
today = date.today().weekday()
# Define the Daily - AM fixed time
AM = "09:00:00Z"
#Build UTC AM string
UTC_AM = f"{current_date}T{AM}"

#Can all of this be cycled?

if option == 'Groundcon':
    logbook = '230'

    GSTMC_Rep_label = "GSTMC Reports"
    #GSTMC_Rep = st.checkbox(GSTMC_Rep_label, value=False)
    GSTMC_Rep = False
    GSTMC_Rep_msg = "GSTMC Reports Retrieval"
    GSTMC_Rep_time = UTC_AM
    GSTMC_Rep_group = "Ground Station"
    GSTMC_Rep_type = "Checks"



    SDA_Rep_label = "SDA Reports"
    #SDA_Rep = st.checkbox(SDA_Rep_label, value=False)
    SDA_Rep = True
    SDA_Rep_msg = "SDA Station Reports Check"
    SDA_Rep_time = ReadFirstPass(merged_df, ["SDA4"], option2) #This will be the First pass per shift. WE NEED TO INTEGRATE iT WITH THE PASS BATCH
    SDA_Rep_group = "Ground Station"
    SDA_Rep_type = "Checks"

    DBA_Rep_label = "DBA Reports"
    DBA_Rep = True
    #DBA_Rep = st.checkbox(DBA_Rep_label, value=False)
    DBA_Rep_msg = "DBA Station Reports Check"
    DBA_Rep_time = ReadFirstPass(merged_df, ["DBA1"], option2) #To be changed to the 1st pass of the shift!!!!
    DBA_Rep_group = "Ground Station"
    DBA_Rep_type = "Checks"


    #print(DBA_Rep_time)

    SDA_OEM_label = "SDA OEMs"
    SDA_OEM = False
    #SDA_OEM = st.checkbox(SDA_OEM_label, value=False)
    SDA_OEM_msg = "SDA4 / 5 OEM file check"
    SDA_OEM_time = UTC_AM
    SDA_OEM_group = "Ground Station"
    SDA_OEM_type = "Checks"

    DBA_OEM_label = "DBA OEMs"
    DBA_OEM = False
    #DBA_OEM = st.checkbox(DBA_OEM_label, value=False)
    DBA_OEM_msg = "DBA OEM file check"
    DBA_OEM_time = UTC_AM
    DBA_OEM_group = "Ground Station"
    DBA_OEM_type = "Checks"
    
    #IBA_AUX_label = "IBA AUX files"
    #IBA_AUX = False
    ##IBA_AUX = st.checkbox(IBA_AUX_label, value=False)
    #IBA_AUX_msg = "IBA and POFD Aux file check"
    #IBA_AUX_time = UTC_AM
    #IBA_AUX_group = "PDP"
    #IBA_AUX_type = "Checks"

    POFD_AUX_label = "POFD and IBA AUX files" #POFD and IBA files could be logged together!
    POFD_AUX = False
    #POFD_AUX = st.checkbox(POFD_AUX_label, value=False)
    POFD_AUX_msg = "IBA and POFD Aux file check"
    POFD_AUX_time = UTC_AM
    POFD_AUX_group = "PDP"
    POFD_AUX_type = "Checks"

    SCH_AUX_label = "SCH AUX files"
    SCH_AUX = False
    #SCH_AUX = st.checkbox(SCH_AUX_label, value=False)
    SCH_AUX_msg = "YOU SHOULD NOT LOG THIS YET"
    SCH_AUX_time = UTC_AM
    SCH_AUX_group = "PDP"
    SCH_AUX_type = "Checks"
    
    AUX_view_label = "AUX data view"
    AUX_view = False
    #AUX_view = st.checkbox(AUX_view_label, value=False)
    AUX_view_msg = "Auxiliary data ingestion check"
    AUX_view_time = UTC_AM
    AUX_view_group = "PDP"
    AUX_view_type = "Checks"

    SDA_MDR_label = "SDA Monitoring Data Reports"
    SDA_MDR = True
    #SDA_MDR = st.checkbox(AUX_view_label, value=False)
    SDA_MDR_msg = "SDA Monitoring Data Reports Check"
    SDA_MDR_time = ReadFirstPass(merged_df, ["SDA4"], option2)
    SDA_MDR_group = "Ground Station"
    SDA_MDR_type = "Checks"

    DBA_MDR_label = "DBA Monitoring Data Reports"
    DBA_MDR = True
    #DBA_MDR = st.checkbox(AUX_view_label, value=False)
    DBA_MDR_msg = "DBA Monitoring Data Reports Check"
    DBA_MDR_time = ReadFirstPass(merged_df, ["DBA1"], option2)
    DBA_MDR_group = "Ground Station"
    DBA_MDR_type = "Checks"
 

    SDA_SCH_label = "SDA weekly schedule"
    #SDA_SCH = st.checkbox(SDA_SCH_label, value=False)
    SDA_SCH = False
    if today == 4 and option2 == 'Morning':
        #st.warning(f"You are supposed to check this on Friday! Today is {datetime.now().strftime('%A')}")
        SDA_SCH = True
    SDA_SCH_msg = "SDA weekly schedule reception check"
    SDA_SCH_time = UTC_AM
    SDA_SCH_group = "MPS"
    SDA_SCH_type = "Checks"

    DBA_SCH_label = "DBA weekly schedule"
    #DBA_SCH = st.checkbox(DBA_SCH_label, value=False)
    DBA_SCH = False
    if today == 4 and option2 == 'Morning':
        #st.warning(f"You are supposed to check this on Friday! Today is {datetime.now().strftime('%A')}")
        DBA_SCH = True
    DBA_SCH_msg = "DBA weekly schedule reception check"
    DBA_SCH_time = UTC_AM
    DBA_SCH_group = "MPS"
    DBA_SCH_type = "Checks"
    

    if option2 == 'Morning':
         GSTMC_Rep = True
         SDA_OEM = True
         DBA_OEM = True
         IBA_AUX = True
         POFD_AUX = True
         SCH_AUX = True
         AUX_view = True


    checklist = [GSTMC_Rep, SDA_Rep, DBA_Rep, SDA_OEM, DBA_OEM, POFD_AUX, SCH_AUX, AUX_view, SDA_SCH, DBA_SCH, SDA_MDR, DBA_MDR]
    msglist = [GSTMC_Rep_msg, SDA_Rep_msg, DBA_Rep_msg, SDA_OEM_msg, DBA_OEM_msg, POFD_AUX_msg, SCH_AUX_msg, AUX_view_msg, SDA_SCH_msg, DBA_SCH_msg, SDA_MDR_msg, DBA_MDR_msg]
    timelist = [GSTMC_Rep_time, SDA_Rep_time, DBA_Rep_time, SDA_OEM_time, DBA_OEM_time, POFD_AUX_time, SCH_AUX_time, AUX_view_time, SDA_SCH_time, DBA_SCH_time, SDA_MDR_time, DBA_MDR_time]
    grouplist = [GSTMC_Rep_group, SDA_Rep_group, DBA_Rep_group, SDA_OEM_group, DBA_OEM_group, POFD_AUX_group, SCH_AUX_group, AUX_view_group, SDA_SCH_group, DBA_SCH_group, SDA_MDR_group, DBA_MDR_group]
    typelist = [GSTMC_Rep_type, SDA_Rep_type, DBA_Rep_type, SDA_OEM_type, DBA_OEM_type, POFD_AUX_type, SCH_AUX_type, AUX_view_type, SDA_SCH_type, DBA_SCH_type, SDA_MDR_type, DBA_MDR_type]


else:
    logbook = '232'
    TTC3_OEMs_label = "TTC3 OEMs"
    TTC3_OEMs = False
    #TTC3_OEMs = st.checkbox(TTC3_OEMs_label, value=False)
    TTC3_OEMs_msg = "TTC3 OEM file check"
    TTC3_OEMs_time = UTC_AM
    TTC3_OEMs_group = "Ground Station"
    TTC3_OEMs_type = "Checks"

    SYSLOG_label = "SYSLOG clear"
    SYSLOG = True
    #SYSLOG = st.checkbox(SYSLOG_label, value=False)
    SYSLOG_msg = "!!! Log inside the pass you clear the log !!!"
    SYSLOG_time = ReadFirstPass(merged_df, ["TTC3"], option2) 
    SYSLOG_group = "Spacecraft"   #!!!!You have to change this wrt the satellite you want to input!!!!!!
    SYSLOG_type = "EPSSG-A1"

    MPS_PROD_label = "MPS product receptions"
    #MPS_PROD = st.checkbox(MPS_PROD_label, value=False)
    MPS_PROD = False
    if today == 4 and option2 == 'Morning':
        #st.warning("You are supposed to check this on Friday!")
        MPS_PROD = True

    
    MPS_PROD_msg = "Mission Planning Products Reception and Processing on OAS"
    MPS_PROD_time = UTC_AM #It has to be on Friday!!! Put a check with the Datetime!
    MPS_PROD_group = "MPS"
    MPS_PROD_type = "Checks"

    TTC3_SCH_label = "TTC3 weekly schedule"
    #TTC3_SCH = st.checkbox(TTC3_SCH_label, value=False)
    TTC3_SCH = False
    if today == 4 and option2 == 'Morning':
        #st.warning(f"You are supposed to check this on Friday! Today is {datetime.now().strftime('%A')}")
        TTC3_SCH = True
    TTC3_SCH_msg = "TTC3 weekly schedule reception check"
    TTC3_SCH_time = UTC_AM #It has to be on Friday!!! Put a check with the Datetime!
    TTC3_SCH_group = "MPS"
    TTC3_SCH_type = "Checks"

    if option2 == 'Morning':
         TTC3_OEMs = True
         

    checklist = [TTC3_OEMs, SYSLOG, MPS_PROD, TTC3_SCH] 
    msglist = [TTC3_OEMs_msg, SYSLOG_msg, MPS_PROD_msg, TTC3_SCH_msg] 
    timelist = [TTC3_OEMs_time, SYSLOG_time, MPS_PROD_time, TTC3_SCH_time] 
    grouplist = [TTC3_OEMs_group, SYSLOG_group, MPS_PROD_group, TTC3_SCH_group] 
    typelist = [TTC3_OEMs_type, SYSLOG_type, MPS_PROD_type, TTC3_SCH_type] 



MCS_REB_label = "MCS weekly reboot"
#MCS_REB = st.checkbox(MCS_REB_label, value=False)
MCS_REB = False
OAS_RES = False
if  option2 == 'Morning' and today == 2:
        #st.warning(f"You are supposed to check this on Wednesday! Today is {datetime.now().strftime('%A')}")
        MCS_REB = True
        OAS_RES = True

MCS_REB_msg = "MCS Weekly reboot"
MCS_REB_time = UTC_AM #It has to be on Wednesday!!! Put a check with the Datetime!
MCS_REB_group = "MCS"
MCS_REB_type = "Activity"

OAS_RES_label = "OAS weekly restart"
#OAS_RES = st.checkbox(OAS_RES_label, value=False)
#if OAS_RES and today != 2:
        #st.warning(f"You are supposed to check this on Wednesday! Today is {datetime.now().strftime('%A')}")
OAS_RES_msg = "OAS Weekly restart"
OAS_RES_time = UTC_AM #It has to be on Wednesday!!! Put a check with the Datetime!
OAS_RES_group = "MCS"
OAS_RES_type = "Activity"


checklist.append(MCS_REB)
checklist.append(OAS_RES)
msglist.append(MCS_REB_msg)
msglist.append(OAS_RES_msg)
timelist.append(MCS_REB_time)
timelist.append(OAS_RES_time)
grouplist.append(MCS_REB_group)
grouplist.append(OAS_RES_group)
typelist.append(MCS_REB_type)
typelist.append(OAS_RES_type)



#print(checklist)


message_str = f"<html><body><p> - {msglist} - </p></body></html>"
#print(message_str)
severity = 'Info'

for i, selection in enumerate(checklist):
    if selection:
        #print(i)
        Uber_DF = pd.concat([Uber_DF, pd.DataFrame([[
                        timelist[i],
                        severity,
                        typelist[i],
                        grouplist[i],
                        f"<html><body><p> {msglist[i]} </p></body></html>",
                        logbook,
                        ]], columns=Uber_DF.columns)], ignore_index=True)
    
#print(Uber_DF)


# Generate and download the CSV via a dedicated button
csv_file = Uber_DF.to_csv(index=False, header=False)
    
st.download_button(
                    label="Download CSV",
                    data=csv_file,
                    file_name=f"{option}T{option2}.csv",
                    mime="text/csv",
                    #icon=":material/download:",
                    )  

    
