from my_application_package import create_app
from my_application_package.models import db


app=create_app()

# Init SQLAlchemy with the current app
db.init_app(app)

def seed_db():
    from my_application_package.models import User, Role, user_roles

    # Ensure app context for the session
    with app.app_context():
        # Drop all the data before seeding
        db.session.query(user_roles).delete()
        db.session.query(Role).delete()
        db.session.query(User).delete()

        # Add data to tables
        # add roles
        admin_role = Role(name='Admin')
        editor_role = Role(name='Editor')
        general_role = Role(name='General')

        db.session.add(admin_role)
        db.session.add(editor_role)
        db.session.add(general_role)
        db.session.flush()

        # add users
        jeff_user = User(email='jeff@tenadams.com', password='password', first_name='Jeff', last_name='Workman')
        joe_user = User(email='joe@tenadams.com', password='password', first_name='Joe', last_name='Nelson')
        cory_user = User(email='cory@tenadams.com', password='password', first_name='Cory', last_name='Clouser')

        db.session.add(jeff_user)
        db.session.add(joe_user)
        db.session.add(cory_user)
        db.session.flush()

        # add user roles
        jeff_user.roles.append(admin_role)
        joe_user.roles.append(editor_role)
        cory_user.roles.append(general_role)

        db.session.commit()
        print("Data committed to the database.")

if __name__ == "__main__":
    print("App context:", app.app_context())
    seed_db()
