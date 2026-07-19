from typing import Optional
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[str] = so.mapped_column(sa.String(10))

    employee: so.Mapped["Employee"] = so.relationship(
            back_populates="user", uselist=False
            )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_manager(self):
        return self.role in ("manager", "admin")
    
    @property
    def is_employee(self):
        return self.role in ("employee", "admin")

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Employee(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    email: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    job_title: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    pay_rate: so.Mapped[float] = so.mapped_column(sa.Float, server_default="0.0")
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, server_default=sa.true())
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)

    user: so.Mapped["User"] = so.relationship(back_populates="employee")
    commute_logs: so.Mapped[list["CommuteLog"]] = so.relationship(back_populates="employee")
    rates: so.Mapped["Rates"] = so.relationship(back_populates="employee")

    def __repr__(self):
        return '<Employee Email {}>'.format(self.email)

class CommuteLog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    employee_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey("employee.id"), index=True)

    start_time: so.Mapped[datetime] = so.mapped_column(
            sa.DateTime, default=datetime.utcnow, nullable=False)
    end_time: so.Mapped[datetime | None] = so.mapped_column(sa.DateTime, nullable=True)

    mileage: so.Mapped[float] = so.mapped_column(sa.Float, nullable=True)

    employee: so.Mapped["Employee"] = so.relationship(back_populates="commute_logs")

class Rates(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    commute_rate: so.Mapped[float] = so.mapped_column(sa.Float)
    mile_reimbursement: so.Mapped[float] = so.mapped_column(sa.Float)
    date: so.Mapped[datetime] = so.mapped_column(
            sa.DateTime, default=datetime.utcnow, nullable=False)
    changed_by: so.Mapped[int] = so.mapped_column(sa.ForeignKey("employee.id"))
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, server_default=sa.true())

    employee: so.Mapped["Employee"] = so.relationship(back_populates="rates")
