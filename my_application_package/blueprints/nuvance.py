from flask import Blueprint, render_template, redirect, url_for


nuvance = Blueprint('nuvance', __name__)

# Define the root route for Ten Adams
@nuvance.route('/')
def nuvance_home():
    return redirect(url_for('index'))  # Redirect to main/welcome route

# Define the utilization route
@nuvance.route('/start')
def start():
    breadcrumb = [
        {'name': 'Welcome', 'url': url_for('index')},
        {'name': 'Start', 'url': url_for('nuvance.start')}
    ]
    return render_template('nuvance/start.html', breadcrumb=breadcrumb)