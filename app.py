from tokenize import String
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from config import Config
from forms import LoginForm, PostForm, UserForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "super secret"
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
            raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
            return check_password_hash(self.password_hash, password)

    def __repr__(self):
            return "<Name %r>" % self.name


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesful!!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        db.session.commit()
        flash("User Updated Successfully!")
        return render_template("dashboard.html", 
            form=form, 
            name_to_update = name_to_update)		
   
    else:
        return render_template("dashboard.html", 
                form=form,
                name_to_update = name_to_update,
                id = id)

    return render_template('dashboard.html')


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User added Successfully!")

    our_users = Users.query.order_by(Users.date_added)         
    return render_template('add_user.html', 
        form=form,
        name=name,
        our_users=our_users)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template(
                "update.html", 
                form=form, 
                name_to_update=name_to_update
                )
        except:
            flash("Error! Try Again...")
            return render_template(
                "update.html", 
                form=form, 
                name_to_update=name_to_update
                )
    else:
        return render_template(
            "update.html", 
            form=form, 
            name_to_update=name_to_update
            )


@app.route('/delete/<int:id>')
def delete(id):
    name = None
    form = UserForm()
    user_to_delete = Users.query.get(id)
    

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted!")

        our_users = Users.query.order_by(Users.date_added)         
        return render_template('add_user.html', 
        form=form,
        name=name,
        our_users=our_users)

    except:
        flash("Error, Try Again...")
        return render_template('add_user.html', 
        form=form,
        name=name,
        our_users=our_users)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(content=form.content.data, author=form.author.data, poster_id=poster)
        form.content.data = ''
        form.author.data = ''

        db.session.add(post)
        db.session.commit()

        flash("Quote Submitted Successfully!")

    return render_template("add_post.html", form=form)


@app.route('/posts')
@login_required
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']		

    
    else:
        return render_template("posts.html", 
                form=form,
                name_to_update = name_to_update,
                id = id, posts=posts)

    return render_template('dashboard.html')

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.author = form.author.data
        post.content = form.content.data
        
        db.session.add(post)
        db.session.commit()
        flash("Quote Has Been Updated!")
        return redirect(url_for('posts'))
    
    form.author.data = post.author
    form.content.data = post.content
    return render_template('edit_post.html', form=form)


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    db.session.delete(post_to_delete)
    db.session.commit()
    flash("Quote Was Deleted!")

    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)
