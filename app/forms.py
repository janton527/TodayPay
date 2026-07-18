from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User, Employee

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class addEmployeeForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Temp Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = StringField('Role', validators=[DataRequired()])
    job_title = StringField('Job Title')
    pay_rate = FloatField('Pay Rate')

    submit = SubmitField('Add Employee')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None: 
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        employee = db.session.scalar(sa.select(Employee).where(
            Employee.email == email.data))
        if employee is not None:
            raise ValidationError('Please use a different email address.')

class editEmployeeForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    job_title = StringField('Job Title')
    pay_rate = FloatField('Pay Rate')

    submit = SubmitField('Edit Employee')

class commuteLogForm(FlaskForm):
    start_commute = SubmitField('Start Commute')
    end_commute = SubmitField('End Commute')

    mileage = FloatField('Mileage', validators=[DataRequired()])
    submit = SubmitField('Submit')

