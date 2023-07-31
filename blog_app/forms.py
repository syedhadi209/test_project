from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, ValidationError, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed
from blog_app.models import User
from flask import flash
from flask_login import current_user


class SignUpForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email Already Taken!!!!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            verified = user.verified
            if not verified:
                raise ValidationError("Your Account is not verified Kindly Check your mail.")
            
        if not user:
            raise ValidationError("Incorrect Credentials")
        


class NewPost(FlaskForm):
    title = StringField("Title",validators=[DataRequired(), Length(max=20)])
    content = TextAreaField("Description")
    attachment = FileField("Add Attachment",validators=[FileAllowed(['jpg','jpeg'])])
    submit = SubmitField("Create New Post")


class CommentForm(FlaskForm):
    comment = StringField("Comment",validators=[DataRequired()])
    submit = SubmitField("Comment")


class UpdatePostForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired(), Length(max=20)])
    content = TextAreaField("Description")
    attachment = FileField("Add Attachment",validators=[FileAllowed(['jpg','jpeg'])])
    submit = SubmitField("Update Post")


class ReplyForm(FlaskForm):
    reply = StringField("Reply",validators=[DataRequired()])
    submit = SubmitField("Reply")


class SuggesstionForm(FlaskForm):
    suggesstion = StringField("Give Suggesstion", validators=[DataRequired()])
    submit = SubmitField("Add Suggesstion")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update Info")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            print(user)
            if user:
                raise ValidationError("Username Already Exists")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email Already Exists")
