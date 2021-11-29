from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import requests
from faker import Factory
from lxml import etree
import os
import json
from . import util
import re
import time
import datetime
import requests
from faker import Factory
from lxml import etree
import re
import execjs

# scut 的API
# 完成登录验证直接拿到classlist
# code和classlist发到api

# 
def scut_login(request):
	password = request.POST.get('password')
	username = request.POST.get('username')

	if len(password) == 0 or len(username) == 0:
		return util.packApiData(412,'lack of params','请填入账号密码',{})
	class_list = scut_class(username,password)
	if class_list == 0:
		return util.packApiData(403,'default','登录失败',{})
	else:
		return util.packApiData(200,'ok','登录成功',class_list)
	return render(request,'schedule.html')

def scut_import(request):
	code = request.POST.get('code')
	class_list = json.loads(request.POST.get('data'))
	# print(class_list)
	try:
		user_info = get_user_info(code)
		user_name = user_info['data']['name']
		user_access_token = user_info['data']['access_token']
		print(user_access_token)
	except:
		return util.packApiData(403,'code invalid','过期',{})
	calendar_id = calendar(user_access_token,user_name)
	# calendar_id = user_calendar(user_access_token)
	create_schedule(user_access_token,calendar_id,class_list)
	return util.packApiData(200,'ok','导入完成',{})



def scut_class(username,password):
	vpnUrl = 'https://sso-443.webvpn.scut.edu.cn/cas/login?service=https%3A%2F%2Fwebvpn.scut.edu.cn%2Fusers%2Fauth%2Fcas%2Fcallback%3Furl%3Dhttp%253A%252F%252Fwww.scut.edu.cn%252F'
	# loginUrl = 'https://sso.scut.edu.cn/cas/login?service=http%3A%2F%2Fjw2018.jw.scut.edu.cn%2Fsso%2Fdriotlogin'
	loginUrl = 'https://sso-443.webvpn.scut.edu.cn/cas/login?service=https%3A%2F%2Fxsjw2018-jw.webvpn.scut.edu.cn%2Fsso%2Fdriotlogin'

	# loginUrl = 'https://sso.scut.edu.cn/cas/login'
	headers = {"User-Agent": Factory.create().user_agent()}  #获取一个随机的UA

	with open("js/des.js", "r") as file:
		desJsCode = file.read()

	desJsFunction = execjs.compile(desJsCode)
	su = username
	pd = password
	ul = len(su)
	pl = len(pd)
	_eventId = "submit"

	session = requests.session()
	loginPage = session.get(vpnUrl, headers = headers)  #先用get获取到lt和execution
	loginPageHTML = etree.HTML(loginPage.text)
	# print(loginPage.text)
	lt = loginPageHTML.xpath(r'//*[@id="lt"]/@value')[0]  #返回的结果是一个列表，取第一个对象))
	execution = loginPageHTML.xpath(r'//*[@name="execution"]/@value')[0]


	data = {"rsa":desJsFunction.call("strEnc", su + pd + lt, "1", "2", "3"),
		"ul": ul,
		"pl": pl,
		"lt": lt,
		"execution": execution,
		"_eventId": _eventId
	}
	# 构造data
	response = session.post(vpnUrl, headers = headers, data = data)
	cookies = session.cookies
	cookies = cookies.get_dict()



	loginPage = session.get(loginUrl, headers = headers,cookies = cookies)  #先用get获取到lt和execution

	cookies = session.cookies
	cookies = cookies.get_dict()

	params = {
	   'gnmkdm':'N2151',
	   'layout':'default',
	   'su':su
}
	# url = 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151&su=202066561291'
	# 查课
	url = 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html'
	data = {
	'xnm': '2021',
	'xqm': '3',
	'xqh_id': '2',
	}
	res = session.post(url,headers = headers,cookies = cookies,params = params,data = data)
	# print(res.text)
	try:
		class_list = json.loads(res.text)
		return class_list
	except:
		return 0


def get_tenant_access_token():
	url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
	data = {
	'app_id':'cli_a1a2172e0038d00d',
	'app_secret':'IVIqpxJvLhHUM76sTSuo0bVWBcTfsX8r'
	}
	res = requests.post(url,data = data)
	res = json.loads(res.text)
	tenant_access_token = res['tenant_access_token']
	return tenant_access_token

def get_user_info(code):
	# 获取用户信息和user_access_token
	app_access_token = get_tenant_access_token()
	url = 'https://open.feishu.cn/open-apis/authen/v1/access_token'
	headers = {
		'Authorization':'Bearer ' + app_access_token,
		'Content-Type':'application/json',
		}
	data = {
		"grant_type":"authorization_code",
		"code":code,
		}
	data = json.dumps(data)
	res = requests.post(url,headers = headers,data = data)
	user_info = json.loads(res.text)
	return user_info


