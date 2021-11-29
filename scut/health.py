import time
from django.shortcuts import render
from django.http import HttpResponse
import requests
from faker import Factory
from lxml import etree
import execjs
from django.contrib import messages
import json
from multiprocessing import Process
import pymysql

def get_cookies(username,password):
	loginUrl = 'https://sso.scut.edu.cn/cas/login?service=https%3A%2F%2Fenroll.scut.edu.cn%2Fdoor%2Fhealth%2Fh5%2Fhealth.html'
	headers = {"User-Agent": Factory.create().user_agent()} 

	with open("des.js", "r") as file:
		desJsCode = file.read()

	desJsFunction = execjs.compile(desJsCode)
	su = username
	pd = password
	session = requests.session()
	loginPage = session.get(loginUrl, headers = headers) 
	loginPageHTML = etree.HTML(loginPage.text)
	lt = loginPageHTML.xpath(r'//*[@id="lt"]/@value')[0]  
	execution = loginPageHTML.xpath(r'//*[@name="execution"]/@value')[0]
	ul = len(su)
	pl = len(pd)
	_eventId = "submit"

	data = {"rsa":desJsFunction.call("strEnc", su + pd + lt, "1", "2", "3"),
		"ul": ul,
		"pl": pl,
		"lt": lt,
		"execution": execution,
		"_eventId": _eventId
	}
	response = session.post(loginUrl, headers = headers, data = data)
	cookies = session.cookies
	cookies = cookies.get_dict()
	return cookies

def fill_health(username,password):
	session = requests.session()
	fill_url = 'https://enroll.scut.edu.cn/door/health/h5/add'
	cookies = get_cookies(username,password)
	get_url = 'https://enroll.scut.edu.cn/door/health/h5/get'
	res = session.get(get_url,cookies = cookies)
	data = json.loads(res.text)['data']['healthRptInfor']
	data['iRptState'] = '0'
	res = session.post(fill_url,cookies=cookies,data = data)

def auto_health(request):
	password = request.POST.get('password')
	username = request.POST.get('username')
	if password and username:
		# try:
		if 1:
			fill_health(username,password)
			inset_data(username,password)
			return HttpResponse('填报成功')

		# except:
		else:
			return HttpResponse('账号或密码错误')
	return render(request,'health.html')

def inset_data(username,password):
	connection = pymysql.connect(host = '159.75.47.53',port = 3306,user = "root",passwd = "124536")
	cursor = connection.cursor()
	sql = 'insert into backstage.user (username,password) select %s,%s from dual where not exists (select * from backstage.user  where username=%s)'
	cursor.execute(sql,[username,password,username])
	connection.commit()
