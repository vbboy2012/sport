"""sport URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from bse import views as bse_views
from django.conf import  settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', bse_views.index, name='index'),
    url(r'^user/', bse_views.user, name='user'),
    url(r'^addAddress/', bse_views.addAddress, name='addAddress'),
    url(r'^verifyInfo/', bse_views.verifyInfo, name='verifyInfo'),
    url(r'^register/', bse_views.register, name='register'),
    url(r'^contact/', bse_views.contact, name='contact'),
    url(r'^reserve/', bse_views.reserve, name='reserve'),
    url(r'^token/', bse_views.token, name='token'),
    url(r'^send/', bse_views.send, name='send'),
    url(r'^queryico/', bse_views.queryico, name='queryico'),
    url(r'^activate/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', bse_views.activate, name='activate'),
    url(r'^login/', bse_views.login, name='login'),
    url(r'^logout/', bse_views.logout, name='logout'),
    url(r'^ChangeLanguage/', bse_views.ChangeLanguage, name='ChangeLanguage'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^bozaiadmin/', admin.site.urls),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)