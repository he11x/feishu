from django.http import HttpResponse
from django.shortcuts import render

def sample(request):
	return render(request,'sample.html')

def hx(request):
	return render(request,'hx.html')

def tjj(request):
	return render(request,'tjj.html')

def zxl(request):
	return render(request,'zxl.html')

def zjs(request):
	return render(request,'zjs.html')

def wbh(request):
	return render(request,'wbh.html')

def zxh(request):
	return render(request,'zxh.html')