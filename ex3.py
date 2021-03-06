from flask import Flask, url_for, render_template, request, send_from_directory, g, abort, flash, session
from flask_session import Session
from werkzeug.utils import redirect, secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import sqlite3
import os
import uuid
import loginform
from flask_login import LoginManager, login_user
from FDataBase import FDataBase
from UserLogin import UserLogin



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = 'static/photos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
DATABASE = 'flsite.db'
DEBUG = True
SECRET_KEY = '&8\xa2|\x11\x0f\xcf\xe8\xc2\xa6\x85"\xfd~\x0c#\x06{>T\xb7\xe9\xd8\xc9'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.config['SESSION_PEMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)
login_manager = LoginManager(app)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db=connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/registration/', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        create_db()
        file = request.files['photo']
        if file and allowed_file(file.filename):
            s = uuid.uuid4()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(s) + '.jpg'))
            filename2db = str(s) + '.jpg'

            db = get_db()
            dbase = FDataBase(db)
            is_reg = dbase.adduser(request.form.get('named'), request.form.get('surname'), request.form.get('email'),
                          request.form.get('age'),
                          request.form.get('work'), request.form.get('position'),
                          generate_password_hash(request.form.get('password')), filename2db)
            if is_reg == "Error 1":
                flash("???????????????????????? ?? ?????????? email ?????? ????????????????????")
                return redirect(url_for('register'))
            if is_reg == "Error 2":
                flash("???? ?????????????????? ???????????????????????????????? ?????? ???????????? ????????????")
                return redirect(url_for('register'))
            if is_reg == True:
                return redirect(url_for('users')+'?page=0')


@app.route('/uploads/<name>')
def download_file(name):
    redirect(url_for('users')+'?page=1')

@app.route('/users/')
def users():

    db = get_db()
    dbase = FDataBase(db)
    authorized = ""
    id_sess = ""
    if 'login' in session:
        authorized = session['login']

    curr_page = int(request.args.get('page'))
    pgcount = 1
    remainder = 0
    all_users = dbase.getAllUsers()
    pgcount = len(all_users) // 4 + 1
    if pgcount == 0:
        pgcount = 1
    if curr_page > pgcount:
        abort(404)
    if pgcount % 4 > 0:
        remainder = len(all_users) % 4
    class pgstore:
        value = pgcount
    match curr_page:
        case 0:
            a = all_users[:4]
        case pgstore.value:
            a = all_users[pgcount - 1:remainder]
        case _:
            a = all_users[curr_page * 4:curr_page * 4 + 4]
    try:
        id_sess = session['_user_id']
    except:
        pass
    return render_template('users.html', users=a, curr_page=curr_page, pagecount=pgcount, is_auth=authorized.split(), id_sess=id_sess)

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    dbase = FDataBase(db)
    return UserLogin().fromDB(user_id, dbase)

@app.route('/auth/', methods=['POST', 'GET'])
def auth():
    db = get_db()
    dbase = FDataBase(db)
    form1 = loginform.LoginForm()
    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form.get('username'))
        if user and check_password_hash(user['password'], request.form.get('password')):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            session['login'] = userlogin.get_login()
            return redirect(url_for('users')+'?page=0')
        flash("???????????????? ??????????/????????????")
        return render_template('auth.html', form=form1, user=user)
    else:
        if request.args.get('avt') is not None:
            session.pop('login')
            session.pop('_user_id')
        if 'login' in session:
            return render_template('auth.html', form=form1, user=session['login'])
        return render_template('auth.html', form=form1)

@app.route('/account/', methods=['POST', 'GET'])
def account():
    is_adm = False
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        id_us = dbase.getUserByEmail((request.form.get('mail')))
        dbase.updateUser(id_us[0], request.form.get('names'), request.form.get('surname'), request.form.get('mail'),
                          request.form.get('age'),
                          request.form.get('work'), request.form.get('post'))
        db.commit()
        return redirect(url_for('users') + '?page=0')
    form1 = loginform.LoginForm()
    if 'login' in session:
        user = dbase.getUserByEmail(request.args.get('user'))
        if user:
            if(dbase.getUser(session['_user_id'])[9] == '??????????'):
                is_adm = True
            return render_template('account.html', user=user, id_sess=session['_user_id'], is_adm=is_adm)
        else:
            abort(404)
    else:
        return render_template('auth.html', form=form1)


@app.errorhandler(404)
@app.errorhandler(403)
@app.errorhandler(410)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
