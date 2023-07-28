from flask import request
from .bigquery_utils import fetch_utilization_data, fetch_departments, fetch_users
from datetime import date, timedelta, datetime
import json
from collections import defaultdict
import numpy as np
import pandas as pd

def calculate_utilization(df, start_date_str, end_date_str, selected_department, selected_user):
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)

    # Calculate workable days between start_date and end_date
    workable_days = np.busday_count(start_date.date(), (end_date + pd.DateOffset(days=1)).date())

    # Filter data based on selected department and user
    df['Date_Worked'] = pd.to_datetime(df['Date_Worked'])

    filtered_data = df[(df['Date_Worked'] >= start_date) & (df['Date_Worked'] <= end_date)]
    
    if selected_department:
        filtered_data = filtered_data[filtered_data['User_Department'] == selected_department]

    if selected_user:
        filtered_data = filtered_data[filtered_data['User_Full_Name'] == selected_user]
    
    # Replace NaN values in photo_url column
    filtered_data['photo_url'].fillna('/static/assets/img/default_profile_photo.jpg', inplace=True)


     # Calculate billable hours
    filtered_data['Billable_Hours'] = np.where(filtered_data['Billable'] == 'Billable', filtered_data['Actual_Hours_Worked'], 0)

    # Group data by 'User_Full_Name' and calculate the total actual hours, total billable hours, and total time off hours
    grouped = filtered_data.groupby(['User_Full_Name', 'User_Department', 'Full_Time', 'Rate_Goal', 'photo_url']).agg(
        total_actual_hours=('Actual_Hours_Worked', 'sum'),
        total_billable_hours=('Billable_Hours', 'sum'),
        total_time_off_hours=('Actual_Hours_Worked', lambda x: x[filtered_data['Project_Type'] == 'zInternal: Time Off'].sum()),
    ).reset_index()
    
    # Calculate utilization rate
    grouped['eligible_hours'] = workable_days * 8 * grouped['Full_Time'] - grouped['total_time_off_hours']
    grouped['utilization_rate'] = grouped['total_billable_hours'] / grouped['eligible_hours']
    
    # Calculate working time
    grouped['working_time'] = grouped['total_actual_hours'] / (workable_days * 8 * grouped['Full_Time'])
    
    
    # Calculate non-billable hours
    non_billable_data = filtered_data[filtered_data['Billable'] == 'Non Billable']
    
    non_billable_grouped = non_billable_data.groupby('Project_Type').agg(
    total_non_billable_hours=('Actual_Hours_Worked', 'sum')
    ).reset_index()
    
    non_billable_grouped.columns = ['project_type', 'non_billable_time']

    return grouped, non_billable_grouped



def tadxp_utilization(start_date_str, end_date_str, selected_department, selected_user):
    

    # Fetch utilization data from BigQuery
    data = fetch_utilization_data(start_date_str, end_date_str)

    # Calculate utilization
    utilization_df = calculate_utilization(data, start_date_str, end_date_str, selected_department, selected_user)

    return utilization_df