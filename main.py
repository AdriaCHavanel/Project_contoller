import streamlit as st

pages = {
    "Tools": [
        st.Page("pages/page_1.py", title="Export Uberlog"),
        st.Page("pages/page_2.py", title="SG Passes Viewer"),
    ]
}
pg = st.navigation(pages)
pg.run()
