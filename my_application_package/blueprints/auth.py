from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, get_flashed_messages
from flask_login import login_user, logout_user, current_user
from my_application_package.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm 
from my_application_package.models import User
from my_application_package.dictionaries import quotes_and_authors, hellos
from my_application_package.app_factory import db, mail
from functools import wraps
from flask import abort
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask_mail import Message
import random


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    random_quote_author = random.choice(quotes_and_authors)
    quote = random_quote_author["quote"]
    author = random_quote_author["author"]
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)  # Use the 'remember_me' field here
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form, quote=quote, author=author)



@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, active_client_id=form.client.data.id, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/logout', methods=['POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out.', 'success')
    return redirect(url_for('index'))  # or wherever you want to redirect after logout


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    user_exists = True  # Initialize as True

    if form.validate_on_submit():
        print('Form validation successful.')  # Add this line for debugging
        user = User.query.filter_by(email=form.email.data).first()
        print(f"User: {user}")  # Add this line for debugging

        if user:
            # Generate a token for password reset
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps(user.email, salt='password-reset')
            
            # Import 'mail' here to avoid circular import
            from my_application_package.app_factory import mail

            # Send the password reset email with the tokenized link
            password_reset_link = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user.email, password_reset_link)

            flash('A password reset email has been sent to your email address.', 'success')
            return redirect(url_for('auth.login'))
        else:
            user_exists = False

    return render_template('auth/forgot_password.html', form=form, user_exists=user_exists)



@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)  # Set a max_age for token validity (1 hour in this case)
    except BadSignature:
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('No account with that email address exists.', 'danger')
        return redirect(url_for('auth.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Reset the user's password and save it to the database
        user.set_password(form.password.data)
        db.session.commit()

        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)



def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def send_password_reset_email(email, password_reset_link):
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'Please click on the following link to reset your password: {password_reset_link}'
    mail.send(msg)