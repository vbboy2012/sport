# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import User,Kyc,Contact,Country,Reserve,Bonus,Config,Token

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','eth_address', 'pcode', 'icode','date_joined','last_login','checkEmail','is_kyc')
    search_fields = ('username','eth_address')

class KycAdmin(admin.ModelAdmin):
    list_display = ('user','country','first_name','last_name','id_type','id_number','image_data1','image_data2','image_data3')
    readonly_fields = ('image_data1','image_data2','image_data3',)  # 必须加这行 否则访问编辑页面会报错

    def image_data1(self, obj):
        if obj.photo1:
            return mark_safe(u'<img src="%s" width="100px" />' % obj.photo1.url)
        else:
            return u'没有图片'
    def image_data2(self, obj):
        if obj.photo2:
            return mark_safe(u'<img src="%s" width="100px" />' % obj.photo2.url)
        else:
            return u'没有图片'
    def image_data3(self, obj):
        if obj.photo3:
            return mark_safe(u'<img src="%s" width="100px" />' % obj.photo3.url)
        else:
            return u'没有图片'

    # 页面显示的字段名称
    image_data1.allow_tags = True
    image_data1.short_description = u'正面照片'
    image_data2.allow_tags = True
    image_data2.short_description = u'反面照片'
    image_data3.allow_tags = True
    image_data3.short_description = u'自拍照片'

class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','email','subject','status')

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name','en_name')

class ReserveAdmin(admin.ModelAdmin):
    list_display = ('email','status')

class BonusAdmin(admin.ModelAdmin):
    list_display = ('user','email','dcb_bonus','status')

class TokenAdmin(admin.ModelAdmin):
    list_display = ('user','eth_num','dcb_num','status')


admin.site.register(User,UserAdmin)
admin.site.register(Kyc,KycAdmin)
admin.site.register(Contact,ContactAdmin)
admin.site.register(Country,CountryAdmin)
admin.site.register(Reserve,ReserveAdmin)
admin.site.register(Bonus,BonusAdmin)
admin.site.register(Token,TokenAdmin)
admin.site.register(Config)