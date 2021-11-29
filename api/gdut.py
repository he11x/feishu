from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import requests
from . import util
from faker import Factory
import time
import json

def yzm(request):
	d = request.GET.get('d')
	url = 'https://jxfw.gdut.edu.cn/yzm?d=' + str(d)
	response = requests.get(url)
	cookies = response.cookies.get_dict()

	cookie = 'JSESSIONID=' + cookies['JSESSIONID']

	Response = HttpResponse(response.content, content_type="image/png")
	Response['Set-Cookie'] = cookie
	return Response

def gdut_login(request):
	cookie = request.COOKIES
	account = request.POST.get('account')
	pwd = request.POST.get('password')
	verifycode = request.POST.get('verifycode')
	headers = {
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Cookie': 'JSESSIONID=' + cookie['JSESSIONID'],
		}
	url = 'https://jxfw.gdut.edu.cn/new/login'
	data = {
	'account':account,
	'pwd':pwd,
	'verifycode':verifycode,
	}
	res = requests.post(url,data = data,headers = headers)

	return HttpResponse(res.text)

def gdut_import(request):
	code = request.POST.get('code')
	cookie = request.COOKIES
	headers = {
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Cookie': 'JSESSIONID=' + cookie['JSESSIONID'],
		}
	url = 'https://jxfw.gdut.edu.cn/xsgrkbcx!getDataList.action'
	params = {
	'xnxqdm': '202101',
	'zc': '',
	'page': '1',
	'rows': '300',
	'sort': 'kxh',
	'order': 'asc',
	}
	response = requests.post(url,headers = headers,params = params)
	data = json.loads(response.text)


	user_info = get_user_info(code)
	user_name = user_info['data']['name']
	user_access_token = user_info['data']['access_token']
	calendar_id = calendar(user_access_token,user_name)
	print('开始录入')
	create_schedule(user_access_token,calendar_id,data)
	print('录入完成')
	return util.packApiData('200','ok','导入成功',{})

def create_schedule(user_access_token,calendar_id,data):
	for i in range(len(data['rows'])):
		date = data['rows'][i]['pkrq']
		length = len(data['rows'][i]['jcdm'])
		address = data['rows'][i]['jxcdmc']
		kcmc = data['rows'][i]['kcmc']
		# 课程名称
		sknrjj = data['rows'][i]['sknrjj']
		n = 0
		while (n != length):
			jc = int(data['rows'][i]['jcdm'][n:n+2])
			if n == 0:
				begin_time_stamp = time_stamp(date,start_time(str(jc)))
			n += 2
			# 每隔2步取
			# +=位置不能动
			if n == length:
				end_time_stamp = time_stamp(date,end_time(str(jc)))
		schedule(user_access_token,calendar_id,kcmc,sknrjj,begin_time_stamp,end_time_stamp,address)

def schedule(user_access_token,calendar_id,kcmc,sknrjj,begin_time_stamp,end_time_stamp,address):
	url = 'https://open.feishu.cn/open-apis/calendar/v4/calendars/{}/events'.format(calendar_id)
	headers = {
		'Authorization':'Bearer ' + user_access_token,
		'Content-Type':'application/json',
	}

	data = {
	'summary':kcmc,
	# 课程名称
	'description': sknrjj,
	# 描述
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
	begin_timetable = {'1':'8:30:00','2':'9:20:00','3':'10:25:00','4':'11:15:00','5':'13:50:00','6':'14:40:00','7':'15:30:00','8':'16:30:00','9':'17:10:00','10':'18:30:00','11':'19:20:00','12':'20:10:00'}
	return begin_timetable[begin_jc]

def end_time(end_jc):
	end_timetable = {'1':'9:15:00','2':'10:05:00','3':'11:10:00','4':'12:00:00','5':'14:35:00','6':'15:25:00','7':'16:15:00','8':'17:15:00','9':'18:05:00','10':'19:15:00','11':'20:05:00','12':'20:55:00'}
	return end_timetable[end_jc]

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