from blog_app import db, login_manager
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, ForeignKey, Column
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=True)
    role = db.Column(db.String, default='user', nullable=True)
    posts = db.relationship('Post', backref='user')
    comments = db.relationship('Comment', backref='user')
    likes = db.relationship('Like', backref='user')
    sugesstion = db.relationship('Suggesstion', backref='user')
    reports = db.relationship('Reported', backref="user")

    def __repr__(self):
        return f'{self.username} {self.email} {self.password} {self.admin}'


class Post(db.Model,Base):
    post_id = db.Column(db.Integer, primary_key=True)
    attachement = Column(String(1000), nullable=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    approved = Column(db.Boolean, default=False,nullable=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    suggesstion = db.relationship('Suggesstion', backref='post',cascade="all, delete-orphan")
    reports = db.relationship('Reported', backref='post',cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.post_id} {self.title} {self.content} {self.user_id}'


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(50), nullable=False)
    user_id = db.Column(Integer, ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, nullable=False)
    parent_type = db.Column(db.String(20), nullable=False)


class Like(db.Model):
    like_id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, ForeignKey('user.id'))
    parent_id = Column(Integer, nullable=False)
    parent_type = Column(String(20), nullable=False)


class Suggesstion(db.Model):
    s_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    post_id = Column(Integer, ForeignKey('post.post_id',ondelete='CASCADE'))
    content = Column(db.String, nullable=False)
    rejected = Column(db.Boolean, default=False)

class Reported(db.Model):
    report_id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    post_id = Column(Integer, ForeignKey('post.post_id',ondelete='CASCADE'))