def create_schedule(user_access_token,calendar_id,data):
	current_week = int(time.strftime("%W")) - 34
	for i in range(current_week,20):
		# 周数开始遍历
		current_week_date = datetime.date(2021,8,30) + datetime.timedelta(i - 1) * 7
		print(i)
		# 本周周一的具体日期
		for k in data['kbList']:
			date = current_week_date + datetime.timedelta(days=(int(k['xqj']) - 1))
			# 那一周周几对应的日期,生成timestamp要用
			address = k['cdmc']
			zcd = k['zcd']
			kcmc = k['kcmc']
			course = k['jcs'].split('-')
			# 节次数
			class_week = re.sub('[\u4e00-\u9fa5^()]', '', zcd)
			class_week_list = class_week.split(',')
			for this_week in class_week_list:
				class_week = this_week.split('-')
				if len(class_week) == 1:
					if int(class_week[0]) == current_week:
						begin_time_stamp = time_stamp(date,start_time(course[0]))
						end_time_stamp = time_stamp(date,end_time(course[1]))
						schedule(user_access_token,calendar_id,kcmc,zcd,begin_time_stamp,end_time_stamp,address)
				elif int(current_week) >= int(class_week[0]) and int(current_week) <= int(class_week[1]):
					if '单' in zcd or '双' in zcd:
						if '单' in zcd: 
							if int(current_week)%2 == 1:
								begin_time_stamp = time_stamp(date,start_time(course[0]))
								end_time_stamp = time_stamp(date,end_time(course[1]))
								schedule(user_access_token,calendar_id,kcmc,zcd,begin_time_stamp,end_time_stamp,address)
							# print(zcd)
						if '双' in zcd:
							if int(current_week)%2 == 0:
								begin_time_stamp = time_stamp(date,start_time(course[0]))
								end_time_stamp = time_stamp(date,end_time(course[1]))
								schedule(user_access_token,calendar_id,kcmc,zcd,begin_time_stamp,end_time_stamp,address)
					# print(zcd)
					else:
						begin_time_stamp = time_stamp(date,start_time(course[0]))
						end_time_stamp = time_stamp(date,end_time(course[1]))
						schedule(user_access_token,calendar_id,kcmc,zcd,begin_time_stamp,end_time_stamp,address)
		current_week += 1

def calendar(user_access_token,user_name):
	# 先创建日历
	url = 'https://open.feishu.cn/open-apis/calendar/v4/calendars'
	headers = {
		'Authorization':'Bearer ' + user_access_token,
		'Content-Type':'application/json',
	}
	data = {
	'summary':'课表-' + user_name ,
	'permissions':'public',
	}
	data = json.dumps(data)
	response = requests.post(url,headers = headers,data=data)
	res = json.loads(response.text)
	# print(res)
	calendar_id = res['data']['calendar']['calendar_id']
	return calendar_id

def user_calendar(user_access_token):
	url = 'https://open.feishu.cn/open-apis/calendar/v4/calendars'
	headers = {
		'Authorization':'Bearer ' + user_access_token,
		'Content-Type':'application/json',
		}
	res = requests.post(url,headers = headers)
	calendars = json.loads(res.text)
	return calendars['data']['calendar']['calendar_id']


def schedule(user_access_token,calendar_id,kcmc,zcd,begin_time_stamp,end_time_stamp,address):
	url = 'https://open.feishu.cn/open-apis/calendar/v4/calendars/{}/events'.format(calendar_id)
	headers = {
		'Authorization':'Bearer ' + user_access_token,
		'Content-Type':'application/json',
	}

	data = {
	'summary':kcmc,
	# 课程名称
	'description': zcd,
	# 周数
	'start_time':{'timestamp':begin_time_stamp},
	'end_time':{'timestamp':end_time_stamp},
	'visibility':'public',
	'attendee_ability':'can_modify_event',
	'location':{'name':address},
	'reminders':[{"minutes":15}],
	'color':'161600'
	}
	data = json.dumps(data)
	response = requests.post(url,headers = headers,data=data)

def time_stamp(date,hour):
	now = '{} {}'.format(date,hour)
	st = time.strptime(now,'%Y-%m-%d %H:%M:%S')
	time_stamp = time.mktime(st)
	return str(int(time_stamp))

def get_current_week():
	monday = datetime.date.today()
	one_day = datetime.timedelta(days=1)
	while monday.weekday() != 0:
		monday -= one_day
	return monday

def start_time(begin_jc):
	# 节次
	begin_timetable = {'1':'8:50:00','2':'9:40:00','3':'10:40:00','4':'11:30:00','5':'14:00:00','6':'14:50:00','7':'15:45:00','8':'16:35:00','9':'19:00:00','10':'19:55','11':'20:50:00','12':'21:45:00'}
	return begin_timetable[begin_jc]

def end_time(end_jc):
	end_timetable = {'1':'9:35:00','2':'10:25:00','3':'11:25:00','4':'12:15:00','5':'14:45:00','6':'15:35:00','7':'16:30:00','8':'17:20:00','9':'19:45:00','10':'20:40:00','11':'21:35:00','12':'22:30:00'}
	return end_timetable[end_jc]


