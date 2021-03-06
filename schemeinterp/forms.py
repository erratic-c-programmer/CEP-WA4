from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField

from wtforms.validators import InputRequired, ValidationError, DataRequired

from datetime import datetime
import string

# class to create new tasks
class TaskForm(FlaskForm):
    name = StringField("Title", validators=[InputRequired()])
    description = TextAreaField("Content")
    # add new field to render - tags
    tags = StringField("Tag (delimit each tag by comma)")

    def validate_name(form, field):
        validated = True  # default state of validation
        if len(field.data) < 3:
            form.name.errors.append("Length of title must be more than 3 characters!")
            validated = False

        if len([ch for ch in field.data if ch in string.punctuation]) > 0:
            form.name.errors.append("Task name should not have punctuations")
            validated = False
        return validated


# class to create reply
class ReplyForm(FlaskForm):
    reply_content = StringField("Reply contents:", validators=[InputRequired()])

    def validate_reply(form, field):
        validated = True  # default state of validation
        if len(field.data) > 100000:
            form.reply_content.errors.append(
                "Length of Reply must be less than 100000 characters!"
            )
            validated = False

        return validated


# class for user to login
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


# class to create account
class CreateAccount(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    email = EmailField("Email", validators=[InputRequired()])

    def validate_password(form, field):
        validated = True  # default state of validation
        if len(field.data) < 8:
            form.password.errors.append(
                "Length of password must be more than 8 characters!"
            )
            validated = False
        return validated
