from flask import flash, render_template, redirect, url_for, Blueprint
from flask_login import login_required, current_user
from my_application_package.models import User, Role, Client, MenuItem, db
from my_application_package.forms import UserForm, EditUserForm
from my_application_package.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/user/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    form = UserForm()

    if form.validate_on_submit():
        user = User(
            fname=form.fname.data,
            lname=form.lname.data,
            email=form.email.data,
            roles=form.roles.data,   # correct field name
            clients=form.clients.data  # correct field name
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User has been created.', 'success')
        return redirect(url_for('admin.user_list'))
    return render_template('admin/new_user.html', form=form, form_type='new')


@admin_bp.route('/user', methods=['GET'])
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)


@admin_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('admin/profile.html', user=current_user)


@admin_bp.route('/user/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted.', 'success')
    return redirect(url_for('admin.user_list'))

@admin_bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get(id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.user_list'))

    roles = Role.query.all()
    clients = Client.query.all()

    form = EditUserForm(obj=user)
    form.roles.choices = [(role.id, role.name) for role in roles]
    form.clients.choices = [(client.id, client.name) for client in clients]

    if form.validate_on_submit():
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.email = form.email.data
        user.roles = form.roles.data
        user.clients = form.clients.data
        db.session.commit()
        flash('User has been updated.', 'success')
        return redirect(url_for('admin.user_list'))
    else:
        print(form.errors)
    
    return render_template('admin/edit_user.html', form=form, user=user, form_type='edit')

