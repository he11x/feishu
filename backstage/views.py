from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

def feishu(request):
	return render(request,'index.html')

def test(request):
	return render(request,'slogin.html')
