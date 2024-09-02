from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, URL, NumberRange, Email, ValidationError, EqualTo
from app.models import User



class UrlForm(FlaskForm):
    url1 = StringField('URL1: ', validators=[DataRequired()])
    url2 = StringField('URL2:')
    url3 = StringField('URL3:')
    url4 = StringField('URL4:')
    url5 = StringField('URL5:')
    submit = SubmitField('submit')

class WordCountForm(FlaskForm):
    max_count = IntegerField('maximum word count', validators=[NumberRange(min=50, max=300)], default=100)
    min_count = IntegerField('minimum word count', validators=[NumberRange(min=50, max=300)], default=100)

class LoginForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

    def validate_login(self, username, password):
        user = User.query.filter_by(username.data).first()
        if user is None or not user.check_password(password.data):
            raise ValidationError('Invalid User name or Password. Please Try again.')




class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is Already Registered. Please Try Again.')

class StoreForm(FlaskForm):
    folder = SelectField('Select Folder', coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

class SearchForm(FlaskForm):
    search = StringField('Search article',
                              render_kw={"placeholder": "Search article"})
    submit = SubmitField('Search')

class EditArticleForm(FlaskForm):
    tags = StringField('Tags')
    submit = SubmitField('Save')

class FolderForm(FlaskForm):
    name = StringField('Folder Name', validators=[DataRequired()])
    submit = SubmitField('Create')
