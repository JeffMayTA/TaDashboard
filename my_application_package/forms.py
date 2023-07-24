from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from .models import Client, User, db, Role

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')  # Add this field
    submit = SubmitField('Log In')

def get_clients():
    return Client.query

class RegisterForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists.')

    def create_user(self):
        user = User(
            fname=self.fname.data,
            lname=self.lname.data,
            email=self.email.data,
            role='user'
        )
        user.set_password(self.password.data)
        db.session.add(user)
        db.session.commit()
        

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class UserForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    roles = QuerySelectMultipleField('Roles', query_factory=lambda: Role.query.all(), get_label='name')
    clients = QuerySelectMultipleField('Clients', query_factory=lambda: Client.query.all(), get_label='name')
    
class EditUserForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    roles = QuerySelectMultipleField('Roles', query_factory=lambda: Role.query.all(), get_label='name')
    clients = QuerySelectMultipleField('Clients', query_factory=lambda: Client.query.all(), get_label='name')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)

        def process_formdata_role(valuelist):
            if valuelist:
                self.roles.data = [Role.query.get(int(id_)) for id_ in valuelist]
            else:
                self.roles.data = []

        self.roles.process_formdata = process_formdata_role

        def process_formdata_client(valuelist):
            if valuelist:
                self.clients.data = [Client.query.get(int(id_)) for id_ in valuelist]
            else:
                self.clients.data = []

        self.clients.process_formdata = process_formdata_client
