import os
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from hashlib import md5
import pydenticon, hashlib, base64
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login

class User(UserMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    phone: so.Mapped[int] = so.mapped_column(unique=True)
    avatar: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    is_admin: so.Mapped[bool] = so.mapped_column(default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def gen_avatar(self, size=36, write_png=True):
        foreground = [ 
            "rgb(45,79,255)",
            "rgb(254,180,44)",
            "rgb(226,121,234)",
            "rgb(30,179,253)",
            "rgb(232,77,65)",
            "rgb(49,203,115)",
            "rgb(141,69,170)"
        ]
        background = "rgb(256,256,256)"

        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        basedir = os.path.abspath(os.path.dirname(__file__))
        pngloc = os.path.join(basedir, 'usercontent', 'identicon', str(digest) + '.png')
        icongen = pydenticon.Generator(5, 5, digest=hashlib.md5, foreground=foreground, background=background)
        pngicon = icongen.generate(self.email, size, size, padding=(8, 8, 8, 8), inverted=False, output_format="png")
        if write_png:
            pngfile = open(pngloc, "wb")
            pngfile.write(pngicon)
            pngfile.close()
        else:
            return str(base64.b64encode(pngicon))[2:-1]
    def __repr__(self):
        return '<User {}>'.format(self.username)


class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), index=True)
    varient: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))

    def __repr__(self):
        return '<Category {}>'.format(self.name)

# class Item(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, index=True)
#     category: so.Mapped[str] = so.mapped_column(sa.String(50), index=True)
#     image: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
#     price: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
#     ingredient: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
#     gst_percentage: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)
    
#     def __repr__(self):
#         return '<Item {}>'.formate(self.name)

# class Order(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
#     timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
#     status: so.Mapped[str] = so.mapped_column(sa.String(32), index=True)

#     def __repr__(self):
#         return '<Order {}>'.formate(self.user_id)

# class OrderItem(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     order_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Order.id), index=True)
#     item:  so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
#     quantity: so.Mapped[int] = so.mapped_column(sa.Integer, default=1)

#     def __repr__(self):
#         return '<OrderItem {}>'.formate(self.order_id)
    
# class Table(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     seats: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
#     price: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
#     available: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)

#     def __repr__(self):
#         return '<table {}>'.formate(self.seats)  

# class RatingOrderItem(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     order_item_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(OrderItem.id), index=True)
#     user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), index=True)
#     rating: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)  
#     remark: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))

#     def __repr__(self):
#         return '<ratingorderitem {}>'.formate(self.order_item_id)  
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
