from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import datetime

from . import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    images = relationship("Images")


class Images(db.Model):
    __tablename__ = "images"
    imageId = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    imageName = db.Column(db.String(100))
    unitPrice = db.Column(db.Integer)
    inventory = db.Column(db.Integer)
    description = db.Column(db.String(1000))
    data = db.Column(db.LargeBinary)
    private = db.Column(db.Boolean)
    userId = db.Column(db.Integer, ForeignKey('user.id'))
    orders = relationship("Orders")


class Orders(db.Model):
    __tablename__ = "orders"
    orderId = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    orderDate = db.Column(db.Date, default=datetime.datetime.now)
    status = db.Column(db.String(100))
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    complete = db.Column(db.Boolean, default=False)
    imageId = db.Column(db.Integer, ForeignKey('images.imageId'))
    buyerId = db.Column(db.Integer, ForeignKey('user.id'))
    sellerId = db.Column(db.Integer, ForeignKey('user.id'))
    buyer = relationship("User", foreign_keys=[buyerId])
    seller = relationship("User", foreign_keys=[sellerId])




