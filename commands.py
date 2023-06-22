import random

import click
from exts import db
from models import Board, User, Post
from faker import Faker


def create_board():
    board_names = ["资源分享", "灌水聊天", "人生感悟"]
    for board_name in board_names:
        board = Board(name=board_name)
        db.session.add(board)
    db.session.commit()
    click.echo("板块添加成功！")


def create_admin():
    admin = User(username="曲不周", email="1137952368@qq.com", password='baihehe123', role='admin')
    db.session.add(admin)
    db.session.commit()
    click.echo("管理员注册成功！")


def create_test_post():
    fake = Faker(locale="zh_CN")
    author = User.query.first()
    boards = Board.query.all()
    click.echo("开始生成测试帖子...")
    for x in range(98):
        title = fake.sentence()
        content = fake.paragraph(nb_sentences=10)
        random_index = random.randint(0, 2)
        board = boards[random_index]
        post = Post(title=title, content=content, board=board, author=author)
        db.session.add(post)
        db.session.commit()
        click.echo("测试帖子生成成功！")