from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import date, timedelta, datetime as dt
from my_application_package.bigquery_utils import get_timesheets_data, fetch_departments, fetch_users, fetch_nonbillable, fetch_utilization_data, fetch_billable
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
        {'name': 'Ten Adams', 'url': url_for('index')},
        {'name': 'Utilization', 'url': url_for('tenadams.utilization')}
    ]
    
    start_date_str = None
    end_date_str = None
    selected_department = None
    selected_user = None
    


    # Get department of the current user
    user_department = current_user.department if (hasattr(current_user, 'department') and current_user.department not in (None, '')) else None
    # print("User Department:", user_department)
    # assign a varible to user deparment to use in the template later 
    department_to_use = user_department

    
    # Fetch departments and users with optional filtering
    # Determine if the user is an admin
    is_admin = True if user_department is None else False

    # Fetch departments and users with optional filtering
    if is_admin:
        departments = fetch_departments()  # Fetch all departments for admin
    else:
        departments = fetch_departments(user_department)  # Fetch only user's department for non-admin

    users = fetch_users(user_department)
    
    # Handle form data on POST
    if request.method == 'POST':
        selected_department = request.form.get('department')
        if selected_department:
            department_to_use = selected_department
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        selected_department = request.form.get('department')
        selected_user = request.form.get('user')
        
        # Override user_department with the form input if provided
        if selected_department:
            user_department = selected_department

        # Fetch the departments again based on is_admin status (not user_department)
        if is_admin:
            departments = fetch_departments()
        else:
            departments = fetch_departments(user_department)

    # If start_date_str and end_date_str are not defined yet, set them to the last week's Monday and Sunday
    if not start_date_str or not end_date_str:
        today = date.today()       
        last_sunday = today - timedelta(days=today.weekday()+1)
        end_date = last_sunday
        start_date = last_sunday - timedelta(days=6)

        # Convert dates to strings in the desired format
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')

    # Call the tadxp_utilization function
    print(department_to_use)
    utilization_df, non_billable_df, billable_grouped_by_client, overall_utilization_rate = tadxp_utilization(start_date_str, end_date_str, department_to_use, selected_user)

    # Filter utilization_df by department
    if user_department:
        utilization_df = utilization_df[utilization_df['User_Department'] == user_department]

    # Calculate the total hours and total billable hours
    total_hours = utilization_df['total_actual_hours'].sum()
    total_billable = utilization_df['total_billable_hours'].sum()

    overall_utilization_rate_formatted = '{:.1f}%'.format(overall_utilization_rate * 100)
    
    # calculate the total working time for each employee
    working_time_df = utilization_df.sort_values(by='working_time', ascending=False)

    return render_template('tenadams/utilization.html', 
                           user_department=user_department,
                           departments=departments, 
                           users=users, 
                           utilization_df=utilization_df, 
                           start_date=start_date_str, 
                           end_date=end_date_str, 
                           selected_department=selected_department, 
                           selected_user=selected_user, 
                           total_hours=total_hours, 
                           total_billable=total_billable, 
                           overall_utilization_rate_formatted=overall_utilization_rate_formatted, 
                           working_time_df=working_time_df, 
                           non_billable_data=non_billable_df.to_json(orient='records'), 
                           billable_time=billable_grouped_by_client, 
                           breadcrumb=breadcrumb,
                           is_admin=is_admin)
