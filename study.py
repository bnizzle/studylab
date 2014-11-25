from flask import Flask, render_template, session, redirect, url_for, flash, g
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy, Pagination
from flask.ext.moment import Moment
from models import *
from flask.ext.mail import Mail


app = Flask(__name__)

# Set config file and import config settings
app.config.from_object("config")
from config import *

# Init all the things!
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['STUDY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['STUDY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


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

@app.route('/teacher/browse', methods=['GET', 'POST'])
@app.route('/teacher/browse/<int:page>', methods=['GET','POST'])
def browse(page=1):
    student_query = Student.query.paginate(page, POSTS_PER_PAGE, False)
    student_items = student_query.items
    return render_template("browse.html", student_items=student_items)

@app.route('/teacher/rewards')
def rewards():
    return render_template("rewards.html")

if __name__ == '__main__':
    app.run(debug=True)
