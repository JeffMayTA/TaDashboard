from flask import Blueprint, render_template, redirect, url_for



# Create a blueprint
tenadams = Blueprint('tenadams', __name__)

# Define the root route for Ten Adams
@tenadams.route('/')
def ta_home():
    return redirect(url_for('index'))  # Redirect to main/welcome route

# Define the utilization route
@tenadams.route('/utilization')
def utilization():
    breadcrumb = [
        {'name': 'Welcome', 'url': url_for('index')},
        {'name': 'Utilization', 'url': url_for('tenadams.utilization')}
    ]
    return render_template('tenadams/utilization.html', breadcrumb=breadcrumb)