import bcrypt
from flask import Flask, redirect, request, flash, session, url_for
from flask import render_template
from flask import current_app as app
from .database import db
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import login_required, current_user, logout_user, login_user, LoginManager
from application.models import User, Tracker, TrackerLogs
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    username = StringField(validators = [InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators = [InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit  = SubmitField("Register")

    def validate_usrrname(self,username):
        existing_username = User.query.filter_by(username = username.data).first()
        if existing_username:
            raise ValidationError("This username already exists")

class LoginForm(FlaskForm):
    username = StringField(validators = [InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Usrrname"})
    password = PasswordField(validators = [InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit  = SubmitField("Log In")


@app.route("/")
def home():
    return render_template("welcome.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
     form = LoginForm()
     if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            session['username'] = user.username
            if bcrypt.check_password_hash(user.password, form.password.data):
                session['password'] = user.password
                login_user(user)
                username=current_user.username
                return redirect('dashboard')

        return '<h1>Invalid username or password<h1>'
     return render_template('login.html', form = form)
@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html', form = form)

@app.route("/dashboard", methods = ['GET','POST'])
@login_required
def dashboard():
    return render_template("index.html", user=current_user, datetime=datetime)

@app.route("/notfound/<error>")
def notfound(error):
    return render_template('notfound.html',error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return login()

@app.route('/tracker/add',methods=['GET','POST'])
@login_required
def add_tracker():
    if request.method=='POST':
        u_id=current_user.get_id()
        name=request.form.get('name')
        desc=request.form.get('desc')
        type=request.form.get('type')
        set=request.form.get('settings')
        if name in [i.name for i in User.query.get(u_id).trackers]:
            return notfound('Tracker name should be unique')

        if type=='Multiple-choice':
            if set=="":
                return notfound('Tracker setting not valid, Multi-Choice should have setting separated by comma.')
        elif set!="":
            set=""
        add=Tracker(user_id=u_id,name=name,desc=desc,type=type,settings=set)
        db.session.add(add)
        db.session.commit()
        return dashboard()
    return render_template('add_tracker.html',user=current_user)

@app.route('/tracker/<int:tracker_id>',methods=['GET','POST'])
@login_required
def view_tl(tracker_id):
    if (tracker_id,) not in db.session.query(Tracker.tracker_id).all():
        return notfound('tracker_id_not_found')
    t=Tracker.query.get(tracker_id)
    tl=TrackerLogs.query.filter(TrackerLogs.tracker_id==tracker_id).order_by(TrackerLogs.log_datetime)
    x,y=[],[]
    fig=plt.figure(figsize=(8,5))
    ax = fig.gca()
    if request.method=='POST' and request.form.get('period'):
        p=request.form.get('period')
        if p=='Custom':
            llim=request.form['customdatetimel']
            hlim=request.form['customdatetimeh']
            comp='%Y-%m-%dT%H:%M'
        elif p=='Today':
            llim=datetime.today().strftime('%d/%m/%y')
            hlim=llim
            comp='%d/%m/%y'
        elif p=='1Month':
            llim=datetime.today().strftime('%m/%y')
            hlim=llim
            comp='%m/%y'
        elif p=='All':
            llim,hlim,comp='','',''
    else:
      llim,hlim,comp='','',''

    for i in tl:
        if i.log_datetime.strftime(comp)>=llim and i.log_datetime.strftime(comp)<=hlim:
            x.append(i.log_datetime)
            if t.type=='Integer':
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                plt.ylabel('Int')
                y.append(int(i.log_value))
            elif t.type=='Numeric':
                plt.ylabel('Float')
                y.append(float(i.log_value))
            elif t.type=='Multiple-choice':
                plt.ylabel('Options')
                y.append(i.log_value)
            elif t.type=='Time':
                ax.yaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
                y.append(datetime.strptime(i.log_value,"%H:%M:%S"))
    plt.plot(x,y,marker='o',color='b',linestyle='--')
    plt.gcf().autofmt_xdate()
    plt.savefig('static/images/chart.png')
    if len(x)>0:
        img='/static/images/chart.png'
    else:
        img=""
    return render_template('tracker.html',tracker=t,chart=img)

@app.route('/tracker/<int:tracker_id>/update',methods=['GET','POST'])
@login_required
def update_tracker(tracker_id):
    if (tracker_id,) not in db.session.query(Tracker.tracker_id).all():
        return notfound('tracker_id_not_found')
    t=Tracker.query.get(tracker_id)
    if request.method=='POST':
        if request.form.get('name')!=t.name or request.form.get('desc')!=t.desc or request.form.get('type')!=request.form.get('settings'):
            db.session.query(TrackerLogs).filter(TrackerLogs.tracker_id==tracker_id).delete()
        updict={Tracker.name:request.form['name'],Tracker.desc:request.form['desc'],Tracker.type:request.form['type'],Tracker.settings:request.form['settings']}
        print(updict)
        db.session.query(Tracker).filter(Tracker.tracker_id==tracker_id).update(updict)
        db.session.commit()
        return dashboard()
    return render_template('update_tracker.html',tracker=t,user=current_user)

@app.route('/tracker/<int:tracker_id>/delete',methods=['GET','POST'])
@login_required
def delete_tracker(tracker_id):
    if (tracker_id,) not in db.session.query(Tracker.tracker_id).all():
        return notfound('tracker_id_not_found')
    t=Tracker.query.get(tracker_id)
    db.session.delete(t)
    db.session.commit()
    return dashboard()

@app.route('/<int:tracker_id>/log/add',methods=['GET','POST','PUT'])
@login_required
def add_logs(tracker_id): 
    if (tracker_id,) not in db.session.query(Tracker.tracker_id).all():
        return notfound('tracker_id_not_found')
    t=Tracker.query.get(tracker_id)
    if request.method=='POST':
        value=request.form.get('value')
        if t.type=='Time':
            check=datetime.strptime(value,'%H:%M:%S')
        log_datetime=datetime.strptime(request.form.get("time"),'%d/%b/%Y, %H:%M:%S.%f')
        if t.lastupdate==None or t.lastupdate<log_datetime:
            t.lastupdate=log_datetime
        l=TrackerLogs(tracker_id=tracker_id,log_datetime=log_datetime,note=request.form.get('note'),log_value=value)
        db.session.add(l)
        db.session.commit()
        return view_tl(tracker_id)
    timedict={'start':'','end':'','duration':''}
    if request.method=='GET':
        if request.args.get('start'):
            s=request.args.get('start')
        elif request.args.get('startb')=="start":
            s=datetime.now().strftime('%H:%M:%S')
        else:
            s=''
        if request.args.get('end'):
            e=request.args.get('end')
        elif request.args.get('endb')=="end":
            e=datetime.now().strftime('%H:%M:%S')
        else:
            e=''
        d=''
        if s!='' and e!='':
            d=datetime.strptime(e,'%H:%M:%S')-datetime.strptime(s,'%H:%M:%S')
        timedict={'start':s,'end':e,'duration':d}
    return render_template('add_logs.html',t=t,datetime=datetime,timedict=timedict)

@app.route('/<int:log_id>/log/update',methods=['GET','POST'])
@login_required
def update_log(log_id):
    if (log_id,) not in db.session.query(TrackerLogs.log_id).all():
        return notfound('log_id_not_found')
    l=TrackerLogs.query.get(log_id)
    if request.method=='POST':
        log_value=request.form.get("value")
        log_note=request.form.get("note")
        log_datetime=datetime.strptime(request.form.get("time"),'%d/%b/%Y, %H:%M:%S.%f')
        db.session.query(TrackerLogs).filter(TrackerLogs.log_id==log_id).update({'log_value':log_value,'note':log_note,'log_datetime':log_datetime})
        db.session.commit()
        return view_tl(l.tracker_id)
    return render_template('update_logs.html',datetime=datetime,log=l)

@app.route('/<int:log_id>/log/delete',methods=['GET','POST'])
@login_required
def delete_log(log_id):
    #validation
    if (log_id,) not in db.session.query(TrackerLogs.log_id).all():
        return notfound('log_id_not_found')
    l=TrackerLogs.query.get(log_id)
    t=l.tracker_id
    db.session.delete(l)
    db.session.commit()
    return view_tl(t)