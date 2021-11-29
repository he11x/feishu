from django.conf.urls import url
from . import mypass
from . import feishu
urlpatterns = [
	url('mypass/sample', mypass.sample),
	url('mypass/hx', mypass.hx),
	url('mypass/tjj', mypass.tjj),
	url('mypass/zjs',mypass.zjs),
	url('mypass/zxl',mypass.zxl),
	url('mypass/wbh',mypass.wbh),
	url('mypass/zxh',mypass.zxh),
	url('schedule',feishu.schedule),
]