from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
# Create your views here.
def redirect(request):
	return HttpResponseRedirect('http://www.yuexiaotrip.cn/newb2c/home?openid=osb_U6GqqjBsoRBUSIbGQ9XBRWNs&orderCustId=6121351&userId=jianrui')

def test(request):
	return HttpResponse('400')

def index(request):
	return HttpResponse('200')