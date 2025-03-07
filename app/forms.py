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

class UpdateProfileForm(FlaskForm):
    avatar = FileField('Upload Avatar',validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField("Register")
    submit = SubmitField("Update")

