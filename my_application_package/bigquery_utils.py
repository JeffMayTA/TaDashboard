from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import logging
import os

def create_bigquery_client():
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):  # local environment
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        )
        project = 'timesheet-data-290519'
    else:  # App Engine
        credentials = None
        project = 'timesheet-data-290519'
    return credentials, project


def fetch_utilization_data(start_date, end_date, department=None):
    try:
        credentials, project = create_bigquery_client()
        department_filter = f"AND Digital_Utilization.User_Department = '{department}'" if department else ""


        query = f"""
            SELECT
                Digital_Utilization.User_Department,
                Digital_Utilization.User_Full_Name,
                Digital_Utilization.Date_Worked,
                Digital_Utilization.Actual_Hours_Worked,
                Digital_Utilization.Billable,
                Digital_Utilization.Project_Type,
                Digital_Utilization.client,
                Digital_Utilization.ServiceDescription,
                employee.Rate_Goal,
                employee.Full_Time,
                employee.photo_url

            FROM
                `timesheet-data-290519.Utilization.Digital-Utilization` AS Digital_Utilization
            JOIN
                `timesheet-data-290519.Utilization.Employee-Data` employee
            ON
                Digital_Utilization.User_Full_Name = employee.User_Full_Name
            WHERE
               Date_Worked BETWEEN '{start_date}' AND '{end_date}'
               {department_filter}
            ORDER BY
                Digital_Utilization.User_Full_Name;
            """
          
        df = pd.read_gbq(query, project_id=project, credentials=credentials)
        return df
    except Exception as e:
        logging.error(f"Error in fetch_utilization_data: {e}")
        logging.error(f"Input values: param1={start_date}, param2={end_date}")
        raise

def fetch_departments(user_department=None):
    credentials, project = create_bigquery_client()

    if user_department:
        query = f"""
        SELECT DISTINCT User_Department
        FROM `timesheet-data-290519.Utilization.Digital-Utilization`
        WHERE User_Department = '{user_department}'
        ORDER BY User_Department;
        """
    else:
        query = """
        SELECT DISTINCT User_Department
        FROM `timesheet-data-290519.Utilization.Digital-Utilization`
        ORDER BY User_Department;
        """
    df_departments = pd.read_gbq(query, project_id=project, credentials=credentials)
    departments_list = df_departments['User_Department'].tolist()
    return departments_list

def fetch_users(user_department=None):
    credentials, project = create_bigquery_client()

    if user_department:
        query = f"""
        SELECT DISTINCT User_Full_Name, User_Department
        FROM `timesheet-data-290519.Utilization.Digital-Utilization`
        WHERE User_Department = '{user_department}'
        ORDER BY User_Full_Name;
        """
    else:
        query = """
        SELECT DISTINCT User_Full_Name, User_Department
        FROM `timesheet-data-290519.Utilization.Digital-Utilization`
        ORDER BY User_Full_Name;
        """
    df_users = pd.read_gbq(query, project_id=project, credentials=credentials)
    users_list = df_users.to_dict('records')
    return users_list

def get_timesheets_data():
    try:
        credentials, project = create_bigquery_client()

        query = f"""
            SELECT
                Digital_Utilization.User_Full_Name,
                Digital_Utilization.User_Department,
                Digital_Utilization.Date_Worked,
                Digital_Utilization.time_Entered_On_Time,
                employee.photo_url
            FROM
                `timesheet-data-290519.Utilization.Digital-Utilization` AS Digital_Utilization
            JOIN
                `timesheet-data-290519.Utilization.Employee-Data` employee
            ON
                Digital_Utilization.User_Full_Name = employee.User_Full_Name
            ORDER BY
                Digital_Utilization.User_Full_Name;
            """

        df = pd.read_gbq(query, project_id=project, credentials=credentials)

        # Replace NaN values in photo_url column
        df['photo_url'].fillna('/static/assets/img/default_profile_photo.jpg', inplace=True)
        return df
    except Exception as e:
        logging.error(f"Error in get_timesheets_data: {e}")
        raise

