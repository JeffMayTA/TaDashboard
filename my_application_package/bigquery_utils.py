from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import logging
import os


# Use the path from the environment variable
keyfile_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
# Use application default credentials to authenticate with BigQuery
# Define the credentials and client objects globally
# credentials = service_account.Credentials.from_service_account_file('/home/JeffMayTA/dashboardapp/secrets/timesheet-data-290519-fa3c335c5b29.json')
# credentials = service_account.Credentials.from_service_account_file('/home/JeffMayTA/dashboardapp/secrets/timesheet-data-290519-fa3c335c5b29.json')
credentials = service_account.Credentials.from_service_account_file(keyfile_path)
client = bigquery.Client(credentials=credentials, project='timesheet-data-290519')


def fetch_utilization_data(start_date, end_date):
    try:
        query = f"""
            SELECT
                Digital_Utilization.User_Department,
                Digital_Utilization.User_Full_Name,
                Digital_Utilization.Date_Worked,
                Digital_Utilization.Actual_Hours_Worked,
                Digital_Utilization.Billable,
                Digital_Utilization.Project_Type,
                employee.Rate_Goal,
                employee.Full_Time
            FROM
                `timesheet-data-290519.Utilization.Digital-Utilization` AS Digital_Utilization
            JOIN
                `timesheet-data-290519.Utilization.Employee-Data` employee
            ON
                Digital_Utilization.User_Full_Name = employee.User_Full_Name
            WHERE
                Date_Worked BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY
                Digital_Utilization.User_Full_Name;
            """

        # df = pd.read_gbq(query, project_id="timesheet-data-290519", credentials=credentials)
        df = pd.read_gbq(query, project_id="timesheet-data-290519")
        # print(df)
        return df
    except Exception as e:
        logging.error(f"Error in fetch_utilization_data: {e}")
        logging.error(f"Input values: param1={start_date}, param2={end_date}")
        raise


def fetch_departments():
    query = """
    SELECT DISTINCT User_Department
    FROM `timesheet-data-290519.Utilization.Digital-Utilization`
    ORDER BY User_Department;
    """
    df_departments = pd.read_gbq(query, project_id="timesheet-data-290519")
    departments_list = df_departments['User_Department'].tolist()
    return departments_list

def fetch_users():
    query = """
    SELECT DISTINCT User_Full_Name, User_Department
    FROM `timesheet-data-290519.Utilization.Digital-Utilization`
    ORDER BY User_Full_Name;
    """
    df_users = pd.read_gbq(query, project_id="timesheet-data-290519")
    users_list = df_users.to_dict('records')
    return users_list


def get_timesheets_data():
    try:
        query = f"""
            SELECT
                User_Full_Name,
                User_Department,
                Date_Worked,
                time_Entered_On_Time
            FROM
                `timesheet-data-290519.Utilization.Digital-Utilization`
            ORDER BY
                User_Full_Name;
            """

        df = pd.read_gbq(query, project_id="timesheet-data-290519")
        return df
    except Exception as e:
        logging.error(f"Error in get_timesheets_data: {e}")
        raise


def fetch_nonbillable(start_date_str, end_date_str, selected_department=None, selected_user=None):
    # Your existing code to define the SQL query

    department_filter = f"AND Digital_Utilization.User_Department = '{selected_department}'" if selected_department else ""
    user_filter = f"AND Digital_Utilization.User_Full_Name = '{selected_user}'" if selected_user else ""
    try:
        query = f"""
            SELECT
                Digital_Utilization.User_Department,
                Digital_Utilization.User_Full_Name,
                Digital_Utilization.Date_Worked,
                Digital_Utilization.Actual_Hours_Worked,
                Digital_Utilization.Billable,
                Digital_Utilization.Project_Type,
                employee.Rate_Goal,
                employee.Full_Time
            FROM
                `timesheet-data-290519.Utilization.Digital-Utilization` AS Digital_Utilization
            JOIN
                `timesheet-data-290519.Utilization.Employee-Data` employee
            ON
                Digital_Utilization.User_Full_Name = employee.User_Full_Name
            WHERE
                Date_Worked BETWEEN '{start_date_str}' AND '{end_date_str}'
                {department_filter}
                {user_filter}
            ORDER BY
                Digital_Utilization.User_Full_Name;
            """

        nonbill_df = pd.read_gbq(query, project_id="timesheet-data-290519")
        return nonbill_df
    except Exception as e:
            logging.error(f"Error in fetch_utilization_data: {e}")
            logging.error(f"Input values: param1={start_date_str}, param2={end_date_str}")
            raise

