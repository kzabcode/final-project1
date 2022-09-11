from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nollnywg:j685PLsz2wNw1ta-qHYGG8GFjLPpJXpT@heffalump.db.elephantsql.com/nollnywg'

db = SQLAlchemy(app)

# class Quotes(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     quote = db.Column(db.String(500), nullable=False)
#     author = db.Column(db.String(50), nullable=False)
#     date_added = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return "<Author %r>" % self.author

class UserForm(FlaskForm):
    quote = StringField("Quote", validator=[DataRequired()])
    author = StringField("Author", validator=[DataRequired()])
    submit = SubmitField("Submit")


# @app.route('/quotes', methods=['GET', 'POST'])

# def add_quote():
#     return render_template('add_quote.html')

@app.route('/')

def index():
    first_name = "John"
    return render_template('index.html', first_name=first_name)

@app.route('/user/<name>')

def user(name):
    return render_template('user.html', user_name=name)

