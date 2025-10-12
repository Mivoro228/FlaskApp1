from flask import render_template, flash, redirect, url_for, request
#-*- coding: utf-8 -*-
from app import app
import sqlalchemy as sa
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from app import db
from app.models import User

#...

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username' : 'Miha'},
            'body':'Big sus in New-York City'
        },
        {
            'author': {'username': 'Putin'},
            'body': 'Geopolitics in Russia'
        },
        {
            'author':{'username': 'king-kong'},
            'body': 'GRaaaaa'
        }
    ]
    return  render_template('index.html', title ='Home Page', posts = posts)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:#Если пользователь авторизован, возвращаем index ссылку
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():#Если пользователь отправил запрос POST метода и все данные прошли проверку
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))# запрос к бд
        if user is None or not user.check_password(form.password.data):#проверка на правильность ввода
            flash('Invalid username or password')# отображение сообщения при помощи функции flesh(отображает один раз)
            return redirect(url_for('login'))# возвращение на страницу входа
        login_user(user, remember=form.remember_me.data)#Если всё в порядке, добавляем куки файл, если нажата кнопка запомнить
        next_page = request.args.get('next')#Получаем страницу, на которую пользователь хотел перейти
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
            return redirect(next_page)
        return redirect(next_page)
    return render_template('login.html', title ='Sign In', form=form)
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html', title= 'Register', form=form)
@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.Select(User).where(User.username == username))
    posts = [
        {'author' : user, 'body': 'Test post #1'},
        {'author' : user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', posts = posts, user=user)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))