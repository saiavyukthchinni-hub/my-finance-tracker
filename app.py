import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- GOOGLE SHEETS CONNECTION ---
# Replace this with your actual Google Sheet URL
SQL_URL = "https://docs.google.com/spreadsheets/d/your-id-here/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- PASSWORD PROTECTION (Same as before) ---
PASSWORD = "Prakash@82"


def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password_input")
        return False
    return st.session_state["password_correct"]


def password_entered():
    if st.session_state["password_input"] == PASSWORD:
        st.session_state["password_correct"] = True
    else:
        st.error("Incorrect Password")


if check_password():
    st.title("☁️ Cloud Connected Finance Tracker")

    # Load data from Google Sheets
    data = conn.read(spreadsheet=SQL_URL, usecols=[0, 1, 2], ttl=5)
    data = data.dropna(how="all")

    col_form, col_chart = st.columns(2)

    with col_form:
        st.subheader("Add Expense")
        with st.form("input_form", clear_on_submit=True):
            cat = st.text_input("Category")
            amt = st.number_input("Amount", min_value=0.0)
            submit = st.form_submit_button("Save to Cloud")

            if submit and cat:
                new_row = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Category": cat, "Amount": amt}])
                updated_df = pd.concat([data, new_row], ignore_index=True)

                # Update Google Sheets
                conn.update(spreadsheet=SQL_URL, data=updated_df)
                st.success("Sent to Google Sheets!")
                st.rerun()

    # --- VISUALS ---
    if not data.empty:
        with col_chart:
            fig = px.pie(data, values='Amount', names='Category', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Cloud History")
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No data in Google Sheets yet.")