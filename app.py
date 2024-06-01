import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
API_PASSWORD = os.getenv('API_PASSWORD')
BASE_URL = os.getenv('BASE_URL')

# Function to track a shipment
def track_shipment(tracking_number):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'api_key': API_KEY,
        'api_password': API_PASSWORD,
        'track_numbers': tracking_number
    }
    response = requests.post(BASE_URL, json=payload, headers=headers)
    return response.json()

# Function to update the status in the sheet
def update_status(df):
    statuses = []
    for number in df['Tracking Number']:
        result = track_shipment(number)
        statuses.append(result)
    df['Status'] = statuses
    return df

# Streamlit UI
st.title("📦🚚 Smart Shipment Tracker: Real-Time Delivery Status Update 📈✨")

uploaded_file = st.file_uploader("Choose a Google Sheet or Excel file", type=["xlsx", "xls", "csv", "json"])

if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1]
    
    if file_extension in ['xlsx', 'xls']:
        df = pd.read_excel(uploaded_file)
    elif file_extension == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_extension == 'json':
        df = pd.read_json(uploaded_file)
    
    st.write("File uploaded successfully!")
    st.write("Tracking Numbers:")
    st.write(df)
    
    if st.button('START Updating Tracking Delivery STATUS!'):
        updated_df = update_status(df)
        
        st.write("Updated Statuses:")
        st.write(updated_df)
        
        # Save the updated file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{uploaded_file.name.split('.')[0]}_{timestamp}.{file_extension}"
        output_path = os.path.join(os.getcwd(), output_file)
        
        if file_extension in ['xlsx', 'xls']:
            updated_df.to_excel(output_path, index=False)
        elif file_extension == 'csv':
            updated_df.to_csv(output_path, index=False)
        elif file_extension == 'json':
            updated_df.to_json(output_path, orient='records')
        
        st.success(f"Updated file saved as {output_file}")

# No need to include st.run() or equivalent; the app is executed via `streamlit run` command
