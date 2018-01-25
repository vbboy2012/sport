# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.utils import timezone
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login,logout as auto_logout
from .models import User,Country,Kyc,Contact,Reserve,Bonus,Config,Token as myToken,Telegram,Noip,Verification
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from .Token import Token
from django.conf import settings
import random,smtplib,json
from email.mime.text import MIMEText
from email.utils import formataddr
from django.core.mail import EmailMultiAlternatives
import requests

# Create your views here.
token_confirm = Token(settings.SECRET_KEY)
def index(request):
    # 访问网址时默认弹出首页
    if request.path == '/':
        user_config = getUserConfig(request)
        request.session["user_config"]['thisTemplateName'] = 'index'
        if user_config['language'] == 'Chinese':
            TemplateName = 'index.html'
        else:
            TemplateName = 'index_en.html'
        return render(request, TemplateName)
    # 在网站内跳转至首页
    else:
        templateName = getTemplateByLanguage(request)
        return render(request, templateName)

def register(request):
    if request.method == 'POST':
        regip = get_client_ip(request)
        try:
            Noip.objects.get(ip=regip)
            isLock = True
        except:
            isLock = False
        if isLock:
            data = {'status': 5}
            return JsonResponse(data, safe=False)
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                verification = Verification.objects.get(email=cd['username'],code=cd['vercode'])
                Verification.objects.filter(email=cd['username']).delete()
            except:
                data = {'status': cd['vercode']}
                return JsonResponse(data, safe=False)
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
                if cd['code']:
                    try:
                        parent = User.objects.get(icode=cd['code'])
                        if parent.is_active == 0:
                            data = {'status': 4}
                            return JsonResponse(data, safe=False)
                    except:
                        data = {'status': 3}
                        return JsonResponse(data, safe=False)
                user = User.objects.create_user(username=cd['username'], password=cd['password1'], icode=icode,pcode=cd['code'],ip=regip)
                user.save()
                # bonus = Bonus(user_id=user.id, email=user.username, dcb_bonus=100, hash=timezone.now(), status=0)
                # bonus.save()
                data = {'status': 2, 'email': cd['username']}
                return JsonResponse(data, safe=False)
    else:
        form = LoginForm()
        user_config = getUserConfig(request)
        if user_config['language'] == 'Chinese':
            TemplateName = 'register.html'
        else:
            TemplateName = 'register_en.html'
        return render(request, TemplateName, {'form': form})

def get_client_ip(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        regip = real_ip.split(",")[0]
    except:
        try:
            regip = request.META['REMOTE_ADDR']
        except:
            regip = ""
    return regip

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.checkEmail == 0:
                    data = {'status': 5,'email':user.username}
                    return JsonResponse(data, safe=False)
                elif user.is_active == 1:
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
        if request.user.is_authenticated:
            user_config = getUserConfig(request)
            if user_config['language'] == 'Chinese':
                TemplateName = 'user.html'
            else:
                TemplateName = 'user_en.html'
            return render(request, TemplateName)
        else:
            form = LoginForm()
            user_config = getUserConfig(request)
            if user_config['language'] == 'Chinese':
                TemplateName = 'login.html'
            else:
                TemplateName = 'login_en.html'
            return render(request, TemplateName, {'form': form})

def logout(request):
    auto_logout(request)
    return HttpResponseRedirect('/')

def activate(request, token):
    user_config = getUserConfig(request)
    if user_config['language'] == 'Chinese':
        TemplateName = 'activate.html'
    else:
        TemplateName = 'activate_en.html'
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        return render(request, TemplateName, {'message': 1})
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, TemplateName, {'message': 2})
    user.checkEmail = True
    user.save()
    auth_login(request, user)
    return render(request, TemplateName, {'message': 3})

def send(request):
    if request.method == 'POST':
        email = request.POST['email']
        # 需查询是否有这个邮箱注册
        sendHtmlmail(email)
        return JsonResponse('1', safe=False)
    else:
        email = request.GET['email']
        # 需查询是否有这个邮箱注册
        sendHtmlmail(email)
        user_config = getUserConfig(request)
        if user_config['language'] == 'Chinese':
            TemplateName = 'send.html'
        else:
            TemplateName = 'send_en.html'
        return render(request, TemplateName, {'email': email})

