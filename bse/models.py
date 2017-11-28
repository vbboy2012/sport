# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
# python3 manage.py makemigrations
# python3 manage.py migrate

class User(AbstractUser):
    checkEmail = models.BooleanField('邮箱验证', default=False)
    pcode = models.CharField(max_length=10)
    icode = models.CharField(max_length=10)
    is_kyc = models.IntegerField('key验证',default=0)
    eth_address = models.CharField(max_length=50)
    eth_count = models.DecimalField(max_digits=20, decimal_places=8,default=0)  # ICO金额

    def __str__(self):
        return self.username

class Kyc(models.Model):
    country = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    id_type = models.IntegerField('ID类型')
    id_number = models.CharField(max_length=30)
    photo1 = models.CharField(max_length=50)
    photo2 = models.CharField(max_length=50)
    photo3 = models.CharField(max_length=50)

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.CharField(max_length=50)
