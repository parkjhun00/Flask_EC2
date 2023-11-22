from datetime import datetime
from ..database import db

class Stocks(db.Model):

    __tablename__ = 'Stocks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

class Sales(db.Model):

    __tablename__ = 'Sales'

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=True)
    income = db.Column(db.Float, nullable=True)
