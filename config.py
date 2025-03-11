import os
basedir = os.path.abspath(os.path.dirname(__file__))
 
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Some-random-secre-key-that-you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///"+os.path.join(basedir, 'app.db')
    AVATAR_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'images', 'avatars')
    IMAGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'images', 'items')