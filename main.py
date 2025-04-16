import streamlit as st
logoname = "../LOGO_COntroller.png"
st.logo(logoname, icon_image=logoname)
pages = {
    "Main": [
        st.Page("pages/Welcome.py",title="Home"),
    ],
    
    "Tools": [
        st.Page("pages/page_1.py", title="Export Uberlog"),
        st.Page("pages/page_2.py", title="SDA and DBA pointer"),
        st.Page("pages/Download_xmlfiles.py", title="Download FDS xml files"),
        st.Page("pages/BatchGen.py", title="Final Batch Gen"),
        st.Page("pages/dailyops.py", title="DailyOps Uberlog"),
        st.Page("pages/ShiftReport.py", title="Shift Reports Downloader"),


    ],
   # "Assistant": [
   #     st.Page("pages/controller_assistant.py", title="Controller Assistant"),
   #]
}
pg = st.navigation(pages)
pg.run()