def sendmail(email):
    token = token_confirm.generate_validate_token(email)
    message = "\n".join(['Thank you!    Please click this link to confirm your email address.',
                         '/'.join([settings.DOMAIN, 'activate', token])])
    msg = MIMEText(message, 'plain')
    msg['From'] = formataddr(["DAOClub Support", settings.EMAIL_HOST_USER])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = email  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = "Verify email address"  # 邮件的主题，也可以说是标题
    server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.sendmail(settings.EMAIL_HOST_USER, [email], msg.as_string())
    server.quit()
    return

def sendHtmlmail(email):
    token = token_confirm.generate_validate_token(email)
    subject, from_email, to = 'Verify email address', settings.EMAIL_HOST_USER, email
    text_content = 'Thank you! Please click this link to confirm your email address.\n'+settings.DOMAIN+'/activate/'+token

    html_content = '<p>感谢您注册DAOClub! 请点击此链接确认您的电子邮件地址。</p>'
    html_content += '<p>如果链接无法使用，请将以下链接复制，并粘贴到新的浏览器地址栏中。</p>'
    html_content += '<p><strong><a href="' + settings.DOMAIN + '/activate/' + token + '">' + settings.DOMAIN + '/activate/' + token + '</a></strong></p>'
    html_content += '<br><br><br>'
    html_content += '<p>Thank you for registering DAOClub! Please click this link to confirm your email address.</p>'
    html_content += "<p>If the above link doesn't work, please copy and paste the following link in a new browser tab instead. </p>"
    html_content += '<p><strong><a href="'+settings.DOMAIN+'/activate/'+token+'">'+settings.DOMAIN+'/activate/'+token+'</a></strong></p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def sendCode(request):
    if request.method == 'POST':
        email = request.POST['username']
        if User.objects.filter(username=email):
            data = {'status': 2}
            return JsonResponse(data, safe=False)
        code = "".join(random.sample(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                                      'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                                      'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4',
                                      '5', '6', '7', '8', '9'], 6))
        subject, from_email, to = 'Verify email address', settings.EMAIL_HOST_USER, email
        text_content = 'Thank you! Your verification code:'+code

        html_content = '<p>您收到的验证码</p>'
        html_content += '<p><strong>'+code+'</strong></p>'
        html_content += '<br><br><br>'
        html_content += '<p>The verification code you received.</p>'
        html_content += '<p><strong>'+code+'</strong></p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        vercode = Verification(email=email,code=code,status=0)
        vercode.save()
        data = {'status': 1}
        return JsonResponse(data, safe=False)

def user(request):
    if request.user.is_authenticated:
        users = Bonus.objects.filter(user_id=request.user.id)
        dcbCount = 0
        for user in users:
            dcbCount += user.dcb_bonus
        tokens = myToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            dcbCount += token.dcb_num
        try:
            kyc = Kyc.objects.get(user_id=request.user.id)
        except:
            kyc = None
        user_config = getUserConfig(request)
        if user_config['language'] == 'Chinese':
            TemplateName = 'user.html'
        else:
            TemplateName = 'user_en.html'
        return render(request, TemplateName,{'users':users,'kyc':kyc,'dcbCount':dcbCount})
    else:
        user_config = getUserConfig(request)
        if user_config['language'] == 'Chinese':
            TemplateName = 'login.html'
        else:
            TemplateName = 'login_en.html'
        return render(request, TemplateName)

