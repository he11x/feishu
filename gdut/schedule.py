from django.shortcuts import render


def shedule(requests):
	# url = 'https://open.feishu.cn/open-apis/authen/v1/index?redirect_uri=https%3A%2F%2Fbackstage.easypus.com%2Findex&app_id=cli_a1a2172e0038d00d&state=test'
	url = 'https://open.feishu.cn/open-apis/authen/v1/index?redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Findex&app_id=cli_a1a2172e0038d00d&state=test'
	# 刷新之后不用重新发起请求
	# n是防止多次调用API而使token过期
	code = request.GET.get('code')
	if code == None:
		# 获取个人信息，封装成函数反而不好用
		return HttpResponseRedirect(url)
		# 本地测试
