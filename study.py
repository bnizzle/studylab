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


basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)

app.config['SECRET_KEY'] = "123456789"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


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
        else:
            flash("Looks like you aren't in the system properly. Please contact the ICT Department.")
        id_add = Attendance(student_id=form.id.data)
        db.session.add(id_add)
        return redirect(url_for('index'))
    return render_template('index.html', form=form, id=id)


@app.route('/teacher')
def teacher():
    attendance = db.session.query(Attendance).order_by(Attendance.timestamp.desc())
    return render_template('teacher.html', attendance=attendance)

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