def token(request):
    if request.user.is_authenticated:
        config = Config.objects.get(id=1)
        privateCount = "{:,}".format(config.private_token_count)
        publicCount = "{:,}".format(config.public_token_count)
        privatePrice = "{:,}".format(config.private_price)
        publicPrice = "{:,}".format(config.public_price)
        currentTime = timezone.now()
        isStart = 0
        progress = 0
        stage = 1
        countdown = config.public_date_start
        endDate = config.public_date_end
        if currentTime > config.public_date_start:
            isStart = 1
            progress = config.public_received_token / config.public_token_count * 100
        if config.public_is_over:
            stage = 3
            isStart = 2
        elif config.private_is_over:
            stage = 2
        tokens = myToken.objects.filter(user_id=request.user.id)
        user_config = getUserConfig(request)
        if user_config['language'] == 'Chinese':
            TemplateName = 'token.html'
        else:
            TemplateName = 'token_en.html'
        return render(request, TemplateName,{'stage':stage,'isStart':isStart,'progress':progress,'endDate':endDate,'countdown':countdown,'privateCount':privateCount,'publicCount':publicCount,'privatePrice':privatePrice,'publicPrice':publicPrice,'tokens':tokens})
    else:
        user_config = getUserConfig(request)
        if user_config['language'] == 'Chinese':
            TemplateName = 'login.html'
        else:
            TemplateName = 'login_en.html'
        return render(request, TemplateName)

def addAddress(request):
    user_config = getUserConfig(request)
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
        config = Config.objects.get(id=1)
        if user_config['language'] == 'Chinese':
            TemplateName = 'addAddress.html'
        else:
            TemplateName = 'addAddress_en.html'
        return render(request, TemplateName,{'config':config})
    if user_config['language'] == 'Chinese':
        TemplateName = 'login.html'
    else:
        TemplateName = 'login_en.html'
    return render(request, TemplateName)

def address(request):
    user_config = getUserConfig(request)
    if request.user.is_authenticated:
        if user_config['language'] == 'Chinese':
            TemplateName = 'address.html'
        else:
            TemplateName = 'address_en.html'
        return render(request, TemplateName)
    if user_config['language'] == 'Chinese':
        TemplateName = 'login.html'
    else:
        TemplateName = 'login_en.html'
    return render(request, TemplateName)

