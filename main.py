import streamlit as st
logoname = "Logo.png"
st.logo(logoname, icon_image=logoname)
pages = {
    "Tools": [
        st.Page("pages/page_1.py", title="Export Uberlog"),
        st.Page("pages/page_2.py", title="SDA and DBA pointer"),
    ],
    "Assistant": [
        st.Page("pages/controller_assistant.py", title="Controller Assistant"),
    ]
}
pg = st.navigation(pages)
pg.run()
