import json
import datetime
import time
from django.http import HttpResponse

class CJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, date):
			return obj.strftime('%Y-%m-%d')
		elif isinstance(obj, decimal.Decimal):
			return float(obj)
		else:
			return json.JSONEncoder.default(self, obj)

def packApiData(code=0, message="Lack Parameter", tips="参数缺失", data={}):
	""" packApiData 规范化组装接口回调数据
	@param  integer  code	 状态码
	@param  string   message  英文提示内容
	@param  string   tips	 中文提示语
	@param  dict	 data	 回调数据
	@return HttpResponse
	@author Oyster Cheung <oyster@easypus.com>
	@since   2021-01-22
	@version 2021-02-19
	"""

	return HttpResponse(json.dumps(
		{
			'code': code,
			'message': message,
			'tips': tips,
			'requestTime': int(time.time()),
			'data': data
		},
		cls=CJsonEncoder),content_type="application/json")
	