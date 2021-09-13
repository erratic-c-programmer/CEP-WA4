from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, PasswordField, SubmitField
from wtforms.fields.html5 import DateField

from wtforms.validators import InputRequired, ValidationError, DataRequired

from datetime import datetime
import string


class TaskForm(FlaskForm):
    name = StringField("Task Name", validators=[InputRequired()])
    description = TextAreaField("Task Description")
    tdate = DateField("Date")
    completed = BooleanField("completed?")
    # add new field to render - tags
    tags = StringField("Tag (delimit each tag by comma)")

    def validate_tdate(form, field):
        today = datetime.today().date()

        if today > field.data:  # if the date is in the past
            raise ValidationError("You must not enter a date in the past")

    """This is added after the last video - Video 10 - to show how you can return more than one error when doing multiple validations on a single field
  
  Here we are making it illegal for user to input a task name that is less than 3 characters and the task name should also not contain any punctuations!
   """

    def validate_name(form, field):
        validated = True  # default state of validation
        if len(field.data) < 3:
            form.name.errors.append(
                "Length of Task Name must be more than 3 characters!"
            )
            validated = False

        if len([ch for ch in field.data if ch in string.punctuation]) > 0:
            form.name.errors.append("Task name should not have punctuations")
            validated = False
        return validated


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class CreateAccount(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def validate_password(form, field):
        validated = True  # default state of validation
        if len(field.data) < 8:
            form.name.errors.append(
                "Length of password must be more than 8 characters!"
            )
            validated = False
