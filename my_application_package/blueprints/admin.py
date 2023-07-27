from flask import flash, render_template, redirect, url_for, Blueprint
from flask_login import login_required, current_user
from my_application_package.models import User, Role, Client, MenuItem, db
from my_application_package.forms import UserForm, EditUserForm, RoleForm, MenuItemForm
from my_application_package.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/user/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    form = UserForm()
    breadcrumb = [
        {'name': 'Welcome', 'url': url_for('index')},
        {'name': 'Add User', 'url': url_for('admin.new_user')}
    ]

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
    return render_template('admin/new_user.html', form=form, form_type='new', breadcrumb=breadcrumb)


@admin_bp.route('/user', methods=['GET'])
@login_required
@admin_required
def user_list():
    breadcrumb = [
        {'name': 'Welcome', 'url': url_for('index')},
        {'name': 'User List', 'url': url_for('admin.user_list')}
    ]
    users = User.query.all()
    return render_template('admin/user_list.html', users=users, breadcrumb=breadcrumb)


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
    breadcrumb = [
        {'name': 'Welcome', 'url': url_for('index')},
        {'name': 'Edit User', 'url': url_for('admin.edit_user')}
    ]
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
    
    return render_template('admin/edit_user.html', form=form, user=user, form_type='edit', breadcrumb=breadcrumb)

# Views for managing roles
@admin_bp.route('/roles', methods=['GET'])
@login_required
@admin_required
def manage_roles():
    breadcrumb = [
        {'name': 'Welcome', 'url': url_for('index')},
        {'name': 'Manage Roles', 'url': url_for('admin.manage_roles')}
    ]
    roles = Role.query.all()
    return render_template('admin/manage_roles.html', roles=roles, breadcrumb=breadcrumb)



@admin_bp.route('/roles/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_role():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data)
        db.session.add(role)
        db.session.commit()
        flash('Role has been created.', 'success')
        return redirect(url_for('admin.manage_roles'))
    return render_template('admin/edit_role.html', form=form)

@admin_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        form.populate_obj(role)
        db.session.commit()
        flash('Role has been updated.', 'success')
        return redirect(url_for('admin.manage_roles'))
    return render_template('admin/edit_role.html', form=form, role=role)

@admin_bp.route('/roles/<int:role_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    flash('Role has been deleted.', 'success')
    return redirect(url_for('admin.manage_roles'))


# Views for managing menu items
@admin_bp.route('/menu_items', methods=['GET'])
@login_required
@admin_required
def manage_menu_items():
    menu_items = MenuItem.query.all()
    return render_template('admin/manage_menu_items.html', menu_items=menu_items)

@admin_bp.route('/menu_items/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_menu_item():
    form = MenuItemForm()

    if form.validate_on_submit():
        menu_item = MenuItem(
            label=form.label.data,
            target_url=form.target_url.data,
            icon_class=form.icon_class.data,
            parent_menu_item_id=form.parent_menu_item.data
        )
        db.session.add(menu_item)
        db.session.commit()
        flash('Menu item has been created.', 'success')
        return redirect(url_for('admin.manage_menu_items'))
     # Populate the choices for the parent menu item and roles fields
    form.parent_menu_item.choices = [(item.id, item.label) for item in MenuItem.query.all()]
    form.roles.choices = [(role.id, role.name) for role in Role.query.all()]


    return render_template('admin/edit_menu_item.html', form=form)


@admin_bp.route('/menu_items/<int:menu_item_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_menu_item(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    form = MenuItemForm(obj=menu_item)

    if form.validate_on_submit():
        form.populate_obj(menu_item)
        db.session.commit()
        flash('Menu item has been updated.', 'success')
        return redirect(url_for('admin.manage_menu_items'))
    
   # Populate the choices for the parent menu item and roles fields
    form.parent_menu_item.choices = [(item.id, item.label) for item in MenuItem.query.filter(MenuItem.id != menu_item.id).all()]
    form.roles.choices = [(role.id, role.name) for role in Role.query.all()]


    return render_template('admin/edit_menu_item.html', form=form, menu_item=menu_item)


@admin_bp.route('/menu_items/<int:menu_item_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_menu_item(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    db.session.delete(menu_item)
    db.session.commit()
    flash('Menu item has been deleted.', 'success')
    return redirect(url_for('admin.manage_menu_items'))