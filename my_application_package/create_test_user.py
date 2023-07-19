from my_application_package.app_factory import create_app
from my_application_package.models import db, User, Client
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()


    # Create a new client (if necessary)
    client = Client(name='Client1', description='First client')
    db.session.add(client)
    db.session.commit()

    # Create a new user
    user = User(fname='Test',lname='User', email='test@example.com', role='admin')
    user.password_hash = generate_password_hash('testpassword')
    user.active_client_id = client.id  # replace with actual client id
    db.session.add(user)
    db.session.commit()