#Utiliztion Route Department Only 
# Define the utilization route
@tenadams.route('/utilizationdept', methods=['GET', 'POST'])
@login_required
def utilizationdept():
    breadcrumb = [
        {'name': 'Ten Adams', 'url': url_for('index')},
        {'name': 'Utilization Department', 'url': url_for('tenadams.utilizationdept')}
    ]
    
    start_date_str = None
    end_date_str = None
    selected_department = None
    selected_user = None
    


    # Get department of the current user
    user_department = current_user.department if (hasattr(current_user, 'department') and current_user.department not in (None, '')) else None
    # print("User Department:", user_department)
    # assign a varible to user deparment to use in the template later 
    department_to_use = user_department

    
    # Fetch departments and users with optional filtering
    # Determine if the user is an admin
    is_admin = True if user_department is None else False

    # Fetch departments and users with optional filtering
    if is_admin:
        departments = fetch_departments()  # Fetch all departments for admin
    else:
        departments = fetch_departments(user_department)  # Fetch only user's department for non-admin

    users = fetch_users(user_department)
    
    # Handle form data on POST
    if request.method == 'POST':
        selected_department = request.form.get('department')
        if selected_department:
            department_to_use = selected_department
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        selected_department = request.form.get('department')
        selected_user = request.form.get('user')
        
        # Override user_department with the form input if provided
        if selected_department:
            user_department = selected_department

        # Fetch the departments again based on is_admin status (not user_department)
        if is_admin:
            departments = fetch_departments()
        else:
            departments = fetch_departments(user_department)

    # If start_date_str and end_date_str are not defined yet, set them to the last week's Monday and Sunday
    if not start_date_str or not end_date_str:
        today = date.today()       
        last_sunday = today - timedelta(days=today.weekday()+1)
        end_date = last_sunday
        start_date = last_sunday - timedelta(days=6)

        # Convert dates to strings in the desired format
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')

    # Call the tadxp_utilization function
    print(department_to_use)
    utilization_df, non_billable_df, billable_grouped_by_client, overall_utilization_rate = tadxp_utilization(start_date_str, end_date_str, department_to_use, selected_user)

    # Filter utilization_df by department
    if user_department:
        utilization_df = utilization_df[utilization_df['User_Department'] == user_department]

    # Calculate the total hours and total billable hours
    total_hours = utilization_df['total_actual_hours'].sum()
    total_billable = utilization_df['total_billable_hours'].sum()

    overall_utilization_rate_formatted = '{:.1f}%'.format(overall_utilization_rate * 100)
    
    # calculate the total working time for each employee
    working_time_df = utilization_df.sort_values(by='working_time', ascending=False)

    return render_template('tenadams/utilizationdept.html', 
                           user_department=user_department,
                           departments=departments, 
                           users=users, 
                           utilization_df=utilization_df, 
                           start_date=start_date_str, 
                           end_date=end_date_str, 
                           selected_department=selected_department, 
                           selected_user=selected_user, 
                           total_hours=total_hours, 
                           total_billable=total_billable, 
                           overall_utilization_rate_formatted=overall_utilization_rate_formatted, 
                           working_time_df=working_time_df, 
                           non_billable_data=non_billable_df.to_json(orient='records'), 
                           billable_time=billable_grouped_by_client, 
                           breadcrumb=breadcrumb,
                           is_admin=is_admin)

@tenadams.route('/timesheets', methods=['GET', 'POST'])
@login_required
def timesheets():
    breadcrumb = [
        {'name': 'Ten Adams', 'url': url_for('index')},
        {'name': 'Timesheets', 'url': url_for('tenadams.timesheets')}
    ]

    # Default to the user's department if available:
    user_department = current_user.department if (hasattr(current_user, 'department') and current_user.department not in (None, '')) else None

    # Use form values if provided, else default to the user's attributes or None:
    department = request.form.get('department', user_department)
    user = request.form.get('user', None)  # Assuming there's no user attribute in current_user for defaulting

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
        'photo_url': 'first'  # Use 'first' to get the first non-null value in the group
    }).reset_index()

    pivot_data = grouped_data.pivot_table(values='time_Entered_On_Time', index=['User_Full_Name', 'photo_url'], columns='week_start', fill_value=0)
    pivot_data.reset_index(inplace=True)
    
    # Extracting date columns and sorting them in reverse order
    date_columns = sorted(pivot_data.columns[2:], key=lambda x: pd.Timestamp(x), reverse=True)
    pivot_data = pivot_data[['User_Full_Name', 'photo_url'] + date_columns]

    pivot_data.columns = [col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col for col in pivot_data.columns]
    data = {
        row['User_Full_Name']: {
            'photo_url': row['photo_url'],
            'values': row[pivot_data.columns[2:]].to_dict()
        }
        for index, row in pivot_data.iterrows()
    }

    # fetch the departments and users
    departments = fetch_departments()
    users = fetch_users()

    first_key = next(iter(data.keys()))

    return render_template('tenadams/timesheets.html', 
                           data=data, 
                           first_key=first_key, 
                           departments=departments,
                           users=users, 
                           selected_department=department, 
                           breadcrumb=breadcrumb)

