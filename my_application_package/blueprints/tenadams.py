from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import date, timedelta, datetime as dt
from my_application_package.bigquery_utils import get_timesheets_data, fetch_departments, fetch_users, fetch_nonbillable
from my_application_package.utilities import tadxp_utilization
import pandas as pd



# Create a blueprint
tenadams = Blueprint('tenadams', __name__)

# Define the root route for Ten Adams
@tenadams.route('/')
def ta_home():
    return redirect(url_for('index'))  # Redirect to main/welcome route

# Define the utilization route
@tenadams.route('/utilization', methods=['GET', 'POST'])
@login_required
def utilization():
    breadcrumb = [
        {'name': 'Welcome', 'url': url_for('index')},
        {'name': 'Utilization', 'url': url_for('tenadams.utilization')}
    ]
    start_date_str = None
    end_date_str = None
    selected_department = None
    selected_user = None

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        selected_department = request.form.get('department')
        selected_user = request.form.get('user')
    
    # If start_date_str and end_date_str are not defined yet, set them to the last week's Monday and Sunday
    if not start_date_str or not end_date_str:
        today = date.today()       
        last_sunday = today - timedelta(days=today.weekday()+1)
        end_date = last_sunday
        start_date = last_sunday - timedelta(days=6)

        # Convert dates to strings in the desired format
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')

    # Call the tadxp_utilization function with the start_date, end_date, selected_department, and selected_user
    utilization_df, non_billable_df = tadxp_utilization(start_date_str, end_date_str, selected_department, selected_user)
    # Calculate the total hours and total billable hours
    total_hours = utilization_df['total_actual_hours'].sum()
    total_billable = utilization_df['total_billable_hours'].sum()
    # Calculate the overall utilization rate
    overall_utilization_rate = total_billable / total_hours if total_hours != 0 else 0
    overall_utilization_rate_formatted = '{:.1f}%'.format(overall_utilization_rate * 100)
    # fetch the departments and users from BigQuery
    departments = fetch_departments()
    users = fetch_users()
    
    # calculate the total working time for each employee
    working_time_df = utilization_df.sort_values(by='working_time', ascending=False)



    return render_template('tenadams/utilization.html', departments=departments, users=users, utilization_df=utilization_df, start_date=start_date_str, end_date=end_date_str, selected_department=selected_department, selected_user=selected_user, total_hours=total_hours, total_billable=total_billable, overall_utilization_rate_formatted=overall_utilization_rate_formatted, working_time_df=working_time_df, non_billable_data=non_billable_df.to_json(orient='records'), breadcrumb=breadcrumb)

@tenadams.route('/timesheets', methods=['GET', 'POST'])
@login_required
def timesheets():
    department = request.form.get('department')
    user = request.form.get('user')

    data = get_timesheets_data()
    data['Date_Worked'] = pd.to_datetime(data['Date_Worked'])
    data['week_start'] = data['Date_Worked'].apply(lambda d: d - timedelta(days=d.weekday()))

    last_12_weeks_start = dt.combine(dt.today(), dt.min.time()) - timedelta(weeks=12)
    data = data[data['week_start'] >= last_12_weeks_start]

    if department:
        data = data[data['User_Department'] == department]
    if user:
        data = data[data['User_Full_Name'] == user]
        
    grouped_data = data.groupby(['User_Full_Name', 'week_start']).agg({
        'time_Entered_On_Time': lambda x: (x == 'YES').mean(),
        'photo_url': 'first'  # You can use 'first' to take the first non-null value in the group
    }).reset_index()
    print(grouped_data.columns)

    pivot_data = grouped_data.pivot_table(values='time_Entered_On_Time', index=['User_Full_Name', 'photo_url'], columns='week_start', fill_value=0)

    # Reset the index to make 'User_Full_Name' and 'photo_url' regular columns
    pivot_data.reset_index(inplace=True)
    
    # Extracting date columns and sorting them in reverse order
    date_columns = sorted(pivot_data.columns[2:], key=lambda x: pd.Timestamp(x), reverse=True)

    # Rearranging the dataframe with sorted date columns
    pivot_data = pivot_data[['User_Full_Name', 'photo_url'] + date_columns]



    pivot_data.columns = [col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col for col in pivot_data.columns]

    data = {
        row['User_Full_Name']: {
            'photo_url': row['photo_url'],
            'values': row[pivot_data.columns[2:]].to_dict()
        }
        for index, row in pivot_data.iterrows()
    }


    # fetch the departments and users from BigQuery
    departments = fetch_departments()
    users = fetch_users()
    
    first_key = next(iter(data.keys()))

    return render_template('tenadams/timesheets.html', data=data, first_key=first_key, departments=departments, users=users, selected_department=department)

@tenadams.route('/nonbillable', methods=['GET', 'POST'])
@login_required
def nonbillable():
    start_date_str = None
    end_date_str = None
    selected_department = None
    selected_user = None

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        selected_department = request.form.get('department')
        selected_user = request.form.get('user')
    
    # If start_date_str and end_date_str are not defined yet, set them to the last week's Monday and Sunday
    if not start_date_str or not end_date_str:
        today = date.today()       
        last_sunday = today - timedelta(days=today.weekday()+1)
        end_date = last_sunday
        start_date = last_sunday - timedelta(days=6)

        # Convert dates to strings in the desired format
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')
    nonbill_df = fetch_nonbillable(start_date_str, end_date_str, selected_department, selected_user)
    grouped_data = nonbill_df.groupby(['User_Full_Name', 'Project_Type']).agg({'Actual_Hours_Worked': 'sum'}).reset_index()
    # fetch the departments and users from BigQuery
    departments = fetch_departments()
    users = fetch_users()
    return render_template('nonbillable.html', start_date=start_date_str, end_date=end_date_str, departments=departments, users=users, grouped_data=grouped_data, selected_department=selected_department)
