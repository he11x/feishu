from django.conf.urls import url
from . import feishu
urlpatterns = [
	url('schedule',feishu.schedule),
]