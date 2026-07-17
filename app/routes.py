from flask import render_template, flash, redirect, url_for, request
import mysql.connector
from app import app
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User
from urllib.parse import urlsplit

def get_db():
    return mysql.connector.connect(
            host='localhost', 
            user='root',
            password='root',
            database='today_pay'
            )

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
                sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(url_for('index'))

    return render_template('login.html', title='Sign in', form=form)

@app.route('/addEmployee', methods=['GET', 'POST'])
@login_required
def addEmployee():
    form = addEmployeeForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role=form.role.data)
        user.set_password(form.password.data)
        employee = Employee(
                first_name=form.first_name.data,
                last_name=form.last_name.data, 
                email=form.email.data, 
                job_title=form.job_title.data)
        employee.user = user

        db.session.add(user)
        db.session.add(employee)
        db.session.commit()
        flash('Employee Added!')
        return redirect(url_for('index'))

    return render_template('addEmployee.html', title='Add Employee', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
