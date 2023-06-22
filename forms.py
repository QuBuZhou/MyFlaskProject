from wtforms import Form, StringField, ValidationError, IntegerField
from wtforms.validators import length, email, equal_to, InputRequired
from models import User, EmailCaptcha


class BaseForm(Form):
    @property
    def messages(self):
        message_list = []
        if self.errors:
            for errors in self.errors.values():
                message_list.extend(errors)
            return message_list


class RegisterForm(BaseForm):
    username = StringField(validators=[length(min=3, max=20, message="请输入正确长度的用户名！")])
    email = StringField(validators=[email(message="请输入正确格式的邮箱！")])
    password = StringField(validators=[length(min=6, max=20, message="请输入正确长度的密码！")])
    confirm_password = StringField(validators=[equal_to('password', message='两次密码不一致！')])
    captcha = StringField(validators=[length(min=4, max=4, message="请输入正确长度的验证码！")])

    def validate_email(self, field):
        test_email = field.data
        user = User.query.filter_by(email=test_email).all()
        if len(user):
            raise ValidationError("邮箱已经被注册！")

    def validate_name(self, field):
        test_name = field.data
        role = User.query.filter_by(name=test_name).all()
        if len(role):
            raise ValidationError("用户名已经被注册！")

    def validate_captcha(self, field):
        test_captcha = field.data
        print(test_captcha)
        email_captcha = EmailCaptcha.query.filter_by(email=email).all()
        if len(email_captcha):
            raise ValidationError("请点击【发送验证码】！")
        email_captcha = EmailCaptcha.query.first()
        if not email_captcha or test_captcha != email_captcha.captcha:
            raise ValidationError("验证码不正确！")


class ReleaseForm(BaseForm):
    title = StringField(validators=[length(min=2, max=100, message="请输入正确长度的标题！")])
    content = StringField(validators=[length(min=2, message="请输入正确长度的内容！")])


class CommentForm(BaseForm):
    content = StringField(validators=[length(min=1, max=5000, message="请输入正确长度的评论！")])