def verifyInfo(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            country = request.POST['country']
            type = request.POST['id_type']
            firstName = request.POST['firstName']
            lastName = request.POST['lastName']
            number = request.POST['number']
            kyc = Kyc(user_id=request.user.id,country=country,id_type=type,first_name=firstName,last_name=lastName,id_number=number)
            if type == '1':
                kyc.photo1 = request.FILES['photo1']
                kyc.photo3 = request.FILES['photo3']
            elif type == '2':
                kyc.photo1 = request.FILES['photo1']
                kyc.photo2 = request.FILES['photo2']
                kyc.photo3 = request.FILES['photo3']
            kyc.save()
            return HttpResponseRedirect('/user')
        try:
            kyc = Kyc.objects.get(user_id=request.user.id)
        except:
            kyc = None
        if request.user.eth_address:
            countryList = Country.objects.all()
            user_config = getUserConfig(request)
            if user_config['language'] == 'Chinese':
                TemplateName = 'verifyInfo.html'
            else:
                TemplateName = 'verifyInfo_en.html'
            return render(request, TemplateName,{'countryList':countryList,'kyc':kyc})
        else:
            return HttpResponseRedirect('/addAddress')
    else:
        user_config = getUserConfig(request)
        if user_config['language'] == 'Chinese':
            TemplateName = 'login.html'
        else:
            TemplateName = 'login_en.html'
        return render(request, TemplateName)

def contact(request):
    if request.method == 'POST':
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        if Contact.objects.filter(email=email, status=0):
            return JsonResponse('2', safe=False)
        Contact.objects.create(first_name=firstName, last_name=lastName,email=email, subject=subject, message=message)
        return JsonResponse('1', safe=False)
    else:
        return JsonResponse('0', safe=False)

def reserve(request):
    if request.method == 'POST':
        email = request.POST['EMAIL']
        if Reserve.objects.filter(email=email):
            return JsonResponse('2', safe=False)
        Reserve.objects.create(email=email)
        return JsonResponse('1', safe=False)
    else:
        return JsonResponse('0', safe=False)

def ChangeLanguage(request):
    if request.method == 'POST':
        lang = request.POST['lang']
        user_config = getUserConfig(request)
        if lang == 'en':
            user_config['language'] = 'English'
        else:
            user_config['language'] = 'Chinese'
        # 语言改变后改变session 和 cookie
        request.session['user_config'] = user_config
        request.session.modified = True
        data = {'status': 1}
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse('0', safe=False)

#根据语言取得要跳转到的模板
def getTemplateByLanguage(request):
    user_config = getUserConfig(request)
    if user_config['language'] == 'Chinese':
        return request.session["user_config"]['thisTemplateName'] + '.html'
    else:
        return request.session["user_config"]['thisTemplateName'] + '_en.html'

def getUserConfig(request):
    user_config = ''
    # 若session存在则用session
    if(request.session.get("user_config")):
          user_config = request.session["user_config"]
    # 若session不存在则使用   系统默认语言   和   index  页面作为默认config，并存入session
    else:
        user_config = {'language': 'English', 'thisTemplateName': 'index'}
        request.session['user_config'] = user_config
        request.session.modified = True
    return user_config

def queryico(request):
    url = "http://api.etherscan.io/api"
    params = "module=account&action=txlist&address=0x1bD35E1f87D9F3870Ff8b3afED0eb1b629033588&startblock=0&endblock=99999999&sort=asc&apikey=EGTSEJ228H579APFKR98ZBPS2CFSNTMBIW"
    if unlockAccount() == False:
        return JsonResponse("unlockAccount False", safe=False)
    response = requests.get(url,params).json()
    for item in response['result']:
        if item['isError'] == "1":
            continue
        try:
            user = User.objects.get(eth_address=item['from'])
        except:
            wei = int(item['value'])
            ethNum = wei / 1000 / 1000 / 1000 / 1000 / 1000 / 1000
            config = Config.objects.get(id=1)
            if config.private_is_over:
                dcbCount = ethNum * config.public_price
            else:
                dcbCount = ethNum * config.private_price
            try:
                token = myToken(user_id=1, eth_num=ethNum, dcb_num=dcbCount, hash=item['hash'], status=1)
                token.save()
                if config.private_is_over:
                    config.public_received_token += dcbCount
                else:
                    config.private_received_token += dcbCount
                config.save()
                sendCount = int(dcbCount * 10000)
                sendCount = "{:064x}".format(sendCount)
                toAddr = item['from'][2:]
                response = sendToken(toAddr, sendCount)
            except:
                continue
            continue
        wei = int(item['value'])
        ethNum = wei / 1000 / 1000 / 1000 / 1000 / 1000 / 1000
        config = Config.objects.get(id=1)
        if config.private_is_over:
            dcbCount = ethNum * config.public_price
        else:
            dcbCount = ethNum * config.private_price
        try:
            token = myToken(user_id=user.id,eth_num=ethNum,dcb_num=dcbCount,hash=item['hash'],status=1)
            token.save()
            if config.private_is_over:
                config.public_received_token += dcbCount
            else:
                config.private_received_token += dcbCount
            config.save()
            sendCount = int(dcbCount * 10000)
            sendCount = "{:064x}".format(sendCount)
            toAddr = item['from'][2:]
            response = sendToken(toAddr, sendCount)
        except:
            continue
        # 给上级奖金
        if user.pcode:
            try:
                parent = User.objects.get(icode=user.pcode)
            except:
                continue
            dcbCount = dcbCount * 0.05
            try:
                bonus = Bonus(user_id=parent.id, email=user.username, dcb_bonus=dcbCount, hash=item['hash'],status=1)
                bonus.save()
                if config.private_is_over:
                    config.public_received_token += dcbCount
                else:
                    config.private_received_token += dcbCount
                config.save()
                sendCount = int(dcbCount * 10000)
                sendCount = "{:064x}".format(sendCount)
                toAddr = parent.eth_address[2:]
                response = sendToken(toAddr, sendCount)
            except:
                continue
    return JsonResponse("end", safe=False)

def unlockAccount():
    url = 'http://101.132.99.27:8332'
    headers = {'content-type': 'application/json'}
    unlockAccount = {
        "jsonrpc": "2.0",
        "method": "personal_unlockAccount",
        "params": ["0xc1f1D4b27623EA722b1B3C10F509aa6C9c05E81C", "okfuckyoujzb2015", 300],
        "id": 86}
    response = requests.post(
        url, data=json.dumps(unlockAccount), headers=headers).json()
    try:
        if response['result']:
            return True
    except:
        return False

def sendToken(to,num):
    url = 'http://101.132.99.27:8332'
    headers = {'content-type': 'application/json'}
    payload = {
        "method": "eth_sendTransaction",
        "params": [{
            "from": "0xc1f1D4b27623EA722b1B3C10F509aa6C9c05E81C",
            "to": "0xf1Db55245c0d293c96C3E8061b202063BBa71502",
            "data": "0xa9059cbb000000000000000000000000"+to+num}],
        "jsonrpc": "2.0",
        "id": 86,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()
    return response

# def sendTokenasaddress(request,to,dcbCount):
#     if unlockAccount() == False:
#         return JsonResponse("unlockAccount False", safe=False)
#     dcbCount = int(dcbCount)
#     sendCount = int(dcbCount * 10000)
#     sendCount = "{:064x}".format(sendCount)
#     toAddr = to[2:]
#     response = sendToken(toAddr, sendCount)
#     return JsonResponse(response, safe=False)

def invitation(request):
    try:
        offset = Telegram.objects.last()
    except:
        offset = 0
    if offset:
        url = "https://api.telegram.org/bot548122025:AAEFgMrQZNvmD_wA7DC9htxa5tskdqgYrLs/getUpdates?offset="+offset.updateID+"&limit=100"
    else:
        url = "https://api.telegram.org/bot548122025:AAEFgMrQZNvmD_wA7DC9htxa5tskdqgYrLs/getUpdates"
    response = requests.get(url,verify=False).json()
    for user in response['result']:
        try:
            if user['message']['new_chat_member']:
                telegram = Telegram(first_name=user['message']['from']['first_name'],name=user['message']['new_chat_member']['first_name'],dcb_num=100,hash=user['message']['new_chat_member']['id'],updateID=user['update_id'],status=0)
                telegram.save()
        except:
            continue
    try:
        telegram = Telegram(first_name="#111",name="#222", dcb_num=0,hash=response['result'][-1]['update_id'], updateID=response['result'][-1]['update_id'], status=0)
        telegram.save()
    except:
        return JsonResponse("end", safe=False)
    return JsonResponse("end",safe=False)

def telegram(request):
    user_config = getUserConfig(request)
    if request.user.is_authenticated:
        if user_config['language'] == 'Chinese':
            TemplateName = 'telegram.html'
        else:
            TemplateName = 'telegram_en.html'
        users = Telegram.objects.filter(first_name=request.user.telegram_name)
        return render(request, TemplateName,{"users":users})
    if user_config['language'] == 'Chinese':
        TemplateName = 'login.html'
    else:
        TemplateName = 'login_en.html'
    return render(request, TemplateName)

def addName(request):
    user_config = getUserConfig(request)
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST['name']
            try:
                user = User.objects.get(telegram_name=name)
                data = {'status': 2}
                return JsonResponse(data, safe=False)
            except:
                user = User.objects.get(id=request.user.id)
                user.telegram_name = name
                user.save()
                data = {'status': 1}
                return JsonResponse(data, safe=False)
        config = Config.objects.get(id=1)
        if user_config['language'] == 'Chinese':
            TemplateName = 'addName.html'
        else:
            TemplateName = 'addName_en.html'
        return render(request, TemplateName,{'config':config})
    if user_config['language'] == 'Chinese':
        TemplateName = 'login.html'
    else:
        TemplateName = 'login_en.html'
    return render(request, TemplateName)

# def eth(request):
#     url = 'http://101.132.99.27:8332'
#     headers = {'content-type': 'application/json'}
#     payload = {
#         "method": "personal_newAccount",
#         "params": ['z35580113'],
#         "jsonrpc": "2.0",
#         "id": 0,
#     }
#     response = requests.post(
#         url, data=json.dumps(payload), headers=headers).json()
#     return JsonResponse(response, safe=False)