import json

from flask import Flask, render_template, request, flash, redirect, url_for, session, g
from flask_mail import Message
from flask_paginate import Pagination

from exts import mail, db, csrf
import random
from forms import RegisterForm, ReleaseForm
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from models import User, EmailCaptcha, Board, Post, Comment
import config
import commands
import re

app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
migrate = Migrate(app, db)
db.init_app(app)
mail.init_app(app)
csrf.init_app(app)

# 初始化命令
app.cli.command("create-boards")(commands.create_board)
app.cli.command("create-admin")(commands.create_admin)
app.cli.command("create-test-port")(commands.create_test_post)


# 删除回复
@app.route('/post/<int:post_id>/<int:comment_id>')
def delete_comment(post_id, comment_id):
    if not session.get('logged_in'):
        return redirect(f'/post/{post_id}')
    user = User.query.filter_by(username=session['username']).first()
    post = Post.query.get(post_id)
    if post in user.posts or user.role == 'admin':
        comment = Comment.query.get(comment_id)
        print(comment.content)
        db.session.delete(comment)
        db.session.commit()
        return redirect(f'/post/{post_id}')
    else:
        return redirect(f'/post/{post_id}')

# 删除帖子
@app.route("/post/<int:post_id>/delete")
def delete_post(post_id):
    if not session.get('logged_in'):
        return redirect(f'/post/{post_id}')
    user = User.query.filter_by(username=session['username']).first()
    post = Post.query.get(post_id)
    if post in user.posts or user.role == 'admin':
        db.session.delete(post)
        db.session.commit()
        return redirect('/post')
    else:
        return redirect(f'/post/{post_id}')


# 发送验证码邮件
@app.route("/mail/captcha")
def mail_captcha():
    email = request.args.get("email")
    print('email=', email)
    pattern = re.compile('^\w+[\.\w]*@[\.\w+]*.[com|gov|net]$')
    res = pattern.match(email)
    if not res: return "<b>你输入的邮箱地址不合法！</b>"
    captcha = ""
    for i in range(4):
        captcha += str(random.randint(0, 9))
    message = Message(subject="验证码：曲不周的个人博客", recipients=[email], body=f"验证码：{captcha}")
    res = EmailCaptcha.query.filter_by(email=email).first()
    print('res:', res)
    if not res:
        email_captcha = EmailCaptcha(email=email, captcha=captcha)
        db.session.add(email_captcha)
        db.session.commit()
        mail.send(message)
    else:
        mail.send(message)
        res.captcha = captcha
        db.session.commit()

    return "<b>发送验证码成功！</b>"


# 登录用户
@app.route("/login")
def login():
    return render_template('login.html')


# 注册用户
@app.route("/register", methods=['GET'])
def register_user():
    return render_template("register.html")


# 发送评论
@app.route("/post/<int:post_id>/comment", methods=['POST'])
def public_comment(post_id):
    data = request.json
    content = data['content']
    comment = Comment(content=content, post_id=post_id,
                      author=User.query.filter_by(username=session['username']).first())
    db.session.add(comment)
    db.session.commit()
    return redirect(f'/post/{post_id}')


# 查看帖子详情
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get(post_id)
    post.read_count += 1
    db.session.commit()
    return render_template('content.html', post=post, post_id=post_id)


# 浏览博客
@app.route("/post")
def blog_content():
    boards = Board.query.all()
    page = request.args.get('page', type=int, default=1)
    start = (page - 1) * app.config.get("PER_PAGE_COUNT")
    end = start + app.config.get("PER_PAGE_COUNT")
    query_obj = Post.query.order_by(Post.create_time.desc())
    board_id = request.args.get('board_id', type=int, default=0)
    if board_id:
        query_obj = query_obj.filter_by(board_id=board_id)
    total = query_obj.count()
    posts = query_obj.slice(start, end)
    pagination = Pagination(bs_version=5, page=page, total=total, outer_window=0, inner_window=2, alignment='center')

    context = {
        'posts': posts,
        'boards': boards,
        'pagination': pagination,
        'current_board': board_id
    }

    return render_template('posts.html', **context)


# 发布帖子
@app.route("/release/check", methods=["POST"])
def release_check():
    data = request.json
    title = data['title']
    content = data['content']
    board_id = data['board_id']
    post = Post(title=title, content=content, board_id=board_id,
                author=User.query.filter_by(username=session['username']).first())
    session.pop('_flashs', None)
    db.session.add(post)
    db.session.commit()
    return redirect('/')


# 注册用户
@app.route("/register/check", methods=["POST"])
def register_check():
    form = RegisterForm(request.form)
    email = form.email.data
    username = form.username.data
    password = form.password.data
    if form.validate():
        user = User(username=username, email=email, password=password, role='user')
        db.session.add(user)
        db.session.commit()
        session.pop('_flashs', None)
        return redirect(url_for('main_page'))


    else:
        for message in form.messages:
            flash(message)
        return redirect('/register')


# 登录用户
@app.route("/login/check", methods=['POST'])
def login_check():
    form = RegisterForm(request.form)
    username = form.username.data
    password = form.password.data
    check_user = User.query.filter_by(username=username).first()
    if not check_user:
        flash("该用户名不存在！")
        return redirect('/login')
    if password != check_user.password:
        flash("密码不正确！")
        return redirect('/login')

    session.pop('_flashs', None)
    session['logged_in'] = True
    session['username'] = username
    session['id'] = str(check_user.id)
    return redirect('/')


# 发布页面
@app.route('/release')
def release_post():
    if not session.get('logged_in'): return redirect('/')
    boards = Board.query.all()
    return render_template('release.html', boards=boards)


# 注销
@app.route('/log_out')
def log_off():
    session.clear()
    return redirect('/')


# 主页
@app.route("/")
def main_page():
    boards = Board.query.all()
    return render_template('index.html', boards=boards)


if __name__ == '__main__':
    app.run()
