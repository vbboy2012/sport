from django import forms
from django.core.exceptions import ValidationError

class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名',max_length=100)
    password1 = forms.CharField(label='密码',widget=forms.PasswordInput())
    password2 = forms.CharField(label='密码', widget=forms.PasswordInput())
    vercode = forms.CharField(label='验证码', max_length=10, required=False)
    code = forms.CharField(label='邀请码', max_length=10,required=False)

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())