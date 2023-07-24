from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

role_menu_items = db.Table('role_menu_items',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('menu_item_id', db.Integer, db.ForeignKey('menu_item.id'), primary_key=True)
)

user_clients = db.Table('user_clients',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))
    profile_photo_url = db.Column(db.String(200))
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    clients = db.relationship('Client', secondary=user_clients, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))

class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    menu_items = db.relationship('MenuItem', secondary=role_menu_items, backref=db.backref('roles', lazy='dynamic'))

class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100))
    target_url = db.Column(db.String(100))
    parent_menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    parent_menu_item = db.relationship('MenuItem', remote_side=[id])

    client = db.relationship('Client', backref='menu_items', foreign_keys=[client_id])