def fetch_billable(start_date_str, end_date_str, department=None, selected_user=None):
    credentials, project = create_bigquery_client()
    department_filter = f"AND Digital_Utilization.User_Department = '{department}'" if department else ""
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
                Digital_Utilization.client,
                Digital_Utilization.project_Name,
                Digital_Utilization.ServiceDescription,
                Digital_Utilization.task_Name,
            FROM
                `timesheet-data-290519.Utilization.Digital-Utilization` AS Digital_Utilization
            JOIN
                `timesheet-data-290519.Utilization.Employee-Data` employee
            ON
                Digital_Utilization.User_Full_Name = employee.User_Full_Name
            WHERE
                Date_Worked BETWEEN '{start_date_str}' AND '{end_date_str}'
                AND Digital_Utilization.Billable = 'Billable' 
                {department_filter}
                {user_filter}
            ORDER BY
                Digital_Utilization.User_Full_Name;
            """
        nonbill_df = pd.read_gbq(query, project_id=project, credentials=credentials)
        return nonbill_df
    except Exception as e:
            logging.error(f"Error in fetch_utilization_data: {e}")
            logging.error(f"Input values: param1={start_date_str}, param2={end_date_str}")
            raise


def fetch_nonbillable(start_date_str, end_date_str, department=None, selected_user=None, data_type=None):
    credentials, project = create_bigquery_client()
    department_filter = f"AND Digital_Utilization.User_Department = '{department}'" if department else ""
    user_filter = f"AND Digital_Utilization.User_Full_Name = '{selected_user}'" if selected_user else ""

    # Additional filter or selection based on data_type
    data_type_filter = ""
    if data_type == 'management_time':
        data_type_filter = "AND Digital_Utilization.Project_Type = 'zInternal: Management'"
    elif data_type == 'gen_admin':
        data_type_filter = "AND Digital_Utilization.Project_Type = 'zInternal: Gen Admin'"
    elif data_type == 'operations':
        data_type_filter = "AND Digital_Utilization.Project_Type = 'zInternal: Operations'"
    elif data_type == 'training':
        data_type_filter = "AND Digital_Utilization.Project_Type = 'zInternal: Training'"
    elif data_type == 'nbca':
        data_type_filter = "AND Digital_Utilization.Project_Type = 'zInternal: NBCA'"
    elif data_type == 'internal_initiative':
        data_type_filter = "AND Digital_Utilization.Project_Type = 'zInternal: Internal Initiative'"

        # Here you can add more columns or conditions specific to 'management time'

    try:
        query = f"""
            SELECT
                Digital_Utilization.User_Department,
                Digital_Utilization.User_Full_Name,
                Digital_Utilization.Date_Worked,
                Digital_Utilization.Actual_Hours_Worked,
                Digital_Utilization.Billable,
                Digital_Utilization.Project_Type,
                Digital_Utilization.client,
                Digital_Utilization.project_Name,
                Digital_Utilization.ServiceDescription,
                Digital_Utilization.task_Name,
            FROM
                `timesheet-data-290519.Utilization.Digital-Utilization` AS Digital_Utilization
            JOIN
                `timesheet-data-290519.Utilization.Employee-Data` employee
            ON
                Digital_Utilization.User_Full_Name = employee.User_Full_Name
            WHERE
                Date_Worked BETWEEN '{start_date_str}' AND '{end_date_str}'
                AND Digital_Utilization.Billable = 'Non Billable' 
                {department_filter}
                {user_filter}
                {data_type_filter}
            ORDER BY
                Digital_Utilization.User_Full_Name;
            """
        nonbill_df = pd.read_gbq(query, project_id=project, credentials=credentials)
        return nonbill_df
    except Exception as e:
            logging.error(f"Error in fetch_utilization_data: {e}")
            logging.error(f"Input values: param1={start_date_str}, param2={end_date_str}")
            raise
