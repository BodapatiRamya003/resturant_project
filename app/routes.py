import os
from app import app
import sqlalchemy as sa
from flask import request
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app import app
from app.models import User
from app.forms import LoginForm,RegistrationForm,UpdateProfileForm

@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", title="Index")

@app.route("/register", methods=["GET", "POST"])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("index"))
    return render_template("register.html", title="Register", form=form)

@app.route('/upload', methods=['GET', 'POST'])


@app.route("/login",  methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user.html', user=user)

@app.route("/user/<username>/edit", methods=["GET", "POST"])
def profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    if user != current_user and not current_user.is_admin:
        if current_user.is_anonymous or user != current_user and not current_user.is_admin:

         flash('You do not have permission to edit this profile.', 'danger')
        return redirect(url_for('index'))

    form = UpdateProfileForm()

    if request.method == "GET":
        form.phone.data = user.phone

    if form.validate_on_submit():
        user.phone = form.phone.data

        if form.avatar.data:
            avatar = form.avatar.data  # This is the file object
            filename = secure_filename(avatar.filename)  # Get the filename
            avatar_path = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
            avatar.save(avatar_path)
            user.avatar = f'images/avatars/{filename}'

            # Update the user's avatar URL in the database
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('user', username=user.username))
    
    return render_template('profile.html', form=form, user=user)
    