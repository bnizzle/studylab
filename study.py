import os
import json
from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import IntegerField, SubmitField
from datetime import datetime, date
from wtforms.validators import Required
from flask.ext.moment import Moment


app = Flask(__name__)

app.config.from_object("config")


db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    surname = db.Column(db.String(64), index=True)
    count = db.Column(db.Integer)


    def __repr__(self):
        return '%r' % self.id



class Reward(db.Model):
    __tablename__ = 'reward'
    entry = db.Column(db.Integer,primary_key=True,autoincrement=True)
    student_id = db.Column(db.Integer,index=True)
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


@app.route('/', methods=['GET', 'POST'])
def index():
    id = None
    form = IdForm()
    if form.validate_on_submit():
        if db.session.query(Student).filter(Student.id == form.id.data) is not None:
            db.session.query(Student).filter(Student.id == form.id.data).update({'count': Student.count+1})
            db.session.commit()
            reward_check = db.session.query(Attendance).filter(Attendance.student_id == form.id.data).count()
            if (reward_check % 3) == 0:
                reward_add = Reward(student_id=form.id.data)
                db.session.add(reward_add)
        else:
            flash("Looks like you aren't in the system properly. Please contact the ICT Department.")
        id_add = Attendance(student_id=form.id.data)
        db.session.add(id_add)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('index.html', form=form, id=id)


@app.route('/teacher')
def teacher():
    attendance = db.session.query(Attendance).order_by(Attendance.timestamp.desc()).limit(10)
    reward = db.session.query(Reward).filter(Reward.reward_given != 1).limit(5)
    count = db.session.query(Student).order_by(Student.count.desc()).limit(5)
    return render_template('teacher.html', attendance=attendance, count=count, reward=reward)

@app.route('/teacher/id/<studentid>')
def student(studentid):
    details = db.session.query(Student).filter(Student.id == studentid)
    student_attendance = db.session.query(Attendance).filter(Attendance.student_id == studentid).order_by(Attendance.timestamp.desc()).all()
    return render_template("student.html", details=details, student_attendance=student_attendance)

@app.route('/teacher/browse')
def browse():
    return render_template("browse.html")

@app.route('/teacher/rewards')
def rewards():
    return render_template("rewards.html")

if __name__ == '__main__':
    app.run(debug=True)
