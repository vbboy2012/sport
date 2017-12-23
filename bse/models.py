# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# python3 manage.py makemigrations
# python3 manage.py migrate

class User(AbstractUser):
    checkEmail = models.BooleanField('邮箱验证', default=False)
    pcode = models.CharField(max_length=10,blank=True)
    icode = models.CharField(max_length=10)
    eth_address = models.CharField(max_length=50)
    dcb_count = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    is_kyc = models.BooleanField('kyc验证', default=False)

class Kyc(models.Model):
    user = models.ForeignKey(User)
    country = models.IntegerField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    id_type = models.IntegerField('ID类型')
    id_number = models.CharField(max_length=30)
    photo1 = models.ImageField(upload_to='img', blank=True)
    photo2 = models.ImageField(upload_to='img', blank=True)
    photo3 = models.ImageField(upload_to='img', blank=True)

class Contact(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.CharField(max_length=50)
    status = models.BooleanField('是否处理', default=False)

class Country(models.Model):
    name = models.CharField(max_length=20)
    en_name = models.CharField(max_length=20)
    code = models.CharField(max_length=5)
    code2 = models.CharField(max_length=5)
    code3 = models.CharField(max_length=5)

class Reserve(models.Model):
    email = models.CharField(max_length=50)
    status = models.BooleanField('是否众筹了', default=False)

class Bonus(models.Model):
    user = models.ForeignKey(User)
    email = models.CharField(max_length=50)
    dcb_bonus = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    hash = models.CharField(max_length=100, unique=True)
    status = models.BooleanField('是否发送', default=False)

class Token(models.Model):
    user = models.ForeignKey(User)
    eth_num = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    dcb_num = models.IntegerField(default=0)
    hash = models.CharField(max_length=100,unique=True)
    status = models.BooleanField('是否发送', default=False)

class Config(models.Model):
    private_price = models.IntegerField(default=0)
    public_price = models.IntegerField(default=0)
    private_token_count = models.IntegerField(default=0)
    public_token_count = models.IntegerField(default=0)
    private_received_token = models.IntegerField(default=0)
    public_received_token = models.IntegerField(default=0)
    eth_price = models.IntegerField(default=0)
    public_date_start = models.DateTimeField(default=0)
    public_date_end = models.DateTimeField(default=0)
    private_is_over = models.BooleanField('私募是否结束',default=False)
    public_is_over = models.BooleanField('公开是否结束',default=False)

    def __str__(self):
        return '系统配置'
