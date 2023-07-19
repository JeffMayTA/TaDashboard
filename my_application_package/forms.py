from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from .models import Client, User, db

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
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
