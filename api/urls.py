from django.conf.urls import url
from . import views
from . import scut
from . import gdut
urlpatterns = [
	url('redirect', views.redirect),
	url('test',views.test),
	url('scut/login',scut.scut_login),
	url('scut/import', scut.scut_import),
	url('gdut/login',gdut.gdut_login),
	url('gdut/import',gdut.gdut_import),
	url('gdut/yzm',gdut.yzm),
]