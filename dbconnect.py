from flask import Flask, request, redirect, jsonify, render_template	
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
    	self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
    	return pwd_context.verify(password, self.password_hash)

# Create database
db.create_all()

@app.route('/api/users', methods = ['POST'])
def new_user():
	username = request.json.get('username')
	password = request.json.get('password')

	if username is None or password is None:
		abort(400) # missing arguments
	if User.query.filter_by(username = username).first() is not None:
		abort(400) # existing user

	user = User (username = username)
	user.hash_password(password)
	db.session.add(user)
	db.session.commit()

	return jsonify({'username' : user.username}), 201



@app.route('/')
def index():
	user_agent = request.headers.get('User-Agent')
	return '<p>Your browser is %s</p>' % user_agent

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 5001)