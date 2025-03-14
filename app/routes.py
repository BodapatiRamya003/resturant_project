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
from app.models import User, Category,Item#,order, OrderItem, Table, RatingOrderItem

from app.forms import LoginForm,RegistrationForm,UpdateProfileForm, CategoryForm, DeleteCategoryForm, ItemForm#,DeleteItemForm,orderForm, orderItemForm, tableForm, ratingOrderForm

@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", title="Index")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("index"))
    return render_template("register.html", title="Register", form=form)

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
    
@app.route("/categories", methods=["GET", "POST"])
def categories():
    categories = db.session.scalars(sa.select(Category)).all()
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, varient=form.varient.data)
        db.session.add(category)
        db.session.commit()
        flash("Congratulations, you are now created category!")
        return redirect(url_for("categories"))
    return render_template("categories.html", title="category", form=form, categories=categories)

@app.route("/categories/<int:category_id>", methods=["GET", "POST"])
@login_required
def category(category_id):
    category = db.first_or_404(sa.select(Category).where(Category.id == category_id))
    items = db.session.scalars(sa.select(Item).where(Item.category_id == category_id)).all()
    form = ItemForm()

    if request.method=="POST" and not current_user.is_anonymous or current_user.is_admin:
        if form.validate_on_submit():
            item = Item(
                name=form.name.data,
                item_category=category,
                price=form.price.data,
                ingredient=form.ingredient.data,
                gst_percentage=form.gst_percentage.data
            )
            if form.image.data:
                file = form.image.data
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
                
                item.image =f'images/items/{filename}'
            db.session.add(item)
            db.session.commit()
            flash("Congratulations, you have created a new item!")
            return redirect(url_for("category", category_id=category_id))
    
    return render_template("category.html", form=form, category=category, items=items)

@app.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
def edit_category(category_id):
    if not current_user.is_admin:
        flash("Permission denied", "danger")
        return redirect(url_for("categories"))

    category = db.first_or_404(sa.select(Category).where(Category.id == category_id))
    form = CategoryForm(obj=category)
   
    if form.validate_on_submit():
        category.name = form.name.data
        category.varient = form.varient.data
        db.session.commit()
        flash("Category successfully updated")
        return redirect(url_for("category", category_id=category.id))
    return render_template("category_form.html", title="Edit Category", form=form)

@app.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        flash("Permission denied", "danger")
        return redirect(url_for("categories"))
    category = db.first_or_404(sa.select(Category).where(Category.id == category_id))

    if not category:
        flash("Unable to delete category")
        return redirect(url_for("categories"))
    db.session.delete(category)
    db.session.commit()
    flash("Category successfully deleted")
    return redirect(url_for("categories"))

@app.route("/categories/<int:category_id>/items/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(category_id, item_id):
    if current_user.is_anonymous or not current_user.is_admin:
        flash("Permission denied", "danger")
        return redirect(url_for("categories"))

    item = db.first_or_404(sa.select(Item).where(Item.id == item_id, Item.category_id == category_id))

    form = ItemForm()
    
    if request.method == "GET":
        form.name.data = item.name
        form.price.data = item.price
        form.ingredient.data = item.ingredient
        form.gst_percentage.data = item.gst_percentage
    
    if form.validate_on_submit():
        item.name=form.name.data
        item.price=form.price.data
        item.ingredient=form.ingredient.data
        item.gst_percentage=form.gst_percentage.data

        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
            item.image =f'images/items/{filename}'

        db.session.commit()
        flash("Category successfully updated")
        return redirect(url_for("category", category_id=category_id))
    else:
        print(form.errors)
    return render_template("item_form.html", title="Edit Item", form=form, item=item)

# @app.route("/order", methods=["GET", "POST"])
# def order():
#     form = OrderForm()
#     if form.validate_on_submit():
#         order = Order(user_id=form.user_id.data, timestamp=form.timestamp.data, status=form.status.data) 
#         db.session.add(order)
#         flash("Congratulations, you are now created order!")
#         return redirect(url_for("index"))
#     return render_template("order_form.html", title="order", form=form)

# @app.route("/orderitem", methods=["GET", "POST"])
# def orderitem():
#     form = orderItemForm()
#     if form.validate_on_submit():
#         order = OrderItem(order=form.order.data, item=form.timestamp.data, status=form.status.data) 
#         db.session.add(orderitem)
#         flash("Congratulations, you are now created orderitem!")
#         return redirect(url_for("index"))
#     return render_template("orderitem_form.html", title="orderitem", form=form)



# @app.route("/table", methods=["GET", "POST"])
# def table():
#     form = tableForm()
#     if form.validate_on_submit():
#         order = Table(seats=form.seats.data, price=form.price.data, available=form.available.data) 
#         db.session.add(table)
#         flash("Congratulations, you are now created table!")
#         return redirect(url_for("index"))
#     return render_template("table_form.html", title="table", form=form)


# @app.route("/ratingorderitem", methods=["GET", "POST"])
# def ratingorderitem():
#     form = ratingOrderForm()
#     if form.validate_on_submit():
#         order = RatingOrderItem(order_item=form.order_item.data, rating=form.rating.data, remark=form.remark.data, user=form.user.data) 
#         db.session.add(table)
#         flash("Congratulations, you are now created ratingorderitem!")
#         return redirect(url_for("index"))
#     return render_template("rating_form.html", title="ratingorderitem", form=form)


