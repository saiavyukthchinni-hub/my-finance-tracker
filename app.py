import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- GOOGLE SHEETS CONNECTION ---
# Replace this with your actual Google Sheet URL
SQL_URL = "SQL_URL = "https://docs.google.com/spreadsheets/d/1JbUjQvjlqxF5RwHN9ZFZdpAR5zKP9vbgSm9JBeZc9Ow/"

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

    # --- LOADING DATA WITH ERROR HANDLING ---
    try:
        # Line 35: This is the critical connection point
        data = conn.read(spreadsheet=SQL_URL, usecols=[0, 1, 2], ttl=5)
        data = data.dropna(how="all")
    except Exception as e:
        st.error("⚠️ Connection to Google Sheets Failed")
        st.info(f"**Technical Detail:** {e}")
        st.write("---")
        st.write("### How to fix this:")
        st.write("1. **Check your URL:** Ensure `SQL_URL` at the top of your script is a valid link.")
        st.write("2. **Check Permissions:** Open your Google Sheet, click **Share**, and set it to **'Anyone with the link'** as **'Editor'**.")
        st.write("3. **Check Secrets:** Ensure your Streamlit Cloud Secrets are configured correctly.")
        st.stop() # Prevents the rest of the app from crashing

    # --- APP LAYOUT (Only runs if connection is successful) ---
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
                try:
                    conn.update(spreadsheet=SQL_URL, data=updated_df)
                    st.success("Sent to Google Sheets!")
                    st.rerun()
                except Exception as update_error:
                    st.error(f"Could not update sheet: {update_error}")

    # --- VISUALS ---
    if not data.empty:
        with col_chart:
            # Ensure column names match your sheet exactly
            fig = px.pie(data, values='Amount', names='Category', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Cloud History")
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No data in Google Sheets yet.")





