from flask.ext.wtf import Form
from wtforms import IntegerField, SubmitField
from datetime import datetime
from wtforms.validators import Required
from study import db


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    surname = db.Column(db.String(64), index=True)
    house = db.Column(db.String(64), index=True)
    tutor = db.Column(db.String(64), index=True)
    year_group = db.Column(db.Integer, index=True)
    count = db.Column(db.Integer)


    def __repr__(self):
        return '%r' % self.id

    def student_lookup(self):
        return Student.query.order_by(Student.id)

class Reward(db.Model):
    __tablename__ = 'reward'
    entry = db.Column(db.Integer,primary_key=True,autoincrement=True)
    student_id = db.Column(db.Integer,index=True)
    first_name = db.Column(db.String(64),index=True)
    surname = db.Column(db.String(64),index=True)
    timestamp = db.Column(db.DateTime,index=True, default=datetime.now)
    reward_given = db.Column(db.Integer, default=0)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    entry = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.Integer,index=True)
    timestamp = db.Column(db.DateTime,index=True, default=datetime.now)

    def __init__(self, student_id):
        self.student_id = student_id

    def __repr__(self):
        return '%r' % (self.student_id)


class IdForm(Form):
    id = IntegerField('Please enter your Student ID', validators=[Required()])
    submit = SubmitField('Submit')