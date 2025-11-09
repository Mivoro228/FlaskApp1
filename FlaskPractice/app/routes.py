from flask import render_template, flash, redirect, url_for, request
#-*- coding: utf-8 -*-
from app import app
import sqlalchemy as sa
from datetime import datetime, timezone
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from app import db
from app.models import User, Post
from app.forms import EmptyForm, PostForm

#...

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form=PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
    posts = db.session.scalars(current_user.following_posts()).all()
    return  render_template("index.html", title ='Home Page', form=form,
                             posts = posts)
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
    form = EmptyForm()
    return render_template('user.html', posts = posts, user=user, form=form)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
@app.route('/edit_profile', methods= ['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )
        if user is None:
            flash(f'Пользователь {username} не найден.')
            return redirect(url_for('index'))
        if user == current_user:
            flash(f'Вы не можете подписаться на самого себя')
            return redirect(url_for('index', user=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'Вы подписались на {username}!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
    
@app.route('/unfollow/<username>', methods = ['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )
        if user is None:
            flash(f'пользователь {username} не найден')
            return redirect(url_for('index'))
        if user == current_user:
            flash(f'нельзя отписаться от самого себя')
            return redirect(url_for('index', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'Вы отписались от {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
@app.route('/explore')
@login_required
def explore():
    query = sa.select(Post). order_by(Post.timestamp.desc())
    posts = db.session.scalar(query).all()
    return render_template('index.html', title = "Explore", posts=posts)