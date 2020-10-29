from datetime import datetime
from hashlib import sha256

from flask import Flask, render_template, request
from flask import session, redirect, url_for

import key
from models.database import db_session
from models.models import WishContent, User

from flask_bootstrap import Bootstrap
app = Flask(__name__)
app.secret_key=key.SECRET_KEY
bootstrap=Bootstrap(app)

@app.route('/')
@app.route('/index')
def index():
    if 'user_name' in session:
        name=request.args.get('name')
        all_wish=WishContent.query.all()
        esa=['bone','melon','nothing']
        return render_template('index.html',name=name,all_wish=all_wish,esa=esa)
    else:
        return redirect(url_for('top',status='logout'))


@app.route('/esa',methods=['post'])
def esa():
    food=request.form.get('radio')
    esa = ['bone', 'melon', 'nothing','go back']
    return render_template('index.html',food=food,esa=esa)


@app.route('/add',methods=['post'])
def add():
    title=request.form['title']
    body=request.form['body']
    content=WishContent(title,body,datetime.now())
    db_session.add(content)
    db_session.commit()
    return redirect(url_for('index'))

@app.route('/update',methods=['post'])
def update():
    content=WishContent.query.filter_by(id=request.form['update']).first()
    content.title=request.form['title']
    content.bosy=request.form['body']
    db_session.commit()
    return redirect(url_for('index'))


@app.route('/delete',methods=['post'])
def delete():
    id_list=request.form.getlist('delete')
    for id in id_list:
        content=WishContent.query.filter_by(id=id).first()
        db_session.delete(content)
    db_session.commit()
    return redirect(url_for('index'))


@app.route('/top')
def top():
    status=request.args.get('status')
    return render_template('top.html',status=status)


@app.route('/login',methods=['post'])
def login():
    user_name = request.form['user_name']
    user = User.query.filter_by(user_name=user_name).first()
    if user:
        password = request.form['password']
        hashed_password = sha256((user_name + password + key.SALT).encode("utf-8")).hexdigest()
        if user.hashed_password == hashed_password:
            session['user_name'] = user_name
            return redirect(url_for('index'))
        else:
            return redirect(url_for('top',status="wrong_password"))
    else:
        return redirect(url_for('top',status="user_notfound"))


@app.route('/newcomer')
def newcomer():
    status=request.args.get('status')
    return render_template('newcomer.html',status=status)


@app.route('/registar',methods=['post'])
def registar():
    user_name = request.form['user_name']
    user = User.query.filter_by(user_name=user_name).first()
    if user:
        return redirect(url_for("newcomer",status="exist_user"))
    else:
        password = request.form['password']
        hashed_password = sha256((user_name + password + key.SALT).encode("utf-8")).hexdigest()
        user = User(user_name, hashed_password)
        db_session.add(user)
        db_session.commit()
        session['user_name'] = user_name
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user_name',None)
    return redirect(url_for('top',status='logout'))


if __name__ == '__main__':
    app.run(debug=True)
