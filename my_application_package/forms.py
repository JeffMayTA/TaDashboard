from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, URL
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from .models import Client, User, db, Role, MenuItem

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
    department = SelectField('Department', choices=[('', 'None'), ('Creative', 'Creative'), ('Client Services/Strategy', 'Client Services/Strategy'), ('Project Management', 'Project Management'), ('Digital', 'Digital'), ('Media', 'Media'), ('Level Ten', 'Level Ten'), ('Business Development', 'Business Development')])
    clients = QuerySelectMultipleField('Clients', query_factory=lambda: Client.query.all(), get_label='name')
    
class EditUserForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    roles = QuerySelectMultipleField('Roles', query_factory=lambda: Role.query.all(), get_label='name')
    clients = QuerySelectMultipleField('Clients', query_factory=lambda: Client.query.all(), get_label='name')
    department = SelectField('Department', choices=[('', 'None'), ('Creative', 'Creative'), ('Client Services/Strategy', 'Client Services/Strategy'), ('Project Management', 'Project Management'), ('Digital', 'Digital'), ('Media', 'Media'), ('Level Ten', 'Level Ten'), ('Business Development', 'Business Development')])


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

class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired()])
    # Add other fields as needed
    submit = SubmitField('Save')

class MenuItemForm(FlaskForm):
    label = StringField('Label', validators=[DataRequired()])
    target_url = StringField('Target URL')
    icon_class = StringField('Icon Class')

    # Include the parent_menu_item field as a SelectField
    # Use coerce=int to ensure the selected value is stored as an integer
    parent_menu_item = SelectField('Parent Menu Item', coerce=int, choices=[(0, 'None')], default=0)
       # New multi-select field for selecting roles
    roles = QuerySelectMultipleField('Roles', query_factory=lambda: Role.query, get_label='name')
    client = QuerySelectField('Client', query_factory=lambda: Client.query.all(),
                              get_label='name', allow_blank=True)




    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(MenuItemForm, self).__init__(*args, **kwargs)

        # Populate the choices for the parent menu item field, including the current menu item
        self.parent_menu_item.choices.extend(
            [(item.id, item.label) for item in MenuItem.query.all()]
        )