@tenadams.route('/nonbillable', methods=['GET', 'POST'])
@login_required

def nonbillable():
    breadcrumb = [
    {'name': 'Ten Adams', 'url': url_for('index')},
    {'name': 'Non-Billable', 'url': url_for('tenadams.nonbillable')}
    ]
    start_date_str = None
    end_date_str = None
    selected_department = None
    selected_user = None
    
    # Get department of the current user
    user_department = current_user.department if (hasattr(current_user, 'department') and current_user.department not in (None, '')) else None
    # print("User Department:", user_department)
    # assign a varible to user deparment to use in the template later 
    department_to_use = user_department

    
    # Fetch departments and users with optional filtering
    # Determine if the user is an admin
    is_admin = True if user_department is None else False

    # Fetch departments and users with optional filtering
    if is_admin:
        departments = fetch_departments()  # Fetch all departments for admin
    else:
        departments = fetch_departments(user_department)  # Fetch only user's department for non-admin

    users = fetch_users(user_department)

    # Handle form data on POST
    if request.method == 'POST':
        selected_department = request.form.get('department')
        if selected_department:
            department_to_use = selected_department
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        selected_department = request.form.get('department')
        selected_user = request.form.get('user')
        
        # Override user_department with the form input if provided
        if selected_department:
            user_department = selected_department

        # Fetch the departments again based on is_admin status (not user_department)
        if is_admin:
            departments = fetch_departments()
        else:
            departments = fetch_departments(user_department)
    
    # If start_date_str and end_date_str are not defined yet, set them to the last week's Monday and Sunday
    if not start_date_str or not end_date_str:
        today = date.today()       
        last_sunday = today - timedelta(days=today.weekday()+1)
        end_date = last_sunday
        start_date = last_sunday - timedelta(days=6)

        # Convert dates to strings in the desired format
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')
    
    data_type = request.form.get('data_type') if request.method == 'POST' else 'management_time'
    
    departments = fetch_departments(user_department=department_to_use)
    users = fetch_users(user_department=department_to_use)


    nonbill_df = fetch_nonbillable(start_date_str, end_date_str, department_to_use, selected_user, data_type)
    print(nonbill_df.columns)
    # Process data based on data_type
    if data_type == 'management_time':
        grouped_data = nonbill_df[nonbill_df['Project_Type'] == 'zInternal: Management'].groupby('task_Name').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    elif data_type == 'gen_admin':
        grouped_data = nonbill_df[nonbill_df['Project_Type'] == 'zInternal: Gen Admin'].groupby('task_Name').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    elif data_type == 'operations':
        grouped_data = nonbill_df[nonbill_df['Project_Type'] == 'zInternal: Operations'].groupby('task_Name').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    elif data_type == 'training':
        grouped_data = nonbill_df[nonbill_df['Project_Type'] == 'zInternal: Training'].groupby('task_Name').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    elif data_type == 'nbca':
        grouped_data = nonbill_df[nonbill_df['Project_Type'] == 'zNB Client Admin'].groupby('task_Name').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    elif data_type == 'internal_initiative':
        grouped_data = nonbill_df[nonbill_df['Project_Type'] == 'zInternal Initiative'].groupby('project_Name').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    elif data_type == 'opp_time':
        # Filter for 'zProposal/Opportunity' and where 'client' is not 'Ten Adams Business Development'
        internal_initiative_df = nonbill_df[(nonbill_df['Project_Type'] == 'zProposal/Opportunity') & 
                                            (nonbill_df['client'] != 'Ten Adams Business Development')]

        
       # Then include entries where 'project_Name' contains 'Opp' or 'Opportunity'
        # filtered_df = internal_initiative_df[
        # internal_initiative_df['project_Name'].str.contains('Opp', na=False) | 
        # internal_initiative_df['project_Name'].str.contains('Opportunity', na=False)]        
        filtered_df = internal_initiative_df
        # Proceed with aggregation on the filtered data
        grouped_data = filtered_df.groupby('project_Name').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    elif data_type == 'new_biz':
         # Filter for 'zProposal/Opportunity' and where 'client' is not 'Ten Adams Business Development'
        internal_initiative_df = nonbill_df[(nonbill_df['Project_Type'] == 'zProposal/Opportunity') & 
                                            (nonbill_df['client'] == 'Ten Adams Business Development')]
  # then exclude entries where 'project_Name' contains 'Opp' or 'Opportunity'
        # filtered_df = internal_initiative_df[
        # ~(internal_initiative_df['project_Name'].str.contains('Opp', na=False) | 
        #   internal_initiative_df['project_Name'].str.contains('Opportunity', na=False))]            
        filtered_df=internal_initiative_df    
        # Proceed with aggregation on the filtered data
        grouped_data = filtered_df.groupby('project_Name').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100


    return render_template('tenadams/nonbillable.html', 
                            user_department=user_department,
                            departments=departments,
                            users=users,  
                            start_date=start_date_str, 
                            end_date=end_date_str, 
                            grouped_data=grouped_data, 
                            selected_department=selected_department, 
                            data_type=data_type,
                            breadcrumb=breadcrumb,
                            is_admin=is_admin)
    
  


