from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import date, timedelta
from my_application_package.bigquery_utils import get_timesheets_data, fetch_departments, fetch_users, fetch_nonbillable
from my_application_package.utilities import tadxp_utilization


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

