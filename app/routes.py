from flask import render_template, flash, redirect, url_for, request, abort
import mysql.connector
from app import app
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Employee, CommuteLog, Rates
from datetime import datetime
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


@app.route('/rates', methods=['GET', 'POST'])
@login_required
def rates():
    if not current_user.is_manager:
        abort(403)

    rate = Rates.query.filter_by(is_active=True).first()

    form = RatesForm(obj=rate)

    if form.validate_on_submit():
        if rate:
            rate.is_active=False

        new_rate = Rates(commute_rate=form.commute_rate.data,
                         mile_reimbursement = form.mile_reimbursement.data,
                         changed_by=current_user.employee.id)

        db.session.add(new_rate)
        db.session.commit()
        flash("Rates Updated")
        return redirect(url_for("index"))

    return render_template('rates.html', title="Rates", form=form, rate=rate)
    

@app.route('/employees', methods=['GET', 'POST'])
@login_required
def employees():
    if not current_user.is_manager:
        abort(403)

    query = sa.select(Employee)
    employees = db.session.scalars(query).all()

    return render_template('employees.html', title='Employees', employees=employees)

@app.route('/employees/new', methods=['GET', 'POST'])
@login_required
def addEmployee():
    if not current_user.is_manager:
        abort(403)

    form = addEmployeeForm()
    if form.validate_on_submit():
        existing_employee = Employee.query.filter_by(email=form.email.data).first()

        if existing_employee:
            flash("That email is already in use.")
            return render_template('addEmployee.html', title='Add Employee', form=form)


        user = User(username=form.username.data, role=form.role.data)
        user.set_password(form.password.data)
        employee = Employee(
                first_name=form.first_name.data,
                last_name=form.last_name.data, 
                email=form.email.data, 
                job_title=form.job_title.data,
                pay_rate=form.pay_rate.data)
        employee.user = user

        db.session.add(user)
        db.session.add(employee)
        db.session.commit()
        flash('Employee Added!')
        return redirect(url_for('employees'))

    return render_template('addEmployee.html', title='Add Employee', form=form)

@app.route('/employee/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def editEmployee(id):
    if not current_user.is_manager:
        abort(403)

    employee = Employee.query.filter_by(id=id).first()

    form = editEmployeeForm(obj=employee)

    if form.validate_on_submit():
        employee.first_name=form.first_name.data
        employee.last_name=form.last_name.data
        employee.email=form.email.data
        employee.job_title=form.job_title.data
        employee.pay_rate=form.pay_rate.data

        db.session.commit()
        flash("Employee Updated")

        return redirect(url_for('employees'))

    return render_template(
            'editEmployee.html', title='Edit Employee', form=form, employee=employee)

@app.route('/employee/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def deleteEmployee(id):
    if not current_user.is_manager:
        abort(403)

    employee = Employee.query.filter_by(id=id).first()

    employee.is_active = False
    db.session.commit()

    flash("Employee Removed")
    return redirect(url_for("employees"))
              

@app.route('/commuteLog', methods=['GET', 'POST'])
@login_required
def commuteLog():
    form = commuteLogForm()
    
    if form.validate_on_submit():
        commute = CommuteLog.query.filter(
                CommuteLog.employee_id==current_user.employee.id,
                CommuteLog.start_time.isnot(None),
                CommuteLog.end_time.isnot(None),
                CommuteLog.mileage.is_(None)
        ).order_by(
                CommuteLog.start_time.desc()
        ).first()

        if commute:
            commute.mileage = float(request.form["mileage"])
            db.session.commit()
            flash("Mileage added. Commute Log complete.")
            return redirect(url_for('index'))
        else: 
            flash("No pending commutes.")

    return render_template('commuteLog.html', title='Commute Log', form=form)


@app.route('/start_commute', methods=['POST'])
@login_required
def start_commute():

    active_commute = CommuteLog.query.filter_by(
        employee_id=current_user.employee.id, end_time=None
    ).first()

    if active_commute: 
        flash("You already have an active commute.")
        return redirect(url_for('commuteLog'))

    commute = CommuteLog(employee_id=current_user.employee.id)

    db.session.add(commute)
    db.session.commit()
    flash("Commute Started")

    return redirect(url_for('commuteLog'))


@app.route('/end_commute', methods=['POST'])
@login_required
def end_commute():
    commute = CommuteLog.query.filter_by(
            employee_id=current_user.employee.id, end_time=None
            ).first()

    if commute: 
        commute.end_time = datetime.utcnow()
        db.session.commit()
        flash("Commute Ended")

    return redirect(url_for("commuteLog"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