# Billable Hours Chart / Page / Route 
@tenadams.route('/billable', methods=['GET', 'POST'])
@login_required


def billable():

    breadcrumb = [
        {'name': 'Ten Adams', 'url': url_for('index')},
        {'name': 'Billable', 'url': url_for('tenadams.billable')}
        ]

    start_date_str = None
    end_date_str = None
    selected_department = None
    selected_user = None
    
    # Get department of the current user
    user_department = current_user.department if (hasattr(current_user, 'department') and current_user.department not in (None, '')) else None
    # print("User Department:", user_department)
    # assign a varible to user deparment to use in the template later 
    department_to_use = user_department
    
        # Fetch departments and users with optional filtering
    # Determine if the user is an admin
    is_admin = True if user_department is None else False

     # Fetch departments and users with optional filtering
    if is_admin:
        departments = fetch_departments()  # Fetch all departments for admin
    else:
        departments = fetch_departments(user_department)  # Fetch only user's department for non-admin

    users = fetch_users(user_department)

    # Handle form data on POST
    if request.method == 'POST':
        selected_department = request.form.get('department')
        if selected_department:
            department_to_use = selected_department
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        selected_department = request.form.get('department')
        selected_user = request.form.get('user')
        
        # Override user_department with the form input if provided
        if selected_department:
            user_department = selected_department

        # Fetch the departments again based on is_admin status (not user_department)
        if is_admin:
            departments = fetch_departments()
        else:
            departments = fetch_departments(user_department)
    
    # If start_date_str and end_date_str are not defined yet, set them to the last week's Monday and Sunday
    if not start_date_str or not end_date_str:
        today = date.today()       
        last_sunday = today - timedelta(days=today.weekday()+1)
        end_date = last_sunday
        start_date = last_sunday - timedelta(days=6)

        # Convert dates to strings in the desired format
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')
    
    data_type = request.form.get('data_type') if request.method == 'POST' else 'billable_service'
    
    departments = fetch_departments(user_department=department_to_use)
    users = fetch_users(user_department=department_to_use)


    bill_df = fetch_billable(start_date_str, end_date_str, department_to_use, selected_user)
    print(bill_df.columns)
    # Process data based on data_type
    if data_type == 'billable_service':
        grouped_data = bill_df.groupby('ServiceDescription').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    elif data_type == 'billable_projecttype':
        grouped_data = bill_df.groupby('Project_Type').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
        grouped_data = grouped_data.sort_values('Actual_Hours_Worked', ascending=False)
        total_hours = grouped_data['Actual_Hours_Worked'].sum()
        grouped_data['Percentage_of_Total'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100


    return render_template('tenadams/billable.html', 
                            user_department=user_department,
                            departments=departments,
                            users=users,  
                            start_date=start_date_str, 
                            end_date=end_date_str, 
                            grouped_data=grouped_data, 
                            selected_department=selected_department, 
                            data_type=data_type,
                            breadcrumb=breadcrumb,
                            is_admin=is_admin)

# this is the code for the Service Description Chart / Page
@tenadams.route('/service-description-chart', methods=['GET', 'POST'])
@login_required
def service_description_chart():
    start_date_str = None
    end_date_str = None
    selected_department = None
    selected_user = None
    
    # Get department of the current user
    user_department = current_user.department if (hasattr(current_user, 'department') and current_user.department not in (None, '')) else None

    # print("User Department:", user_department)
    
    # assign a varible to user deparment to use in the template later 
    department_to_use = user_department
    
    # Fetch departments and users with optional filtering
    # Determine if the user is an admin
    is_admin = True if user_department is None else False

    # Fetch departments and users with optional filtering
    if is_admin:
        departments = fetch_departments()  # Fetch all departments for admin
    else:
        departments = fetch_departments(user_department)  # Fetch only user's department for non-admin

    users = fetch_users(user_department)
    
    # Handle form data on POST
    if request.method == 'POST':
        selected_department = request.form.get('department')
        if selected_department:
            department_to_use = selected_department
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        selected_department = request.form.get('department')
        selected_user = request.form.get('user')
        
        # Override user_department with the form input if provided
        if selected_department:
            user_department = selected_department

        # Fetch the departments again based on is_admin status (not user_department)
        if is_admin:
            departments = fetch_departments()
        else:
            departments = fetch_departments(user_department)
        
    # If start_date_str and end_date_str are not defined yet, set them to the last week's Monday and Sunday
    if not start_date_str or not end_date_str:
        today = date.today()       
        last_sunday = today - timedelta(days=today.weekday()+1)
        end_date = last_sunday
        start_date = last_sunday - timedelta(days=6)

        # Convert dates to strings in the desired format
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')
    
    # Fetch data using the fetch_utilization_data function
    df = fetch_utilization_data(start_date_str, end_date_str, department_to_use)
    
    # Filter data by selected user if provided
    if selected_user:
        df = df[df['User_Full_Name'] == selected_user]
    
    # Group and aggregate data for pie chart
    grouped_data = df.groupby('ServiceDescription').agg({'Actual_Hours_Worked': 'sum'}).reset_index()
    
    # Compute percentages
    total_hours = grouped_data['Actual_Hours_Worked'].sum()
    grouped_data['Percentage'] = (grouped_data['Actual_Hours_Worked'] / total_hours) * 100
    
    # Sort by percentage in descending order
    grouped_data = grouped_data.sort_values(by='Percentage', ascending=False)


    return render_template('tenadams/servicecodes.html', 
                           departments=departments, 
                           grouped_data=grouped_data,
                           users=users, 
                           selected_department=selected_department, 
                           selected_user=selected_user,
                           start_date=start_date_str, 
                           end_date=end_date_str,
                           user_department=user_department,
                           is_admin=is_admin)    
