# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login,logout as auto_logout
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from bitcoinrpc.authproxy import AuthServiceProxy
from .Token import Token
from django.conf import settings as django_settings
import random,smtplib,decimal,requests,json
from email.mime.text import MIMEText
from email.utils import formataddr
from django.core.mail import EmailMultiAlternatives

# Create your views here.
token_confirm = Token(django_settings.SECRET_KEY)
def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if User.objects.filter(username=cd['username']):
                data = {'status': 1}
                return JsonResponse(data,safe=False)
            else:
                while True:
                    icode = "".join(random.sample(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                                          'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                                          'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4',
                                          '5', '6', '7', '8', '9'], 6))
                    if not User.objects.filter(icode=icode):
                        break
                user = User.objects.create_user(username=cd['username'], password=cd['password1'], icode=icode,pcode=cd['code'])
                user.save()
                #Login
                auth_login(request, user)
                data = {'status':2, 'email':cd['username']}
                return JsonResponse(data, safe=False)
    else:
        form = LoginForm()
        return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active == 1:
                    auth_login(request, user)
                    data = {'status': 1}
                    return JsonResponse(data, safe=False)
                else:
                    data = {'status': 2}
                    return JsonResponse(data, safe=False)
            else:
                data = {'status': 3}
                return JsonResponse(data, safe=False)
        else:
            data = {'status': 4}
            return JsonResponse(data, safe=False)
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

def logout(request):
    auto_logout(request)
    return HttpResponseRedirect('/')

def activate(request, token):
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        return render(request, 'activate.html', {'message': 1})
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'activate.html', {'message': 2})
    user.checkEmail = True
    user.save()
    return render(request, 'activate.html', {'message': 3})

def checkmail(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)
        token = token_confirm.generate_validate_token(user.username)
        message = "\n".join([u'{0},欢迎加入RISChain'.format(user.username), u'请访问该链接，完成用户验证:',
                             '/'.join([django_settings.DOMAIN, 'activate', token])])

        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(["RISChain", django_settings.EMAIL_HOST_USER])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["FK", user.username])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "RISChain用户注册验证!"  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP_SSL(django_settings.EMAIL_HOST, django_settings.EMAIL_PORT)
        server.login(django_settings.EMAIL_HOST_USER, django_settings.EMAIL_HOST_PASSWORD)
        server.sendmail(django_settings.EMAIL_HOST_USER, [user.username], msg.as_string())
        server.quit()
        #send_mail('RISChain用户注册验证!', message, django_settings.EMAIL_HOST_USER, [user.username], fail_silently=False)
        return JsonResponse('1', safe=False)
    else:
        return JsonResponse('0', safe=False)

def send(request):
    if request.method == 'POST':
        email = request.POST['email']
        #需查询是否有这个邮箱注册
        sendmail(email)
        return JsonResponse('1', safe=False)
    else:
        email = request.GET['email']
        # 需查询是否有这个邮箱注册
        sendmail(email)
        return render(request, 'send.html',{'email':email})

def sendmail(mail):
    token = token_confirm.generate_validate_token(mail)
    message = "\n".join(['Thank you!    Please click this link to confirm your email address.',
                         '/'.join([django_settings.DOMAIN, 'activate', token])])
    msg = MIMEText(message, 'plain')
    msg['From'] = formataddr(["SEC Support", django_settings.EMAIL_HOST_USER])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = mail  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = "Verify email address"  # 邮件的主题，也可以说是标题
    server = smtplib.SMTP_SSL(django_settings.EMAIL_HOST, django_settings.EMAIL_PORT)
    server.login(django_settings.EMAIL_HOST_USER, django_settings.EMAIL_HOST_PASSWORD)
    server.sendmail(django_settings.EMAIL_HOST_USER, [mail], msg.as_string())
    server.quit()
    return

def sendcode(request):
    seed = "1234567890"
    sa = []
    for i in range(4):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    request.session['tbcode'] = salt
    user = User.objects.get(id=request.user.id)
    message = "\n".join([u'您的验证码是：{0}'.format(salt)])
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = formataddr(["RISChain", django_settings.EMAIL_HOST_USER])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = formataddr(["FK", user.username])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = "RISChain添加提币地址验证!"  # 邮件的主题，也可以说是标题
    server = smtplib.SMTP_SSL(django_settings.EMAIL_HOST, django_settings.EMAIL_PORT)
    server.login(django_settings.EMAIL_HOST_USER, django_settings.EMAIL_HOST_PASSWORD)
    server.sendmail(django_settings.EMAIL_HOST_USER, [user.username], msg.as_string())
    server.quit()
    # send_mail('RISChain添加提币地址验证!', message, django_settings.EMAIL_HOST_USER, [user.username], fail_silently=False)
    return JsonResponse('1', safe=False)

def user(request):
    if request.user.is_authenticated:
        return render(request, 'user.html')
    else:
        return render(request, 'login.html')

def addAddress(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            address = request.POST['address']
            try:
                user = User.objects.get(eth_address=address)
                data = {'status': 2}
                return JsonResponse(data, safe=False)
            except:
                user = User.objects.get(id=request.user.id)
                user.eth_address = address
                user.save()
                data = {'status': 1}
                return JsonResponse(data, safe=False)
        return render(request, 'addAddress.html')
    return render(request, 'login.html')

def verifyInfo(request):
    if request.user.is_authenticated:
        return render(request, 'verifyInfo.html')
    else:
        return render(request, 'login.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        Contact.objects.create(name=name, email=email, subject=subject, message=message)
        return JsonResponse('1', safe=False)
    else:
        return JsonResponse('0', safe=False)

def test(request):
    subject, from_email, to = 'hello', 'noreply@sec.cool', '362395084@qq.com'
    text_content = 'This is an important message'
    html_content = u'''''欢迎使用找回密码功能。 
    请点击链接重置密码：<br/>http://passport.TEST.com/user/find_pwd.php?bcode=i9VSteFh2g<br/> 
    (该链接在24小时内有效)<br/> 
    如果上面不是链接形式，请将地址复制到您的浏览器(例如IE)的地址栏再访问'''
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()