import sqlalchemy as sa
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from wtforms import (
    StringField, 
    PasswordField, 
    BooleanField, 
    SubmitField, 
    FileField
)

from app import db
from app.models import User



class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    phone = StringField("Phone", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data
        ))
        if user is not None:
            raise ValidationError("please use a different user name")

    def validate_email(self,email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data
            ))
        if user is not None:
                raise ValidationError("please use a different email address")
    def validate_phone(self,phone):
        user = db.session.scalar(sa.select(User).where(
            User.phone == phone.data
            ))
        if user is not None:
                raise ValidationError("please use a phone")
            
class UpdateProfileForm(FlaskForm):
    avatar = FileField('Upload Avatar',validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField("Register")
    submit = SubmitField("Update")

class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    varient = StringField("Varient", validators=[DataRequired()])
    submit = SubmitField("Category")

class DeleteCategoryForm(FlaskForm):
    submit = SubmitField("Delete")

# class ItemForm(FlaskForm):
#     name = StringField("Name", validators=[DataRequired()])
#     category = StringField("Category", validators=[DataRequired()])
#     image = FileField('Upload Image',validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
#     price = StringField("Price", validators=[DataRequired()])
#     ingredient = StringField("Ingredient", validators=[DataRequired()])
#     gst_percentage = StringField("GST Percentage", validators=[DataRequired()])
#     submit = SubmitField("Add Item")

# class OrderForm(FlaskForm):
#     user_id = StringField("User ID", validators=[DataRequired()])
#     timestamp = StringField("Timestamp", validators=[DataRequired()])
#     status = StringField("Status", validators=[DataRequired()])
#     submit = SubmitField("Order")

# class orderItemForm(FlaskForm):
#     order_id = StringField("Order ID", validators=[DataRequired()])
#     item = StringField("Item", validators=[DataRequired()])
#     quantity = StringField("Quantity", validators=[DataRequired()])
#     submit = SubmitField("Order Item")


# class tableForm(FlaskForm):
#     seats = StringField("Seats", validators=[DataRequired()])
#     price = StringField("Price", validators=[DataRequired()])
#     available = StringField("Available", validators=[DataRequired()])
#     submit = SubmitField("Table")

# class ratingOrderForm(FlaskForm):
#     order_item = StringField("Order Item", validators=[DataRequired()])
#     rating = StringField("Rating", validators=[DataRequired()])
#     remark = StringField("Remark", validators=[DataRequired()])
#     user = StringField("User", validators=[DataRequired()])
#     submit = SubmitField("Rating")    